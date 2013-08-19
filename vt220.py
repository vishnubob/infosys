#!/usr/bin/python
import serial
import figlet
import socket
import time
import re
import os

# Escape
ESC = '\x1b'
# Index  
IND = ESC + 'D'
# Next line
NEL = ESC + 'E'
# Horizontal tab set
HTS = ESC + 'H'
# Reverse index
RI = ESC + 'M'
# Single shift G2
SS2 = ESC + 'N'
# Single shift G3
SS3 = ESC + 'O'
# Device control string
DCS = ESC + 'P'
# Control sequence introducer
CSI = ESC + '['
# String terminator
ST = ESC + '\\'
## CUP - Cursor Position
CUP = CSI + '%d;%df'

## IRM Insertion-Replacement Mode
IRMI = CSI + '4h'
IRMR = CSI + '4l'

## CKM Cursor key mode
CKMVIS = CSI + '?25h'
CKMINV = CSI + '?25l'

## Erase in display
# Erase from the active position to the end of the screen, inclusive (default)
ED0 = CSI + '0J'
# Erase from start of the screen to the active position, inclusive
ED1 = CSI + '1J'
# Erase all of the display, cursor does not move.
ED2 = CSI + '2J'

WIDTH = 160
HEIGHT = 25
LEFT_CLIP = 80
RIGHT_CLIP = 81

space_re = re.compile('\s+')

class SocketDisplay:
    SocketName = 'display.socket'

    def __init__(self, socket):
        self.socket = socket
        self.current_page = Page()

    def clear_screen(self, screen=0):
        if screen == 0:
            self.socket.send(ED2)
            self.socket.send(ED2)
        elif screen == 1:
            self.socket.send(ED2)
        elif screen == 2:
            self.socket.send(ED2)

    def draw(self, page):
        buffer = ''
        try:
            for y in range(HEIGHT):
                buffer += CUP % (y+1, 1)
                for x in range(WIDTH):
                    if page.page[x][y] == None:
                        char = ' '
                    else:
                        char = str(page.page[x][y])
                    buffer += char
            self.socket.send(buffer)
        except:
            import traceback
            traceback.print_exc()

class Display:
    def __init__(self):
        self.current_page = Page()

    def clear_screen(self, screen=0):
        if screen == 0:
            self.right.write(ED2)
            self.left.write(ED2)
        elif screen == 1:
            self.right.write(ED2)
        elif screen == 2:
            self.left.write(ED2)

    def open(self): 
        df = DisplayFactory.get_instance()
        df.open()
        self.left = df.left
        self.right = df.right

    def reboot(self):
        df = DisplayFactory.get_instance()
        df.reboot()
        self.left = df.left
        self.right = df.right

    def close(self):
        df = DisplayFactory.get_instance()
        df.close()

    def _draw(self, page):
        cp = self.current_page
        np = page
        for y in range(cp.height):
            for right_flag in (0, 1):
                txt = ''
                skip = 1
                for x in range(LEFT_CLIP):
                    cc = cp.page[x+(LEFT_CLIP*right_flag)][y]
                    nc = np.page[x+(LEFT_CLIP*right_flag)][y]
                    # if current character equals next character
                    if cc == nc:
                        skip += 1
                        continue
                    if skip:
                        txt += CUP % (y+1, x+1)
                        skip = 0
                    if nc == None:
                        nc = ' '
                    txt += nc
                if txt:
                    txt = str(txt)
                if right_flag:
                    if txt:
                        self.right.write(txt)
                        self.left.flush()
                else:
                    if txt:
                        self.left.write(txt)
                        self.right.flush()
        self.current_page = page

    def draw(self, page):
        cp = self.current_page
        np = page
        left_page = ''
        right_page = ''
        for y in range(cp.height):
            for right_flag in (0, 1):
                txt = ''
                skip = 1
                for x in range(LEFT_CLIP):
                    cc = cp.page[x+(LEFT_CLIP*right_flag)][y]
                    nc = np.page[x+(LEFT_CLIP*right_flag)][y]
                    # if current character equals next character
                    if cc == nc:
                        skip += 1
                        continue
                    if skip:
                        txt += CUP % (y+1, x+1)
                        skip = 0
                    if nc == None:
                        nc = ' '
                    txt += nc
                if txt:
                    txt = str(txt)
                if right_flag:
                    right_page += txt
                else:
                    left_page += txt
        self.left.write(left_page)
        self.right.write(right_page)
        self.current_page = page


class Page(object):
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.new_page()
        self.cursor = (0,0)

    def __str__(self):
        buf = ''
        for y in range(self.height):
            for x in range(self.width):
                ch = self.page[x][y]
                if ch == None:
                    ch = '`'
                buf += ch
        return buf

    def copy(self):
        copy = self.__class__()
        for x in range(self.width):
            for y in range(self.height):
                copy.page[x][y] = self.page[x][y]
        return copy

    def new_page(self):
        self.page = []
        for x in range(self.width):
            self.page.append([None] * self.height)

    def set_cursor(self, x, y):
        assert x <= self.width
        assert y <= self.height
        self.cursor = (x, y)

    def write(self, line):
        yoff = self.cursor[1]
        for x in range(len(line)):
            xoff = x + self.cursor[0]
            # hard clip
            if xoff > self.width - 1:
                break
            self.page[xoff][yoff] = line[x]

