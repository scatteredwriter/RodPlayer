from music import Music, MusicInfo, getMusicList
from observer import Listener, Event, eventName
from curseshelper import CursesHelper, CursesColor, CursesAttr
import curses
import curseshelper
import download
import playmusic
import re


_helpDict = {
    '所有页面': {
        'q/Q': '取消',
    },
    '主页面': {
        's/S': '搜索',
        'l/L': '查看播放列表',
        'p/P': '暂停/播放',
        'n/N': '下一首',
        'b/B': '上一首',
        'm/M': '更换播放模式',
        'c/C': '清除播放列表',
        'h/H': '查看帮助',
    },
    '歌曲搜索': {
        'q/Q': '重新搜索',
        '回车': '下一页',
        'a/A': '添加当页所有歌曲至播放列表',
    },
    '歌曲详情': {
        'a/A': '添加当前歌曲至播放列表',
    }
}


class Main(Listener):
    def __init__(self):
        self.player = playmusic.Player()
        self.addObserver(self.player, eventName.MusicCompletation)
        self.addObserver(self.player, eventName.musicDeleted)
        self.stdscr = curses.initscr()
        self.cursesHelper = CursesHelper(self.stdscr)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def onNotify(self, event):
        if not isinstance(event, Event):
            return
        if event.eventName == eventName.MusicCompletation:
            self._printPlayerStatus()
        elif event.eventName == eventName.musicDeleted:
            if not isinstance(event.eventContent, tuple):
                return
            self._printDeletedMusic(
                event.eventContent[0], event.eventContent[1])
            self.cursesHelper.getCh()

    def _addAll(self, begin, musics):
        if self.player is None:
            self.player = playmusic.Player()
        self.cursesHelper.clearSrc()
        for i in range(begin, len(musics)):
            for j in range(3):
                try:
                    music = musics[i]
                    music.musicInfo = music.getMusicInfo(0)
                    break
                except:
                    self.cursesHelper.printStr('/f/第{}次添加 {} - {} 失败! 正在重试...'.format(str(j+1), music.singerName, music.songName), [CursesColor.red])
                    continue
            self.player.addMusic(music)
            self.cursesHelper.printStr('/f/已添加 /f/{} - {} /f/至播放列表'.format(music.singerName, music.songName), (CursesColor.blue, CursesColor.green, CursesColor.normal))
        self.cursesHelper.printStr(
            '/f/添加完成!', [CursesColor.blue], needPressKey=True)

    def _showPlayList(self):
        if self.player and len(self.player.playList) > 0:
            self.cursesHelper.printStr('/f/播放列表:(共{}首)'.format(
                str(len(self.player.playList))), [CursesColor.blue], True)
            for i in range(len(self.player.playList)):
                if i == self.player._cur_index:
                    self.cursesHelper.printStr(
                        '/f/[{}].歌曲:{}\t歌手:{}\t专辑:{}'.format(str(i),
                                                             self.player.playList[i].songName,
                                                             self.player.playList[i].singerName,
                                                             self.player.playList[i].albumName), [CursesColor.blue])
                else:
                    self.cursesHelper.printStr(
                        '[/f/{}/f/]./f/歌曲/f/:/f/{}\t/f/歌手/f/:/f/{}\t/f/专辑/f/:/f/{}'.format(str(i),
                                                                                           self.player.playList[i].songName,
                                                                                           self.player.playList[i].singerName,
                                                                                           self.player.playList[i].albumName), (CursesColor.green, CursesColor.normal,
                                                                                                                                CursesColor.green, CursesColor.normal,
                                                                                                                                CursesAttr.bold,
                                                                                                                                CursesColor.green, CursesColor.normal,
                                                                                                                                CursesAttr.bold,
                                                                                                                                CursesColor.green, CursesColor.normal,
                                                                                                                                CursesAttr.bold))
            self.cursesHelper.printStr(
                '请输入要播放的歌曲/f/序号/f/或其他命令(用/f/空格/f/分割序号进行多选):',
                (CursesColor.yellow, CursesColor.normal, CursesColor.yellow, CursesColor.normal))
            command = self.cursesHelper.getStr()
            if command[0:1] == 'd' or command[0:1] == 'D':
                #删除播放列表中对应序号的歌曲
                try:
                    pattern = re.compile(r'\d+')
                    result = re.findall(pattern, command)
                    if len(result) <= 0:
                        self.cursesHelper.printStr(
                            '/f/错误指令!', [CursesColor.red])
                        return
                    indexs = []
                    for index in result:
                        indexs.append(int(index))
                    self.player.deleteMusic(indexs)
                except:
                    self.cursesHelper.printStr(
                        '/f/错误指令!', [CursesColor.red])
                return
            else:
                #播放列表中对应序号的歌曲
                try:
                    pattern = re.compile(r'(\d+)')
                    result = re.search(pattern, command).groups()
                    if len(result) != 1:
                        self.cursesHelper.printStr(
                            '/f/错误指令!', [CursesColor.red])
                        return
                    index = int(result[0])
                    self.player.playMusic(index)
                except:
                    self.cursesHelper.printStr(
                        '/f/错误指令!', [CursesColor.red])
                return
        else:
            self.cursesHelper.printStr(
                '/f/播放列表为空', [CursesColor.red], clear=True, needPressKey=True)

    def _clearPlayList(self):
        if self.player:
            self.player.clearPlayList()

    def _printPlayerStatus(self):
        self.cursesHelper.clearSrc()
        if self.player and self.player.cur_music:
            play_mode = ''
            if self.player.play_mode == playmusic.PlayMode.NORMAL:
                play_mode = '顺序播放'
            elif self.player.play_mode == playmusic.PlayMode.REVERSE:
                play_mode = '逆序播放'
            self.cursesHelper.printStr(
                '正在播放:/f/{} - {}/f/\t播放模式:/f/{}'.format(
                    self.player.cur_music.singerName, self.player.cur_music.songName, play_mode), (CursesColor.green,
                                                                                                   CursesColor.normal,
                                                                                                   CursesColor.blue), True)

    def _printDeletedMusic(self, singerName, songName):
        self.cursesHelper.printStr(
            '/f/已删除 {} - {}'.format(singerName, songName), [CursesColor.green])

    def _printHelp(self):
        self.cursesHelper.clearSrc()
        for (mainTitle, mainValue) in _helpDict:
            self.cursesHelper.printStr(
                '/f/{}:'.format(mainTitle), [CursesColor.blue])
            for (key, value) in mainValue:
                self.cursesHelper.printStr(
                    '/f/{}/f/\t:\t/f/{}'.format(key, value), (CursesColor.blue, CursesColor.normal, CursesColor.green))
        self.cursesHelper.getCh()
