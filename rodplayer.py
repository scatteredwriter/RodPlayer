from music import Music, MusicInfo, getMusicList
from observer import Listener, Event, eventName
from curseshelper import CursesHelper, CursesColor, CursesAttr
from enum import Enum
import curses
import curseshelper
import download
import playmusic
import re


class _helpKey(Enum):
    allPage = '所有页面'
    mainPage = '主页面'
    playList = '播放列表'
    musicSearchResult = '歌曲搜索结果'
    musicDetail = '歌曲详情'


_helpDict = {
    _helpKey.allPage: {
        'q/Q': '退出当前页面',
    },
    _helpKey.mainPage: {
        's/S': '搜索',
        'l/L': '查看播放列表',
        'p/P': '暂停或播放',
        'n/N': '下一首',
        'b/B': '上一首',
        'm/M': '更换播放模式',
        'h/H': '查看帮助',
    },
    _helpKey.playList: {
        '方向键下': '下一页',
        '方向键上': '上一页',
        'p/P': '播放播放列表中的歌曲',
        'd/D': '删除播放列表中的歌曲',
        'c/C': '清除播放列表',
    },
    _helpKey.musicSearchResult: {
        '方向键下': '下一页',
        '方向键上': '上一页',
        'a/A': '添加当前页所有歌曲至播放列表',
        'd/D': '查看歌曲详情',
    },
    _helpKey.musicDetail: {
        'a/A': '添加当前歌曲至播放列表',
        'd/D': '下载当前歌曲',
    }
}


