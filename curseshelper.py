import curses
from enum import IntEnum


class CursesColor(IntEnum):
    green = 1,
    blue = 2,
    red = 3,
    yellow = 4,
    normal = 5,


class CursesAttr(IntEnum):
    blink = -1,
    bold = -2,
    underline = -3,
    normal = -4,


_Attr = {
    CursesAttr.blink: curses.A_BLINK,
    CursesAttr.bold: curses.A_BOLD,
    CursesAttr.underline: curses.A_UNDERLINE,
    CursesAttr.normal: curses.A_NORMAL,
}

_splitStr = '/f/'


class CursesHelper:

    def __init__(self, stdscr):
        self.stdscr = stdscr
        if not self.stdscr:
            return
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
        key = None
        if needPressKey:
            key = self.getCh()
        self.stdscr.refresh()
        return key

    def getKey(self):
        ch = self.stdscr.getkey()
        return ch

    def getCh(self):
        ch = self.stdscr.getch()
        return ch

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