#         print('{}\
# 所有页面:\n\
# q/Q:取消\n\
# \n主页面:\n\
# s/S:搜索\n\
# l/L:查看播放列表\n\
# p/P:暂停/播放\n\
# p [编号]/P [编号]:播放列表中对应序号的歌曲\n\
# n/N:下一首\n\
# b/B:上一首\n\
# m/M:更换播放模式\n\
# d [编号]/D [编号]:删除播放列表中对应序号的歌曲,多个编号可用空格分隔\n\
# c/C:清除播放列表\n\
# h/H:查看帮助\n\
# \n歌曲搜索:\n\
# q/Q:重新搜索\n\
# 回车:下一页\n\
# a/A:添加当页所有歌曲至播放列表\n\
# \n歌曲详情:\n\
# a/A:添加当前歌曲至播放列表\n\
# {}'.format(Color.OKBLUE, Color.ENDC))

    def mainFun(self):
        while(True):
            musics = []
            begin = 0
            p = 0
            self._printPlayerStatus()
            self.cursesHelper.printStr('请输入命令(/f/h/H/f/查看帮助):', (
                CursesColor.yellow, CursesColor.normal))
            command = self.cursesHelper.getKey()
            if command == 'q' or command == 'Q':
                #退出
                if self.player:
                    self.player.executeCommand(playmusic.PlayerCommand.STOP)
                    self.addObserver(self.player, eventName.MusicCompletation)
                    self.addObserver(self.player, eventName.musicDeleted)
                    self.stdscr.keypad(False)
                    curses.echo()
                    curses.nocbreak()
                    curses.endwin()
                exit()
            elif command == 'p' or command == 'P':
                if self.player:
                #暂停/播放
                    self.player.executeCommand(
                        playmusic.PlayerCommand.PAUSE)
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
            elif command == 'h' or command == 'H':
                #查看帮助
                self._printHelp()
                continue
            elif command == 's' or command == 'S':
                #搜索
                # command = input(
                #     '请输入搜索关键字(%sq%s取消):' % (Color.WARNING, Color.ENDC))
                self.cursesHelper.printStr('请输入搜索关键字(/f/q或Q/f/取消):', (
                    CursesColor.yellow, CursesColor.normal), True)
                command = self.cursesHelper.getStr()
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
                            # print('%s已到最后一页!%s' % (Color.FAIL, Color.ENDC))
                            self.cursesHelper.printStr(
                                '/f/已到最后一页!', [CursesColor.red])
                        else:
                            musics.extend(newMusics)
                            self.cursesHelper.printStr(
                                '/f/{} 搜索结果:'.format(command), [CursesColor.blue], True)
                            for i in range(begin, len(musics)):
                                realI = i
                                self.cursesHelper.printStr(
                                    '[{}]./f/歌曲/f/:/f/{}\t/f/歌手/f/:/f/{}\t/f/专辑/f/:/f/{}'.format(str(realI),
                                                                                                 musics[realI].songName,
                                                                                                 musics[realI].singerName,
                                                                                                 musics[realI].albumName), (
                                                                                            CursesColor.green, CursesColor.normal,
                                                                                            CursesAttr.bold,
                                                                                            CursesColor.green, CursesColor.normal,
                                                                                            CursesAttr.bold,
                                                                                            CursesColor.green, CursesColor.normal,
                                                                                            CursesAttr.bold))
                    except:
                        self.cursesHelper.printStr('/f/搜索失败!/f/', (
                            CursesColor.red, CursesColor.normal))
                        break
                    self.cursesHelper.printStr(
                        '请输入要下载的歌曲/f/序号/f/或其他命令(用/f/空格/f/分割序号进行多选):',
                        (CursesColor.yellow, CursesColor.normal, CursesColor.yellow, CursesColor.normal))
                    command = self.cursesHelper.getStr()
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
                        self.cursesHelper.clearSrc()
                        music = musics[int(selectIndex)]
                        for j in range(3):
                            try:
                                music.musicInfo = music.getMusicInfo(0)
                                break
                            except:
                                self.cursesHelper.printStr('/f/第{}次获取 {} - {} 信息失败! 正在重试.../f/'.format(str(j+1), music.singerName, music.songName), (CursesColor.red, CursesColor.normal))
                                continue
                        self.cursesHelper.printStr(
                            '歌曲:/f/{} - {}/f/\n歌曲链接:/f/{}/f/\n专辑图片:/f/{}'.format(music.singerName,
                                                                                 music.songName,
                                                                                 music.musicInfo.music_url,
                                                                                 music.musicInfo.albumImg_url), (CursesColor.blue,
                                                                                                                 CursesColor.normal,
                                                                                                                 CursesAttr.underline,
                                                                                                                 CursesAttr.normal,
                                                                                                                 CursesAttr.underline))
                        # command = input('输入任意键下载或其他命令:')
                        self.cursesHelper.printStr('输入任意键下载或其他命令:')
                        command = self.cursesHelper.getKey()
                        if command == 'q' or command == 'Q':
                            continue
                        elif command == 'a' or command == 'A':
                            # if self.player is None:
                            #     self.player = playmusic.Player()
                            # self.player.addMusic(music)
                            self._addAll(0, [music])
                            continue
                        # print('开始下载 %s - %s ...' % (Color.OKGREEN +
                        #                             music.singerName, music.songName + '.mp3' + Color.ENDC))
                        self.cursesHelper.printStr('开始下载 /f/{} - {}/f/ ...'.format(music.singerName, music.songName + '.mp3'), (CursesColor.green, CursesColor.normal))
                        isSucc = download.downloadFile(music)
                        if not isSucc:
                            # print(
                            #     '%s下载失败，正在重试...%s' % (Color.FAIL, Color.ENDC))
                            self.cursesHelper.printStr('/f/下载失败，正在重试.../f/', (
                                CursesColor.red, CursesColor.normal))
                            music.musicInfo = music.getMusicInfo(1)
                            # print('歌曲:%s - %s\n歌曲链接:%s\n专辑图片:%s' % (Color.OKBLUE + music.singerName, music.songName + Color.ENDC, Color.OKBLUE + music.musicInfo.music_url + Color.ENDC, Color.OKBLUE + music.musicInfo.albumImg_url + Color.ENDC))
                            self.cursesHelper.printStr(
                                '歌曲:/f/{} - {}/f/\n歌曲链接:/f/{}/f/\n专辑图片:/f/{}'.format(music.singerName,
                                                                                     music.songName,
                                                                                     music.musicInfo.music_url,
                                                                                     music.musicInfo.albumImg_url), (CursesColor.blue,
                                                                                                                     CursesColor.normal,
                                                                                                                     CursesAttr.underline,
                                                                                                                     CursesAttr.normal,
                                                                                                                     CursesAttr.underline))
                            isSucc = download.downloadFile(music)
                            if not isSucc:
                                # print('%s下载失败!%s' % (Color.FAIL, Color.ENDC))
                                self.cursesHelper.printStr(
                                    '/f/下载失败!', [CursesColor.red], needPressKey=True)
                                break
                        # print('%s下载完成!%s' % (Color.OKGREEN, Color.ENDC))
                        self.cursesHelper.printStr(
                            '/f/下载完成!', [CursesColor.green], needPressKey=True)
                    break
            elif command == 'KEY_UP':
                self.cursesHelper.scrollUp()
            elif command == 'KEY_DOWN':
                self.cursesHelper.scrollDown()
            # elif len(command) != 0:
            #     # print('{}错误指令!{}'.format(Color.FAIL, Color.ENDC))
            #     self.cursesHelper.printStr('/f/错误指令!', [CursesColor.red])
            #     continue


if __name__ == '__main__':
    main = Main()
    main.mainFun()