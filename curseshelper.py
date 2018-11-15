import curses
import threading
from observer import Publisher, eventName
from enum import IntEnum


class CursesColor(IntEnum):
    green = 1
    blue = 2
    red = 3
    yellow = 4
    normal = 5


class CursesAttr(IntEnum):
    blink = -1
    bold = -2
    underline = -3
    normal = -4


_Attr = {
    CursesAttr.blink: curses.A_BLINK,
    CursesAttr.bold: curses.A_BOLD,
    CursesAttr.underline: curses.A_UNDERLINE,
    CursesAttr.normal: curses.A_NORMAL,
}

_splitStr = '/f/'


class CursesHelper():

    def __init__(self, stdscr):
        self.stdscr = stdscr
        if not self.stdscr:
            return
        self.winWidth = self.stdscr.getmaxyx()[1]
        self.winHeight = self.stdscr.getmaxyx()[0]
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, -1, -1)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        self.stdscr.scrollok(True)
        self.stdscr.idlok(True)

    def dealloc(self):
        self.stdscr.keypad(False)
        self.stdscr.scrollok(False)
        self.stdscr.idlok(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    # def _realLen(self, strs):
    #     totalLens = 0
    #     for _str in strs:
    #         totalLens += (len(_str) + sum(1 for ch in _str if ch > chr(127)))
    #     return totalLens

    # def setTitle(self, strs, attrs=None, center=True):
    #     self.title.clear()
    #     if attrs is None:
    #         self.title.addstr(
    #             0, int((self.winWidth - self._realLen(strs)) / 2), strs.encode('utf-8'))
    #     elif attrs is not None and len(attrs) > 0:
    #         arr_str = strs.split(_splitStr)
    #         if len(arr_str) <= 1:
    #             return
    #         if len(arr_str) - 1 != len(attrs):
    #             return
    #         for i in range(len(arr_str)):
    #             if i == 0:
    #                 self.title.addstr(0, self._realLen(
    #                     arr_str[i]), arr_str[i].encode('utf-8'))
    #             else:
    #                 if attrs[i - 1] > 0:
    #                     self.title.addstr(
    #                         arr_str[i].encode('utf-8'), curses.color_pair(attrs[i - 1]))
    #                 elif attrs[i - 1] < 0:
    #                     self.title.addstr(
    #                         arr_str[i].encode('utf-8'), _Attr[attrs[i - 1]])
    #     self.stdscr.refresh()

    def printStr(self, strs, attrs=None, clear=False, newLine=True, needPressKey=False, y=-1, x=-1):
        if attrs is None and y == -1 and x == -1:
            if clear:
                self.stdscr.clear()
            self.stdscr.addstr(strs.encode('utf-8'))
        elif attrs is None and y != -1 and x != -1:
            if clear:
                self.stdscr.clear()
            self.stdscr.addstr(y, x, strs.encode('utf-8'))
        elif attrs is not None and len(attrs) > 0 and y == -1 and x == -1:
            arr_str = strs.split(_splitStr)
            if len(arr_str) <= 1:
                return
            if len(arr_str) - 1 != len(attrs):
                return
            if clear:
                self.stdscr.clear()
            for i in range(len(arr_str)):
                if i == 0:
                    self.stdscr.addstr(arr_str[i].encode('utf-8'))
                else:
                    if attrs[i - 1] > 0:
                        self.stdscr.addstr(
                            arr_str[i].encode('utf-8'), curses.color_pair(attrs[i - 1]))
                    elif attrs[i - 1] < 0:
                        self.stdscr.addstr(
                            arr_str[i].encode('utf-8'), _Attr[attrs[i - 1]])
        elif attrs is not None and len(attrs) > 0 and y != -1 and x != -1:
            arr_str = strs.split(_splitStr)
            if len(arr_str) <= 1:
                return
            if len(arr_str) - 1 != len(attrs):
                return
            if clear:
                self.stdscr.clear()
            for i in range(len(arr_str)):
                if i == 0:
                    self.stdscr.addstr(y, x, arr_str[i].encode('utf-8'))
                else:
                    if attrs[i - 1] > 0:
                        self.stdscr.addstr(
                            arr_str[i].encode('utf-8'), curses.color_pair(attrs[i - 1]))
                    elif attrs[i - 1] < 0:
                        self.stdscr.addstr(
                            arr_str[i].encode('utf-8'), _Attr[attrs[i - 1]])
        if newLine:
            self.stdscr.addstr('\n'.encode('utf-8'))
        self.stdscr.refresh()
        key = None
        if needPressKey:
            key = self.getKey()
        return key

    def getKey(self):
        try:
            ch = self.stdscr.getkey()
            return ch
        except:
            return ''

    def getCh(self):
        try:
            ch = self.stdscr.getch()
            return ch
        except:
            return chr('')

    def clearSrc(self):
        self.stdscr.clear()

    def getStr(self):
        curses.echo()
        curses.nocbreak()
        _str = self.stdscr.getstr()
        curses.noecho()
        curses.cbreak()
        return _str.decode('utf-8')

    def scrollUp(self):
        if self.stdscr:
            self.stdscr.scroll(-1)

    def scrollDown(self):
        if self.stdscr:
            self.stdscr.scroll(1)