#!/usr/bin/python

import os
from subprocess import *

FIGLET_CLI = "/usr/bin/figlet -f %(Font)s -w %(Width)d"
FIGLISTFONT_CLI = "/usr/bin/figlist -d /usr/share/figlet/fonts"

SkipFonts = [
    '1row', '3-d', '3x5', 'alphabet', 'amcthin', 'amcun1', 'bear', 'benjamin', 
    'bigchief', 'binary', 'braced', 'bubble', 'cards', 'contessa', 
    'cybersmall', 'cygnet', 'DANC4', 'dancingfont', 'decimal', 'diamond', 
    'dietcola', 'digital', 'dosrebel', 'dwhistled', 'eftichess', 'eftifont', 
    'eftipiti', 'eftirobot', 'eftiwall', 'eftiwater', 'filter', 'flipped', 
    'fourtops', 'funface', 'funfaces', 'goofy', 'gradient', 'greek', 
    'heart_left', 'heart_right', 'hex', 'hieroglyphs', 'horizontalleft', 
    'horizontalright', 'ICL-1900', 'invita', 'isometric4', 'italic', 'ivrit', 
    'jazmine', 'jerusalem', 'katakana', 'knob', 'konto', 'lcd', 'letters', 
    'lildevil', 'linux', 'lockergnome', 'madrid', 'merlin2', 'mike', 'mini', 
    'mirror', 'mnemonic', 'morse', 'morse2', 'moscow', 'mshebrew210', 'muzzle',
    'nipples', 'octal', 'os2', 'pawp', 'pepper', 'puzzle', 'pyramid', 
    'rammstein', 'relief2', 'rot13', 'rotated', 'rounded', 'runic', 'runyc', 
    'santaclara', 'short', 'slide', 'slscript', 'smallcaps', 'smisome1', 
    'smkeyboard', 'smtengwar', 'straight', 'tanja', 'tengwar', 'term', 
    'test1', 'threepoint', 'tiles', 'tinker-toy', 'train', 'trek', 'tsalagi', 
    'tubular', 'twisted', 'twopoint', 'usaflag', 'wavy', 'weird', 'wow'
]


class FigletFormatter(object):
    def __init__(self, font="larry3d", **args):
        self.font = font
        self.fonts = []
        self.fontset = [0] * 0xff
        dct = {
            'Font':self.font,
            'Width':10000,
        }
        dct.update(args)
        self.cli = FIGLET_CLI % dct

    def format(self, message):
        message = message.encode('ascii', 'ignore')
        if self.font == 'ascii':
            return message
        cmd = self.cli.split(' ')
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)
        figout = proc.stdout
        figin = proc.stdin
        figin.write(message)
        figin.flush()
        figin.close()
        msg = figout.read()
        msg = msg.split('\n')
        figin.close()
        figout.close()
        proc.wait()
        return msg

    def get_fonts(self):
        teststr = str.join('', [chr(x) for x in range(32,127)])
        flist = os.listdir('/usr/share/figlet/fonts')
        fonts = []
        for fn in flist:
            fn = fn.split('.')
            if fn[1] in ['tlf', 'vlc', 'flf']:
                fonts.append(fn[0])
        for font in fonts:
            if font in SkipFonts:
                continue
            f = self.__class__(font)
            try:
                msg = f.format(teststr)
            except:
                import traceback
                traceback.print_exc()
            if len(msg) == 1 and not msg[0]:
                continue
            if msg:
                self.fonts.append((font, len(msg)))
        def sortf(x,y):
            if x[1] > y[1]: return -1
            if x[1] < y[1]: return 1
            return 0
        self.fonts.sort(sortf)
        return self.fonts

class AsciiFormatter(object):
    def format(self, message):
        return message
