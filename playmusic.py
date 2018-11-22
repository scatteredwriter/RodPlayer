from enum import Enum, IntEnum
from observer import Publisher, Event, eventName
import subprocess
import threading


class PlayMode(IntEnum):
    NORMAL = 1
    REVERSE = 2


class PlayerCommand(Enum):
    NEXT = 1
    PREVIOUS = 2
    PAUSE = 3
    STOP = 4
    QUIT = 5


class Player(Publisher):

    def __init__(self):
        Publisher.__init__(self)
        self.cur_music = None
        self.playList = []
        self._cur_index = -1
        self._retryCount = 0
        self._lock = threading.RLock()
        self._player_theard = None
        self.play_mode = PlayMode.NORMAL
        self._mpg123Process = subprocess.Popen(['mpg123', '-R'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._player_theard = threading.Thread(target=self._player)
        self._player_theard.start()

    def addMusic(self, music):
        '''添加歌曲至播放列表'''
        if self.playList.count(music) > 0:
            self.playList.remove(music)
        _music_singername = music.singerName
        _music_songname = music.songName
        self.playList.append(music)
        self.notify(
            eventName.MusicAdded, (_music_singername, _music_songname))

    def deleteMusic(self, indexs):
        '''删除播放列表中的歌曲'''
        if not indexs or len(indexs) <= 0:
            return
        musics = []
        for index in indexs:
            if self.playList and len(self.playList) > index:
                musics.append(self.playList[index])
        if not musics or len(musics) <= 0:
            return
        for music in musics:
            _music_singername = music.singerName
            _music_songname = music.songName
            self.playList.remove(music)
            self.notify(
                eventName.MusicDeleted, (_music_singername, _music_songname))
        if self.cur_music:
            #调整当前播放歌曲的位置
            self._cur_index = self.playList.index(self.cur_music)

    def clearPlayList(self):
        '''清除播放列表'''
        if len(self.playList) > 0:
            self.playList.clear()
            self._stop()

    def executeCommand(self, command):
        '''执行播放指令'''
        if command == PlayerCommand.NEXT:
            self._playNext()
        elif command == PlayerCommand.PREVIOUS:
            self._playPrevious()
        elif command == PlayerCommand.PAUSE:
            self._pause()
        elif command == PlayerCommand.STOP:
            self._stop()
        elif command == PlayerCommand.QUIT:
            self._quit()

    def changePlayMode(self):
        '''更换播放模式'''
        value = self.play_mode
        if value == PlayMode.REVERSE:
            self.play_mode = PlayMode.NORMAL
            return
        self.play_mode = self.play_mode + 1

    def playMusic(self, index):
        '''播放列表中的指定歌曲'''
        if index < 0 or index >= len(self.playList):
            return
        self._setCurrentIndex(index)

    def _pause(self):
        '''暂停或继续播放'''
        if self._mpg123Process and self.cur_music:
            self._mpg123Process.stdin.write('P\n'.encode('utf-8'))
            self._mpg123Process.stdin.flush()

    def _stop(self):
        '''停止播放'''
        if self._mpg123Process:
            self._mpg123Process.stdin.write('S\n'.encode('utf-8'))
            self._mpg123Process.stdin.flush()
        self._cur_index = -1
        self.cur_music = None

    def _quit(self):
        '''停止播放'''
        if self._mpg123Process:
            self._mpg123Process.stdin.write('Q\n'.encode('utf-8'))
            self._mpg123Process.stdin.flush()
            self._mpg123Process.terminate()
            self._mpg123Process = None
        self._cur_index = -1
        self.cur_music = None

    def _next(self):
        '''播放下一首'''
        if len(self.playList) < 1:
            self._stop()
            return False
        if self._mpg123Process:
            #只有一首歌曲
            if len(self.playList) == 1 and self._cur_index == 0:
                #重新播放之前的歌曲
                self._setCurrentIndex(self._cur_index)
            else:
                if self._cur_index == len(self.playList) - 1:
                    #播放第一首歌曲
                    self._setCurrentIndex(0)
                else:
                    #播放下一首歌曲
                    self._setCurrentIndex(self._cur_index + 1)
            return True
        return False

    def _previous(self):
        '''播放上一首'''
        if len(self.playList) < 1:
            self._stop()
            return False
        if self._mpg123Process:
            #只有一首歌曲
            if len(self.playList) == 1 and self._cur_index == 0:
                #重新播放之前的歌曲
                self._setCurrentIndex(self._cur_index)
            else:
                if self._cur_index == 0:
                    #播放最后一首歌曲
                    self._setCurrentIndex(len(self.playList) - 1)
                else:
                    #播放上一首歌曲
                    self._setCurrentIndex(self._cur_index - 1)
            return True
        return False

    def _playNext(self):
        '''播放当前歌曲结束后的下一首'''
        if self.play_mode == PlayMode.NORMAL:
            return self._next()
        elif self.play_mode == PlayMode.REVERSE:
            return self._previous()

    def _playPrevious(self):
        '''播放当前歌曲结束后的下一首'''
        if self.play_mode == PlayMode.NORMAL:
            return self._previous()
        elif self.play_mode == PlayMode.REVERSE:
            return self._next()

    def _setCurrentIndex(self, index):
        '''指定当前播放的歌曲并且播放该歌曲'''
        self._lock.acquire()
        if len(self.playList) > index:
            self._cur_index = index
            self.cur_music = self.playList[self._cur_index]
            if self._mpg123Process:
                music_url = self.cur_music.musicInfo.music_url
                self._mpg123Process.stdin.write(
                    ('L {}\n').format(music_url).encode('utf-8'))
                self._mpg123Process.stdin.flush()
        self._lock.release()

    def _player(self):
        '''监听mpg123运行情况的线程'''
        if self._mpg123Process is None:
            return
        while True:
            try:
                stdout = self._mpg123Process.stdout.readline(
                    ).decode('utf-8').strip()
                if stdout[:2] == '@F':
                    #正在播放
                    continue
                elif stdout[:2] == '@E':
                    #错误
                    # if self._retryCount >= 0 and self._retryCount < 3:
                    #     self.notify(eventName.PlayError, (
                    #         self.cur_music.singerName, self.cur_music.songName, self._retryCount + 1))
                    #     self.playMusic(self._cur_index)
                    #     self._retryCount += 1
                    # else:
                    #     self._playNext()
                    #     self._retryCount = 0
                    self.notify(eventName.PlayError, (
                        self.cur_music.singerName, self.cur_music.songName))
                    self.deleteMusic(self._cur_index)
                    self._playNext()
                    continue
                elif stdout == '@P 0':
                    #播放结束
                    if len(self.playList) > 0:
                        #播放下一首
                        self._playNext()
                        self.notify(eventName.MusicCompletation, '')
                        continue
                    if len(self.playList) == 0:
                        self._stop()
                        break
            except:
                self._stop()
                break