class Clip(object):
    def __init__(self):
        self.left_margin = 0
        self.right_margin = WIDTH
        self.top_margin = 0
        self.bottom_margin = HEIGHT
        self.width = WIDTH
        self.height = HEIGHT
        self.midline = LEFT_CLIP

    def set_margins(self, margins):
        self.left_margin = margins[0]
        self.right_margin = margins[1]
        self.top_margin = margins[2]
        self.bottom_margin = margins[3]
        self.width = self.right_margin - self.left_margin
        self.height = self.bottom_margin - self.top_margin

    def get_margins(self):
        return (self.left_margin, self.right_margin, \
                    self.top_margin, self.bottom_margin)

    def clip_x(self, x):
        return (x >= self.right_margin or x < self.left_margin)

    def clip_y(self, y):
        return (y >= self.bottom_margin or y < self.top_margin)

    def clip_xy(self, x, y):
        return (self.clip_x(x) or self.clip_y(y))

    def clip_left_screen(self, x):
        return (x <= RIGHT_CLIP)

    def clip_right_screen(self, x):
        return (x > LEFT_CLIP)
            
class Transition(Clip):
    def __init__(self, page1, page2):
        super(Transition, self).__init__()
        self.current_page = page1
        self.next_page = page2

    def __iter__(self):
        return self

    def draw_next_page(self, x, y):
        return True

    def next(self):
        newpage = Page()
        for y in range(self.bottom_margin):
            for x in range(self.right_margin):
                if self.draw_next_page(x, y):
                    newpage.page[x][y] = self.next_page.page[x][y]
                else:
                    newpage.page[x][y] = self.current_page.page[x][y]
        return newpage

class Animation(Clip):
    def __iter__(self):
        return self

    def next(self):
        pass

class Image(Clip):
    def draw(self, page=None):
        pass

class Sprite(Clip):
    def __init__(self):
        super(Sprite, self).__init__()
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.buffer = None

    def set_buffer(self, buf):
        self.width = 0
        self.height = 0
        if type(buf) == str:
            buf = buf.split('\n')
        self.buffer = buf
        for line in self.buffer:
            self.width = max(self.width, len(line))
        self.height = len(self.buffer)

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, page=None):
        if page == None:
            page = Page()
        cnt = 0
        buf = ''
        for line in self.buffer:
            if self.clip_y(self.y+cnt):
                continue
            leftclip = abs(min(self.x - self.left_margin, 0)) 
            if self.clip_x(self.x + len(line)):
                rightclip = self.right_margin - (self.x + len(line))
            else:
                rightclip = len(line)
            page.set_cursor(self.x, self.y+cnt)
            page.write(line[leftclip:rightclip])
            cnt += 1
        return page

