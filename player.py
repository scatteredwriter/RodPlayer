from music import Music, MusicInfo, getMusicList
from observer import Listener, Event
import download
import playmusic
import re


class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Main(Listener):
    def __init__(self):
        self.player = playmusic.Player()
        self.addObserver(self.player, 'MusicCompletation')

    def onNotify(self, event):
        if not isinstance(event, Event):
            return
        if event.eventName == 'MusicCompletation':
            self._printPlayerStatus()

    def _addAll(self, begin, musics):
        if self.player is None:
            self.player = playmusic.Player()
        for i in range(begin, len(musics)):
            for j in range(3):
                try:
                    music = musics[i]
                    music.musicInfo = music.getMusicInfo(0)
                    break
                except:
                    print('{}第{}次添加 {} - {} 失败! 正在重试...{}'.format(
                        Color.FAIL, str(j+1), music.singerName, music.songName, Color.ENDC))
                    continue
            self.player.addMusic(music)
            print('{}已添加{} {} - {} 至播放列表'.format(Color.OKBLUE, Color.ENDC, Color.OKGREEN + music.singerName, music.songName + Color.ENDC))
        print('{}添加完成!{}'.format(Color.OKBLUE, Color.ENDC))

    def _showPlayList(self):
        if self.player and len(self.player.playList) > 0:
            print('{}播放列表:{}'.format(Color.OKBLUE, Color.ENDC))
            for i in range(len(self.player.playList)):
                print(
                    '[{}].{}歌曲{}:{}\t{}歌手{}:{}\t{}专辑{}:{}'.format(Color.OKGREEN + str(i) + Color.ENDC,
                                                                  Color.OKGREEN, Color.ENDC,
                                                                  Color.BOLD + self.player.playList[i].songName + Color.ENDC,
                                                                  Color.OKGREEN, Color.ENDC,
                                                                  Color.BOLD + self.player.playList[i].singerName + Color.ENDC,
                                                                  Color.OKGREEN, Color.ENDC,
                                                                  Color.BOLD+self.player.playList[i].albumName + Color.ENDC))
        else:
            print('{}播放列表为空{}'.format(Color.FAIL, Color.ENDC))

    def _clearPlayList(self):
        if self.player:
            self.player.clearPlayList()

    def _printPlayerStatus(self):
        if self.player and self.player.cur_music:
            play_mode = ''
            if self.player.play_mode == playmusic.PlayMode.NORMAL:
                play_mode = '顺序播放'
            elif self.player.play_mode == playmusic.PlayMode.REVERSE:
                play_mode = '逆序播放'
            print('正在播放:{} - {}\t播放模式:{}'.format(Color.OKGREEN + self.player.cur_music.singerName, self.player.cur_music.songName + Color.ENDC, Color.OKBLUE + play_mode + Color.ENDC))
        # command = input('请输入命令(%sh/H%s查看帮助):' % (Color.WARNING, Color.ENDC))

    def _printHelp(self):
        print('{}\
所有页面:\n\
q/Q:取消\n\
\n主页面:\n\
s/S:搜索\n\
l/L:查看播放列表\n\
p/P:暂停/播放\n\
p [编号]/P [编号]:播放列表中对应序号的歌曲\n\
n/N:下一首\n\
b/B:上一首\n\
m/M:更换播放模式\n\
d [编号]/D [编号]:删除播放列表中对应序号的歌曲,多个编号可用空格分隔\n\
c/C:清除播放列表\n\
h/H:查看帮助\n\
\n歌曲搜索:\n\
q/Q:重新搜索\n\
回车:下一页\n\
a/A:添加当页所有歌曲至播放列表\n\
\n歌曲详情:\n\
a/A:添加当前歌曲至播放列表\n\
{}'.format(Color.OKBLUE, Color.ENDC))

    def mainFun(self):
        while(True):
            musics = []
            begin = 0
            p = 0
            self._printPlayerStatus()
            command = input('')
            if command == 'q' or command == 'Q':
                #退出
                if self.player:
                    self.player.executeCommand(playmusic.PlayerCommand.STOP)
                exit()
            elif command[0:1] == 'p' or command == 'P':
                if self.player:
                    if len(command) == 1:
                        #暂停/播放
                            self.player.executeCommand(
                                playmusic.PlayerCommand.PAUSE)
                    else:
                        #播放列表中对应序号的歌曲
                        try:
                            pattern = re.compile(r'[p|P]\s(\d+)')
                            result = re.search(pattern, command).groups()
                            if len(result) != 1:
                                print("{}错误指令!{}".format(
                                    Color.FAIL, Color.ENDC))
                                continue
                            index = int(result[0])
                            self.player.playMusic(index)
                        except:
                            print("{}错误指令!{}".format(Color.FAIL, Color.ENDC))
                continue
            elif command == 'n' or command == 'N':
                #下一首
                if self.player:
                    self.player.executeCommand(playmusic.PlayerCommand.NEXT)
                continue
            elif command == 'b' or command == 'B':
                #上一首
                if self.player:
                    self.player.executeCommand(
                        playmusic.PlayerCommand.PREVIOUS)
                continue
            elif command == 'm' or command == 'M':
                #更换播放模式
                if self.player:
                    self.player.changePlayMode()
            elif command == 'l' or command == 'L':
                #查看播放列表
                self._showPlayList()
                continue
            elif command == 'c' or command == 'C':
                #清除播放列表
                if self.player:
                    self.player.clearPlayList()
                continue
            elif command[0:1] == 'd' or command[0:1] == 'D':
                #删除播放列表中对应序号的歌曲
                try:
                    pattern = re.compile(r'\d+')
                    result = re.findall(pattern, command)
                    if len(result) <= 0:
                        print("{}错误指令!{}".format(
                            Color.FAIL, Color.ENDC))
                        continue
                    for index in result:
                        index = int(index)
                        self.player.deleteMusic(index)
                except:
                    print("{}错误指令!{}".format(Color.FAIL, Color.ENDC))
                continue
            elif command == 'h' or command == 'H':
                #查看帮助
                self._printHelp()
                continue
            elif command == 's' or command == 'S':
                #搜索
                command = input(
                    '请输入搜索关键字(%sq%s取消):' % (Color.WARNING, Color.ENDC))
                if command == 'q' or command == 'Q':
                    continue
                #执行搜索
                while(True):
                    try:
                        p += 1
                        newMusics = getMusicList(command, p)
                        if len(musics) == 0 and len(newMusics) == 0:
                            break
                        elif len(newMusics) == 0:
                            print('%s已到最后一页!%s' % (Color.FAIL, Color.ENDC))
                        else:
                            musics.extend(newMusics)
                            for i in range(begin, len(musics)):
                                realI = i
                                print(
                                    '[%s].%s:%s\t%s:%s\t%s:%s' % (Color.OKGREEN + str(realI) + Color.ENDC,
                                                                  Color.OKGREEN +
                                                                  '歌曲' +
                                                                  Color.ENDC,
                                                                  Color.BOLD + musics[realI].songName + Color.ENDC,
                                                                  Color.OKGREEN +
                                                                  '歌手' +
                                                                  Color.ENDC,
                                                                  Color.BOLD + musics[realI].singerName + Color.ENDC,
                                                                  Color.OKGREEN +
                                                                  '专辑' +
                                                                  Color.ENDC,
                                                                  Color.BOLD + musics[realI].albumName + Color.ENDC
                                                                  ))
                    except:
                        print('{}搜索失败!{}'.format(Color.FAIL, Color.ENDC))
                        break
                    command = input('请输入要下载的歌曲%s序号%s或其他命令(%s空格%s分割序号进行多选):'%(
                        Color.WARNING, Color.ENDC, Color.WARNING, Color.ENDC))
                    if command == 'q' or command == 'Q':
                        #退出
                        break
                    elif command == 'a' or command == 'A':
                        #添加当前所有歌曲至播放列表
                        self._addAll(begin, musics)
                        break
                    elif len(command) == 0:
                        #下一页
                        begin = len(musics)
                        continue
                    selecteds = command.split(' ')
                    for selectIndex in selecteds:
                        music = musics[int(selectIndex)]
                        for j in range(3):
                            try:
                                music.musicInfo = music.getMusicInfo(0)
                                break
                            except:
                                print('{}第{}次获取 {} - {} 信息失败! 正在重试...{}'.format(
                                    Color.FAIL, str(j+1), music.singerName, music.songName, Color.ENDC))
                                continue
                        print('歌曲:%s - %s\n歌曲链接:%s\n专辑图片:%s' % (Color.OKBLUE + music.singerName, music.songName + Color.ENDC, Color.OKBLUE + music.musicInfo.music_url + Color.ENDC, Color.OKBLUE + music.musicInfo.albumImg_url + Color.ENDC))
                        command = input('输入任意键下载或其他命令:')
                        if command == 'q' or command == 'Q':
                            continue
                        elif command == 'a' or command == 'A':
                            if self.player is None:
                                self.player = playmusic.Player()
                            self.player.addMusic(music)
                            continue
                        print('开始下载 %s - %s ...' % (Color.OKGREEN +
                                                    music.singerName, music.songName + '.mp3' + Color.ENDC))
                        isSucc = download.downloadFile(music)
                        if not isSucc:
                            print(
                                '%s下载失败，正在重试...%s' % (Color.FAIL, Color.ENDC))
                            music.musicInfo = music.getMusicInfo(1)
                            print('歌曲:%s - %s\n歌曲链接:%s\n专辑图片:%s' % (Color.OKBLUE + music.singerName, music.songName + Color.ENDC, Color.OKBLUE + music.musicInfo[0] + Color.ENDC, Color.OKBLUE + music.musicInfo[1] + Color.ENDC))
                            isSucc = download.downloadFile(music)
                            if not isSucc:
                                print('%s下载失败!%s' % (Color.FAIL, Color.ENDC))
                                break
                        print('%s下载完成!%s' % (Color.OKGREEN, Color.ENDC))
                    break
            elif len(command) != 0:
                print('{}错误指令!{}'.format(Color.FAIL, Color.ENDC))
                continue


if __name__ == '__main__':
    main = Main()
    main.mainFun()