class Main(Listener):
    def __init__(self):
        self.player = playmusic.Player()
        self.addObserver(self.player, eventName.MusicCompletation)
        self.addObserver(self.player, eventName.MusicAdded)
        self.addObserver(self.player, eventName.MusicDeleted)
        self.addObserver(self.player, eventName.PlayError)
        self.stdscr = curses.initscr()
        self.cursesHelper = CursesHelper(self.stdscr)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def _dealloc(self):
        if self.player:
            self.player.executeCommand(playmusic.PlayerCommand.QUIT)
            self.removeObserver(self.player, eventName.MusicCompletation)
            self.removeObserver(self.player, eventName.MusicAdded)
            self.removeObserver(self.player, eventName.MusicDeleted)
            self.removeObserver(self.player, eventName.PlayError)
        if self.cursesHelper:
            self.cursesHelper.dealloc()
        exit()

    def onNotify(self, event):
        if not isinstance(event, Event):
            return
        if event.eventName == eventName.MusicCompletation:
            self._printPlayerStatus()
        elif event.eventName == eventName.MusicAdded:
            if not isinstance(event.eventContent, tuple) or len(event.eventContent) != 2:
                return
            self._printAddedMusic(
                event.eventContent[0], event.eventContent[1])
        elif event.eventName == eventName.MusicDeleted:
            if not isinstance(event.eventContent, tuple) or len(event.eventContent) != 2:
                return
            self._printDeletedMusic(
                event.eventContent[0], event.eventContent[1])
        elif event.eventName == eventName.PlayError:
            if not isinstance(event.eventContent, tuple) or len(event.eventContent) != 2:
                return
            self._printPlayError(event.eventContent[0], event.eventContent[1])

    def _addAll(self, musics):
        if not musics or len(musics) == 0:
            self._printErrorCommand()
            return
        if self.player is None:
            self.player = playmusic.Player()
        self.cursesHelper.printStr(
            '/f/正在添加歌曲至播放列表...', [CursesColor.blue], clear=True)
        for i in range(len(musics)):
            for j in range(3):
                try:
                    music = musics[i]
                    music.musicInfo = music.getMusicInfo(0)
                    break
                except:
                    self.cursesHelper.printStr('/f/第{}次添加 {} - {} 失败! 正在重试...'.format(str(j+1), music.singerName, music.songName), [CursesColor.red])
                    continue
            self.player.addMusic(music)
        if len(musics) == 1:
            self.cursesHelper.getCh()
            return
        self.cursesHelper.printStr(
            '/f/添加完成!', [CursesColor.blue], needPressKey=True)

    def _printPlayError(self, singerName, songName):
        self.cursesHelper.printStr('/f/播放 {} - {} 遇到错误,正在第{}次重试...'.format(
            singerName, songName), [CursesColor.red], clear=True)
        # self._printPlayerStatus(False)

    def _printAddedMusic(self, singerName, songName):
        self.cursesHelper.printStr('/f/已添加 /f/{} - {} /f/至播放列表'.format(
            singerName, songName), (CursesColor.blue, CursesColor.green, CursesColor.normal))

    def _showPlayList(self):
        if self.player and len(self.player.playList) > 0:
            p = 1
            begin = 0
            step = 20
            pageLens = step
            while(True):
                self.cursesHelper.printStr('/f/播放列表:(共{}首)'.format(
                    str(len(self.player.playList))), [CursesColor.blue], True)
                if len(self.player.playList) <= begin:
                    #已到最后一页
                    if p > 1:
                        p -= 1
                begin = step * (p - 1)
                if len(self.player.playList) - (begin + step) < 0:
                    #最后一页不够一个step展示
                    pageLens = len(self.player.playList) - begin
                else:
                    pageLens = step
                for i in range(pageLens):
                    index = i + begin
                    if i == self.player._cur_index:
                        self.cursesHelper.printStr(
                            '/f/>[{}].歌曲:{}\t歌手:{}\t专辑:{}'.format(str(index),
                                                                  self.player.playList[index].songName,
                                                                  self.player.playList[index].singerName,
                                                                  self.player.playList[index].albumName), [CursesColor.blue])
                    else:
                        self.cursesHelper.printStr(
                            '[/f/{}/f/]./f/歌曲/f/:/f/{}\t/f/歌手/f/:/f/{}\t/f/专辑/f/:/f/{}'.format(str(index),
                                                                                               self.player.playList[index].songName,
                                                                                               self.player.playList[index].singerName,
                                                                                               self.player.playList[index].albumName), (CursesColor.green, CursesColor.normal,
                                                                                                                                        CursesColor.green, CursesColor.normal,
                                                                                                                                        CursesAttr.bold,
                                                                                                                                        CursesColor.green, CursesColor.normal,
                                                                                                                                        CursesAttr.bold,
                                                                                                                                        CursesColor.green, CursesColor.normal,
                                                                                                                                        CursesAttr.bold))
                begin += pageLens
                self._printHelp(_helpKey.playList, needPressKey=False)
                command = self.cursesHelper.printStr(
                    '请输入命令:', needPressKey=True, newLine=False)
                if command == 'q' or command == 'Q':
                    #退出
                    return
                elif command == 'd' or command == 'D':
                    #删除播放列表中对应序号的歌曲
                    self.cursesHelper.printStr(
                        '请输入要删除的/f/歌曲序号/f/(用/f/空格/f/分割序号进行多选):',
                        (CursesColor.yellow, CursesColor.normal, CursesColor.yellow, CursesColor.normal), newLine=False, curLine=True)
                    command = self.cursesHelper.getStr()
                    try:
                        pattern = re.compile(r'\d+')
                        result = re.findall(pattern, command)
                        if len(result) <= 0:
                            continue
                        indexs = []
                        for index in result:
                            indexs.append(int(index))
                        self.cursesHelper.clearSrc()
                        self.player.deleteMusic(indexs)
                        self.cursesHelper.getCh()
                        continue
                    except:
                        continue
                elif command == 'p' or command == 'P':
                    #播放播放列表中对应序号的歌曲
                    self.cursesHelper.printStr(
                        '请输入要播放的/f/歌曲序号:', [CursesColor.yellow], newLine=False, curLine=True)
                    command = self.cursesHelper.getStr()
                    try:
                        pattern = re.compile(r'(\d+)')
                        result = re.search(pattern, command).groups()
                        if len(result) != 1:
                            continue
                        index = int(result[0])
                        self.player.playMusic(index)
                        return
                    except:
                        continue
                elif command == 'c' or command == 'C':
                    #清除播放列表
                    self._clearPlayList()
                    self.cursesHelper.printStr(
                        '/f/播放列表已清空', [CursesColor.green], clear=True, needPressKey=True)
                    return
                elif command == 'KEY_UP':
                    #上一页
                    if p > 1:
                        p -= 1
                    continue
                elif command == 'KEY_DOWN':
                    #下一页
                    p += 1
                    continue
                else:
                    continue
        else:
            self.cursesHelper.printStr(
                '/f/播放列表为空', [CursesColor.red], clear=True, needPressKey=True)

    def _clearPlayList(self):
        if self.player:
            self.player.clearPlayList()

    def _printPlayerStatus(self, clear=True):
        if clear:
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
                                                                                                   CursesColor.blue))
        self.cursesHelper.printStr('请输入命令(/f/h/H/f/查看帮助):', (
            CursesColor.yellow, CursesColor.normal), newLine=False)

    def _printDeletedMusic(self, singerName, songName):
        self.cursesHelper.printStr(
            '/f/已删除 {} - {}'.format(singerName, songName), [CursesColor.green])

    def _printHelp(self, selectedTitle=None, needPressKey=True):
        if not selectedTitle:
            self.cursesHelper.clearSrc()
        if selectedTitle:
            self.cursesHelper.printStr(
                '/f/指令帮助:{}'.format(selectedTitle.value), [CursesAttr.bold])
            for (key, value) in _helpDict[selectedTitle].items():
                self.cursesHelper.printStr(
                    '/f/{}/f/:\t/f/{}'.format(key, value), (CursesColor.blue, CursesColor.normal, CursesColor.green))
        else:
            for (mainTitle, mainValue) in _helpDict.items():
                self.cursesHelper.printStr(
                    '/f/{}:'.format(mainTitle.value), [CursesAttr.bold])
                for (key, value) in mainValue.items():
                    self.cursesHelper.printStr(
                        '/f/{}/f/:\t/f/{}'.format(key, value), (CursesColor.blue, CursesColor.normal, CursesColor.green))
        if needPressKey:
            return self.cursesHelper.getKey()
        else:
            return None

    def _printErrorCommand(self, wording=None, attrs=None, needPressKey=True):
        if wording and attrs:
            self.cursesHelper.printStr(
                wording, attrs, needPressKey=needPressKey)
        else:
            self.cursesHelper.printStr(
                '/f/错误指令!', [CursesColor.red], needPressKey=needPressKey)

    def _search(self):
        #搜索
        musicDict = {}
        p = 1
        begin = 0
        nextPage = True
        self.cursesHelper.printStr('请输入搜索关键字(/f/q或Q/f/取消):', (
            CursesColor.yellow, CursesColor.normal), clear=True, newLine=False)
        command = self.cursesHelper.getStr()
        if command == 'q' or command == 'Q':
            return
        keyword = command
        #执行搜索
        while(True):
            try:
                if nextPage:
                    #搜索下一页
                    if p not in musicDict:
                        #还没有该页的歌曲数据
                        newMusics = getMusicList(keyword, p)
                        if len(musicDict) == 0 and len(newMusics) == 0:
                            command = self.cursesHelper.printStr(
                                '/f/搜索失败!(q或Q退出,任意键重试)/f/', (CursesColor.red, CursesColor.normal), clear=True, needPressKey=True)
                            if command == 'q' or command == 'Q':
                                return
                            continue
                        elif len(newMusics) == 0:
                            self.cursesHelper.printStr(
                                '/f/已到最后一页!', [CursesColor.red], clear=True, needPressKey=True)
                            p -= 1
                        else:
                            musicDict[p] = newMusics
                            if p > 1:
                                begin += len(musicDict[p-1])
                    else:
                        if p > 1:
                            begin += len(musicDict[p-1])
                    nextPage = False
                musics = musicDict[p]
                self.cursesHelper.printStr(
                    '/f/{} 搜索结果:'.format(keyword), [CursesColor.blue], clear=True)
                for i in range(len(musics)):
                    self.cursesHelper.printStr(
                        '[{}]./f/歌曲/f/:/f/{}\t/f/歌手/f/:/f/{}\t/f/专辑/f/:/f/{}'.format(str(i+begin),
                                                                                     musics[i].songName,
                                                                                     musics[i].singerName,
                                                                                     musics[i].albumName), (
                                                                                CursesColor.green, CursesColor.normal,
                                                                                CursesAttr.bold,
                                                                                CursesColor.green, CursesColor.normal,
                                                                                CursesAttr.bold,
                                                                                CursesColor.green, CursesColor.normal,
                                                                                CursesAttr.bold))
            except:
                command = self.cursesHelper.printStr(
                    '/f/搜索失败!(q或Q退出,任意键重试)/f/', (CursesColor.red, CursesColor.normal), clear=True, needPressKey=True)
                if command == 'q' or command == 'Q':
                    return
                continue
            self._printHelp(_helpKey.musicSearchResult, needPressKey=False)
            command = self.cursesHelper.printStr(
                '请输入命令:', needPressKey=True, newLine=False)
            if command == 'q' or command == 'Q':
                #退出
                return
            elif command == 'a' or command == 'A':
                #添加当前所有歌曲至播放列表
                self._addAll(musicDict[p])
                continue
            elif command == 'KEY_UP':
                #上一页
                if p > 1:
                    begin -= len(musicDict[p])
                    p -= 1
                continue
            elif command == 'KEY_DOWN':
                #下一页
                nextPage = True
                p += 1
                continue
            elif command == 'd' or command == 'D':
                #查看歌曲详情
                self.cursesHelper.printStr(
                    '请输入要查看的/f/歌曲序号/f/(用/f/空格/f/分割序号进行多选):',
                    (CursesColor.yellow, CursesColor.normal, CursesColor.yellow, CursesColor.normal), newLine=False, curLine=True)
                command = self.cursesHelper.getStr()
                pattern = re.compile(r'\d+')
                musicIndexs = re.findall(pattern, command)
                if len(musicIndexs) <= 0:
                    self._printErrorCommand()
                    return
                else:
                    self._musicsDetail(musicIndexs, musicDict[p], begin)
                    continue

    def _musicsDetail(self, musicIndexs, musics, begin):
        '''查看歌曲详情'''
        if len(musicIndexs) <= 0:
            self._printErrorCommand()
            return
        for selectIndex in musicIndexs:
            self.cursesHelper.clearSrc()  # 清屏
            selectIndex = int(selectIndex) - begin
            if selectIndex < 0 or selectIndex >= len(musics):
                self._printErrorCommand('/f/歌曲编号{}已超出当前页歌曲列表范围!'.format(
                    str(selectIndex)), [CursesColor.red])
                continue
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
            self._printHelp(_helpKey.musicDetail, needPressKey=False)
            command = self.cursesHelper.printStr(
                '请输入命令:', needPressKey=True, newLine=False)
            if command == 'q' or command == 'Q':
                #退出查看当前歌曲详情
                continue
            elif command == 'a' or command == 'A':
                #添加当前歌曲至播放列表
                self._addAll([music])
                continue
            elif command == 'd' or command == 'D':
                #下载
                self.cursesHelper.printStr('开始下载 /f/{} - {}/f/ ...'.format(music.singerName, music.songName + '.mp3'), (CursesColor.green, CursesColor.normal), clear=True)
                isSucc = download.downloadFile(music)
                if not isSucc:
                    self.cursesHelper.printStr('/f/下载失败，正在重试.../f/', (
                        CursesColor.red, CursesColor.normal))
                    music.musicInfo = music.getMusicInfo(1)
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
                        self.cursesHelper.printStr(
                            '/f/下载失败!', [CursesColor.red], needPressKey=True)
                        break
                self.cursesHelper.printStr(
                    '/f/下载完成!', [CursesColor.green], needPressKey=True)
            else:
                self._printErrorCommand()
                continue

    def mainFun(self):
        while(True):
            self._printPlayerStatus()
            command = self.cursesHelper.getKey()
            if command == 'q' or command == 'Q':
                #退出
                self._dealloc()
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
            elif command == 'h' or command == 'H':
                #查看帮助
                self._printHelp()
                continue
            elif command == 's' or command == 'S':
                #搜索
                self._search()
                continue
            # elif command == 'KEY_UP':
            #     # self.cursesHelper.scrollUp()
            #     self.cursesHelper.stdscr.refresh(-1, 0, 5, 5, 10, 60)
            # elif command == 'KEY_DOWN':
            #     # self.cursesHelper.scrollDown()
            #     self.cursesHelper.stdscr.refresh(1, 0, 5, 5, 10, 60)


if __name__ == '__main__':
    main = Main()
    main.mainFun()