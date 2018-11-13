from enum import Enum, IntEnum
from observer import Publisher, Event
import subprocess
import threading


class PlayMode(IntEnum):
    NORMAL = 1,
    REVERSE = 2,


class PlayerCommand(Enum):
    NEXT = 1,
    PREVIOUS = 2,
    PAUSE = 3,
    STOP = 4


class Player(Publisher):

    def __init__(self):
        Publisher.__init__(self)
        self.cur_music = None
        self.playList = []
        self._cur_index = 0
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
        self.playList.append(music)

    def deleteMusic(self, index):
        '''删除播放列表中的歌曲'''
        if self.playList and len(self.playList) > index:
            self.playList.remove(self.playList[index])
            if self.cur_music:
                #调整当前播放歌曲的位置
                self._cur_index = self.playList.index(self.cur_music)

    def clearPlayList(self):
        '''清除播放列表'''
        if len(self.playList) > 0:
            self.playList.clear()

    def executeCommand(self, command):
        '''执行播放指令'''
        if command == PlayerCommand.NEXT:
            self._next()
        elif command == PlayerCommand.PREVIOUS:
            self._previous()
        elif command == PlayerCommand.PAUSE:
            self._pause()
        elif command == PlayerCommand.STOP:
            self._stop()

    def changePlayMode(self):
        '''更换播放模式'''
        value = self.play_mode.value
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
            self._mpg123Process.stdin.write('Q\n'.encode('utf-8'))
            self._mpg123Process.stdin.flush()
            self._mpg123Process.terminate()
            self._mpg123Process = None
        self._cur_index = 0
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
                    self._mpg123Process.stdin.write('Q\n'.encode('utf-8'))
                    self._mpg123Process.stdin.flush()
                    break
                elif stdout == '@P 0':
                    #播放结束
                    if len(self.playList) > 0:
                        self._playNext()
                        self.notify('MusicCompletation', '')
                        continue
                    if len(self.playList) == 0:
                        self._stop()
                        break
            except:
                self._stop()
                break