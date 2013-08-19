import vt220
import math
import random
import figlet

class HorizontalMidlineTransition(vt220.Transition):
    def __init__(self, page1, page2):
        super(HorizontalMidlineTransition, self).__init__(page1, page2)
        self.topline = self.top_margin
        self.bottomline = self.bottom_margin
        self.top_flag = True

    def set_margins(self, margins):
        super(HorizontalMidlineTransition, self).set_margins(margins)
        self.topline = self.top_margin
        self.bottomline = self.bottom_margin
        
    def draw_next_page(self, x, y):
        return (self.top_flag and y == self.topline) or \
            (not self.top_flag and y == self.bottomline)
    
    def next(self):
        if self.bottomline < self.topline:
            raise StopIteration
        newpage = super(HorizontalMidlineTransition, self).next()
        if self.top_flag:
            self.topline += 1
        else:
            self.bottomline -= 1
        self.top_flag = not self.top_flag
        self.current_page = newpage
        return self.current_page

class VerticalMidlineTransition(vt220.Transition):
    def __init__(self, page1, page2):
        super(VerticalMidlineTransition, self).__init__(page1, page2)
        self.left_flag = True
        self.set_margins(self.get_margins())

    def set_margins(self, margins):
        super(VerticalMidlineTransition, self).set_margins(margins)
        self.leftline = self.left_margin
        self.rightline = self.right_margin

    def draw_next_page(self, x, y):
        return (self.left_flag and x == self.leftline) or \
            (not self.left_flag and x == self.rightline)

    def next(self):
        if self.rightline < self.leftline:
            raise StopIteration
        newpage = super(VerticalMidlineTransition, self).next()
        if self.left_flag:
            self.leftline += 1
        else:
            self.rightline -= 1
        self.left_flag = not self.left_flag
        self.current_page = newpage
        return self.current_page

"""
class RadarTransition(vt220.Transition):
    def __init__(self, page1, page2):
        super(RadarTransition, self).__init__(page1, page2)
        self.angle = 0
        self.set_margins(self.get_margins())

    def set_margins(self, margins):
        super(RadarTransition, self).set_margins(margins)
        self.center_x = (self.right_margin - self.left_margin) / 2
        self.center_y = (self.bottom_margin - self.top_margin) / 2
        self.radius = max(self.right_margin - self.center_x, \
                            self.bottom_margin - self.center_y) +2

    def next(self):
        if self.angle >= 360:
            raise StopIteration
        self.current_page = self.current_page.copy()
        x = self.radius * math.cos(math.radians(self.angle+90)) + self.center_x
        y = self.radius * math.sin(math.radians(self.angle+90)) + self.center_y
        self.angle += .5 
        self.line(x, y)
        return self.current_page

    def update_page(self, x, y):
        x = int(x)
        y = int(y)
        if not self.clip_xy(x, y):
            self.current_page.page[x][y] = self.next_page.page[x][y]

    def line(self, x1, y1):
        x1 = int(x1)
        y1 = int(y1)
        x0 = self.center_x
        y0 = self.center_y
        dy = y1 - y0
        dx = x1 - x0
        t = 0.5

        self.update_page(x0, y0)
        if (abs(dx) > abs(dy)):
            m = float(dy) / float(dx)
            t += y0
            if dx < 0:
                dx = -1.0
            else:
                dx = 1.0
            m *= dx
            while (x0 != x1):
                x0 += dx
                t += m
                self.update_page(x0, t)
        else:
            m = float(dx) / float(dy)
            t += x0
            if dy < 0:
                dy = -1.0
            else:
                dy = 1.0
            m *= dy;
            while (y0 != y1):
                y0 += dy
                t += m
                self.update_page(t, y0)
"""

class Temperature(vt220.Bounce):
    def __init__(self):
        import infosys
        self.infosys = infosys.get_infosys()
        self.set_margins((0, 160, 1, 25))
        weather = self.infosys.registry.Weather
        ff = figlet.FigletFormatter("fraktur")
        ff = figlet.FigletFormatter()
        temp = ff.format(weather.current_temperature)
        sp = vt220.Sprite()
        sp.set_buffer(temp)
        super(Temperature, self).__init__(sp)
        self.count = random.randint(100, 200)

    def next(self):
        if not self.count:
            raise StopIteration
        self.count -= 1
        return super(Temperature, self).next()

class StartupImage(vt220.Image):
    def draw(self, page=vt220.Page()):
        ts = vt220.TypeSetter()
        ts.set_margins((0, 160, 3, 25))
        ts.set_justification(vt220.TypeSetter.CENTER)
        ts.set_font("fraktur")
        ts.layout("VT 220", page)
        return page

class VTTVImage(vt220.Image):
    def draw(self, page=vt220.Page()):
        ts = vt220.TypeSetter()
        ts.set_justification(vt220.TypeSetter.CENTER)
        ts.set_font("caligraphy")
        ts.top_margin = 3
        ts.layout("VT TV", page)
        return page

class VTNEWSImage(vt220.Image):
    def draw(self, page=vt220.Page()):
        ts = vt220.TypeSetter()
        ts.set_justification(vt220.TypeSetter.CENTER)
        ts.set_font("fraktur")
        ts.layout("VT News", page)
        return page

"""
class EmoticonImage(vt220.Image):
    def draw(self, page=vt220.Page()):
        ts = vt220.TypeSetter()
        ts.set_justification(vt220.TypeSetter.CENTER)
        ts.set_font("doh")
        ts.layout("=)", page)
        return page
"""