class TypeSetter(Clip):
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    ACROSS = 1
    DOWN = 2

    def __init__(self):
        super(TypeSetter, self).__init__()
        self.current_font = 'larry3d'
        self.justification = self.LEFT
        self.textflow = self.ACROSS
        self.home_cursor()

    def set_font(self, font):
        self.current_font = font

    def get_font_height(self, text=None):
        if text == 'None':
            text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ff = figlet.FigletFormatter(self.current_font)
        tst = ff.format(text)
        self.font_height = len(tst)
    
    def set_textflow(self, mode):
        assert mode in (TypeSetter.ACROSS, TypeSetter.DOWN)
        self.textflow = mode

    def set_justification(self, mode):
        assert mode in (TypeSetter.LEFT, TypeSetter.RIGHT, TypeSetter.CENTER)
        self.justification = mode

    def home_cursor(self):
        self.x = self.left_margin
        self.y = self.top_margin

    def format_text(self, text, fonts, page):
        while fonts:
            font = fonts[0]
            del fonts[0]
            self.set_font(font)
            remainder = self.layout(text)
            if not remainder:
                break
        self.layout(text, page)
        return page

    def layout(self, text, page=None):
        if page == None:
            page = Page()
        ff = figlet.FigletFormatter(self.current_font)
        self.home_cursor()
        self.get_font_height(text)
        words = text.split(' ')
        lw = 0
        rw = len(words)
        spc = ' '
        while True:
            if lw == rw:
                break
            if (self.y + self.font_height) > self.height:
                break
            nrw = self.boundtext(words[lw:rw]) + lw
            sp = Sprite()
            msg = spc.join(words[lw:nrw])
            # justification
            xoff = 0
            sp.set_buffer(ff.format(msg))
            if self.justification == self.CENTER:
                if not self.clip_right_screen(self.x):
                    xoff = ((self.midline - self.left_margin) - sp.width) / 2
                else:
                    xoff = ((self.right_margin - self.midline) - sp.width) / 2
            if self.justification == self.RIGHT:
                if not self.clip_right_screen(self.x):
                    xoff = ((self.midline - self.left_margin) - sp.width)
                else:
                    xoff = ((self.right_margin - self.midline) - sp.width)
            sp.set_position(self.x + xoff, self.y)
            sp.draw(page)
            lw = nrw
            if self.textflow == TypeSetter.ACROSS:
                if not self.clip_right_screen(self.x) and \
                    self.clip_right_screen(self.right_margin):
                        # screen hop
                        self.x = self.midline + 1
                else:
                    # move down one line
                    self.x = self.left_margin
                    self.y += self.font_height
            elif self.textflow == TypeSetter.DOWN:
                if ((self.y + self.font_height*2) > self.height) and \
                    not self.clip_right_screen(self.x) and \
                    self.clip_right_screen(self.right_margin):
                        # screen hop
                        self.x = self.midline + 1
                        self.y = self.top_margin
                else:
                    # move down one line
                    if self.clip_right_screen(self.x):
                        self.x = self.midline + 1
                    else:
                        self.x = self.left_margin
                    self.y += self.font_height
        return str.join(" ", words[lw:rw])

    def boundtext(self, words):
        rw = len(words)
        ff = figlet.FigletFormatter(self.current_font)
        spc = ' '
        rw = len(words)
        lw = 0
        if not self.clip_right_screen(self.x) and \
            self.clip_right_screen(self.right_margin):
                width = self.midline - self.x
        else:
            width = self.right_margin - self.x
        while lw != rw:
            msg = spc.join(words[0:lw+1])
            msg = ff.format(msg)
            maxline = self.max_line(msg)
            if maxline > width:
                return lw
            else:
                lw += 1
        return lw

    def raw_format(self, txt, page):
        width = self.right_margin - self.left_margin
        lines = len(txt) / width
        page.set_cursor(self.left_margin, self.top_margin)
        line_offset = 0
        txt = space_re.split(txt)
        for word in txt:
            if (page.cursor[0] + len(word)) > self.right_margin:
                line_offset += 1
                page.cursor = (self.left_margin, self.top_margin + line_offset)
            msg = word + ' '
            page.write(msg)
            page.cursor = (page.cursor[0] + len(msg), page.cursor[1])
            
    def max_line(self, buffer):
        maxline = 0
        for line in buffer:
            maxline = max(len(line), maxline)
        return maxline

class Bounce(Animation):
    def __init__(self, sprite):
        super(Bounce, self).__init__()
        self.sprite = sprite
        self.sprite.x = 0
        self.sprite.y = 0
        self.vector = [1,1]

    def next(self):
        x = self.sprite.x + self.vector[0]
        spwidth = self.sprite.width
        y = self.sprite.y + self.vector[1]
        spheight = self.sprite.height
        if (x+spwidth) >= self.right_margin:
            x = self.right_margin - ((x+spwidth) - self.right_margin + spwidth)
            self.vector[0] = -self.vector[0]
        elif x < self.left_margin:
            x = -x
            self.vector[0] = -self.vector[0]
        if (y+spheight) >= self.bottom_margin:
            y = self.bottom_margin - ((y+spheight)-self.bottom_margin+spheight)
            self.vector[1] = -self.vector[1]
        elif y < self.top_margin:
            y = -y
            self.vector[1] = -self.vector[1]
        self.sprite.set_position(x, y)
        return self.sprite.draw()

class DisplayFactory(object):
    Instance = None

    def __init__(self, socket_flag=False):
        self.serial = []

    def get_instance(cls):
        if cls.Instance == None:
            cls.Instance = cls()
        return cls.Instance
    get_instance = classmethod(get_instance)

    def open(self):
        baudrate = 19200
        rtscts=0
        xonxoff=0
        left = '/dev/ttyUSB0'
        right = '/dev/ttyUSB1'
        self.serial = []
        self.serial.append(serial.Serial(left, baudrate, rtscts=0, xonxoff=0))
        self.serial.append(serial.Serial(right, baudrate, rtscts=0, xonxoff=0))
        self.left = self.serial[0]
        self.right = self.serial[1]

    def reboot(self):
        self.close()
        os.system('rmmod pl2303')
        time.sleep(.1)
        os.system('rmmod usbserial')
        time.sleep(.1)
        os.system('modprobe usbserial')
        time.sleep(.1)
        os.system('modprobe pl2303')
        cnt = 5
        while cnt:
            time.sleep(.1)
            if os.path.exists('/dev/ttyUSB1') and os.path.exists('/dev/ttyUSB0'):
                break
            cnt -= 1
        self.open()

    def cls(self):
        for s in self.serial:
            s.write(ED2 + IRMR + CKMINV)

    def close(self):
        for port in self.serial:
            port.close()
        self.serial = []
