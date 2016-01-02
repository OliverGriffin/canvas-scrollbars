from tkinter import *

class VerticalScrollbar:
    def __init__(self, parent, x0, y0, x1, y1, sideButtonsHeight=8, buttonSpacing=2, numRange=100, defaultNum=0, interval=1, minScrollBtnHeight=2, colours=None, shownNumX=None, permanentText=False, invertScaleY=False, lock=False, hoverColourAlterations=0):
        self.parent = parent
        self.x0, self.x1 = x0, x1
        self.y0, self.y1 = y0, y1
        self.totalHeight = y1-y0
        if self.totalHeight < 1 or (x1-x0) < 1: raise ValueError('Object is too small!')
        self.midX, self.midY = (x1+x0)/2, (y1+y0)/2
        if 2*(sideButtonsHeight + buttonSpacing) > self.totalHeight: raise ValueError('Side button height + button spacing must not exceed total height of object.')
        else: self.sideButtonsHeight = sideButtonsHeight
        self.scaleHeight = self.totalHeight - 2*(sideButtonsHeight + buttonSpacing)
        self.scaleMax = self.midY - (self.scaleHeight/2)
        self.scaleZero = self.midY + (self.scaleHeight/2)
        self.setRange(numRange, defaultNum, interval, minScrollBtnHeight)
        self.shownNumX = shownNumX
        self.permText = permanentText
        if self.permText and self.shownNumX is None: self.shownNumX = 0
        self.invertScaleY = invertScaleY
        self.locked, self.held = False, False
        self.hoverAlt = hoverColourAlterations
        self.colours = ['#606060','#a3a3a3','#c3c3c3','#8f8f8f','#333333'] if colours is None else list(colours)
        self.colourDefaults = ('#606060','#a3a3a3','#c3c3c3','#8f8f8f','#333333') if colours is None else tuple(colours)
        self.draw(x0, y0, x1, y1, lock)
    
    def draw(self, x0, y0, x1, y1, lock):
        self.incrementBtn = self.parent.create_rectangle(x0, y0, x1, y0+self.sideButtonsHeight, fill=self.colours[1], width=1, outline=self.colours[0])
        self.scaleBack = self.parent.create_rectangle(x0, self.scaleMax, x1, self.scaleZero, fill=self.colours[3], width=1, outline=self.colours[0])
        self.decrementBtn = self.parent.create_rectangle(x0, y1-self.sideButtonsHeight, x1, y1, fill=self.colours[1], width=1, outline=self.colours[0])

        self.scaleBtn = self.parent.create_rectangle(0, 0, 0, 0, fill=self.colours[1], width=1, outline=self.colours[0])
        if self.shownNumX is not None: self.numText = self.parent.create_text(0, 0, text='', fill=self.colours[4], font=('Times New Roman', '10'))
        self.resetScale()
        if lock: self.lock()
        self.bindTags()

    def bindTags(self):
        bindList = ((self.scaleBack, self.scaleBtnClick, 0),
                    (self.scaleBack, self.scaleBtnClick, '<B1-Motion>'),
                    (self.scaleBtn, self.scaleBtnClick, 0),
                    (self.scaleBtn, self.scaleBtnClick, '<B1-Motion>'),
                    (self.numText, self.scaleBtnClick, '<B1-Motion>'),
                    (self.incrementBtn, self.incrementBtnClick, 0),
                    (self.decrementBtn, self.decrementBtnClick, 0),
                    (self.scaleBack, self.scaleBtnUnclick, 1),
                    (self.scaleBtn, self.scaleBtnUnclick, 1),
                    (self.numText, self.scaleBtnUnclick, 1),
                    (self.incrementBtn, lambda e: self.parent.itemconfig(self.incrementBtn, fill=self.colours[1]), 1),
                    (self.decrementBtn, lambda e: self.parent.itemconfig(self.decrementBtn, fill=self.colours[1]), 1))

        if self.hoverAlt is not None:
            bindList += ((self.scaleBack, self.onHover, 2),
                        (self.scaleBtn, self.onHover, 2),
                        (self.numText, self.onHover, 2),
                        (self.incrementBtn, self.onHover, 2),
                        (self.decrementBtn, self.onHover, 2),
                        (self.scaleBack, self.offHover, 3),
                        (self.scaleBtn, self.offHover, 3),
                        (self.numText, self.offHover, 3),
                        (self.incrementBtn, self.offHover, 3),
                        (self.decrementBtn, self.offHover, 3))

        for i in bindList:
            e = {0:"<ButtonPress-1>", 1:"<ButtonRelease-1>", 2:'<Enter>', 3:'<Leave>'}.get(i[2], i[2])
            self.parent.tag_bind(i[0], e, i[1])

    def setRange(self, numRange, defaultNum=None, interval=None, minHeight=None):
        d = defaultNum if defaultNum is not None else self.defaultNum
        i = interval if interval is not None else self.interval
        m = interval if minHeight is not None else self.minScrollBtnHeight
        if numRange < d: raise ValueError('To reduce graphical glitches, the number range cannot be less than the default number!(Currently {}) You may also pass in defaultNum=? to this method to redefine it.'.format(d))
        elif numRange < i: raise ValueError('Number range cannot be less than the interval!(Currently {}) You may also pass in interval=? to this method to redefine it.'.format(i))
        elif numRange < 0: raise ValueError('Number range MUST be zero or greater!')
        else:
            self.numRange = numRange
            h = self.scaleHeight/numRange
            self.buttonHeight = h if h > m else m
            self.w = self.buttonHeight/2
            if defaultNum is not None: self.setDefault(defaultNum)
            if interval is not None: self.setInterval(interval)

    def setDefault(self, defaultNum):
        if defaultNum > self.numRange: raise ValueError('Default number MUST be less than the number range! (Currently {})'.format(self.numRange))
        elif defaultNum < 0: raise ValueError('Default number MUST be zero or greater!')
        else: self.defaultNum = defaultNum

    def setInterval(self, interval):
        if interval > self.numRange: raise ValueError('Interval number MUST be less than the number range! (Currently {})'.format(self.numRange))
        elif interval < 0: raise ValueError('Interval number MUST be zero or greater!')
        else: self.interval = interval

    def setMinScrollBtnHeight(self, minHeight):
        if minHeight > self.numRange: raise ValueError('Minimum scroll button height should be less than the number range! (Currently {})'.format(self.numRange))
        elif minHeight < 1: raise ValueError('Default number MUST be one or greater!')
        else: self.minScrollBtnHeight = minHeight

    def setColours(self, clist=None, border=None, buttonface=None, buttonclick=None, bg=None, text=None, restoreDefaults=False):
        if restoreDefaults: border, buttonface, buttonclick, bg, text = self.colourDefaults
        elif clist is not None: border, buttonface, buttonclick, bg, text = clist
        if border is not None and border is not self.colours[0]:
            self.colours[0] = border
            self.parent.itemconfig(self.decrementBtn, outline=self.colours[0])
            self.parent.itemconfig(self.incrementBtn, outline=self.colours[0])
            self.parent.itemconfig(self.scaleBtn, outline=self.colours[0])
            self.parent.itemconfig(self.scaleBack, outline=self.colours[0])
        if buttonface is not None and buttonface is not self.colours[1]:
            self.colours[1] = buttonface
            self.parent.itemconfig(self.decrementBtn, fill=self.colours[1])
            self.parent.itemconfig(self.incrementBtn, fill=self.colours[1])
            self.parent.itemconfig(self.scaleBtn, fill=self.colours[1])
        if buttonclick is not None and buttonclick is not self.colours[2]: self.colours[2] = buttonclick
        if bg is not None and bg is not self.colours[3]:
            self.colours[3] = bg
            self.parent.itemconfig(self.scaleBack, fill=self.colours[3])
        if text is not None and text is not self.colours[4]:
            self.colours[4] = text
            self.parent.itemconfig(self.numText, fill=self.colours[4])

    def shade(self, alt):
        newColourList = []
        for i in range(len(self.colours)):
            rgb, newCol = [self.colours[i][1:3], self.colours[i][3:5], self.colours[i][5:]], '#'
            for c in rgb:
                d = int(c, 16) + alt #Convert from base 16 to base 10 and adds decimal alteration
                if d < 0: d = 0 #Ensures new number is within range of a two digit hexadecimal number
                elif d > 255: d = 255
                h = "%X" % d #Converts back to hexadecimal
                if d < 16: h = '0' + h #Ensures the hexadecimal consists of two digits
                newCol += h #Adds onto new hexadecimal string
            newColourList.append(newCol)
        self.setColours(clist=newColourList)

    def getNum(self, pos): return (pos-(self.scaleMax+self.w))/(self.scaleHeight-self.buttonHeight) * self.numRange
    def invertNum(self, num): return self.numRange - num if not self.invertScaleY else num
    def getValue(self): return int(self.invertNum(self.getNum(self.pos)))
    def getRange(self): return self.numRange
    def onHover(self, e):
        if not self.held and not self.locked and self.hoverAlt != 0: self.shade(self.hoverAlt)
    def offHover(self, e):
        if not self.held and not self.locked and self.hoverAlt != 0: self.setColours(restoreDefaults=True)

    def lock(self, e=None, alt=-32):
        if not self.locked:
            self.parent.itemconfig(self.scaleBtn, state='hidden')
            self.parent.itemconfig(self.numText, state='hidden')
            self.shade(alt)
            self.locked = True
        else: print('Scrollbar must be unlocked before it can be locked!')

    def unlock(self, e=None):
        if self.locked:
            self.parent.itemconfig(self.scaleBtn, state='normal')
            self.parent.itemconfig(self.numText, state='normal')
            self.setColours(self.colourDefaults)
            self.locked = False
        else: print('Scrollbar must be locked before it can be unlocked!')

    def incrementBtnClick(self, e):
        if not self.locked:
            self.parent.itemconfig(self.incrementBtn, fill=self.colours[2])
            if self.pos >= self.scaleMax+((self.interval+2)*self.w): self.pos -= (self.interval/self.numRange)*(self.scaleHeight-self.buttonHeight)
            else: self.pos = self.scaleMax + self.w
            self.updateScale()
        
    def decrementBtnClick(self, e):
        if not self.locked:
            self.parent.itemconfig(self.decrementBtn, fill=self.colours[2])
            if self.pos <= self.scaleZero-((self.interval+2)*self.w): self.pos += (self.interval/self.numRange)*(self.scaleHeight-self.buttonHeight)
            else: self.pos = self.scaleZero - self.w
            self.updateScale()

    def scaleBtnClick(self, e):
        if not self.locked:
            self.held = True
            self.parent.itemconfig(self.scaleBtn, fill=self.colours[2])
            if e.y < (self.scaleMax + self.w): self.pos = self.scaleMax + self.w
            elif e.y > (self.scaleZero - self.w): self.pos = self.scaleZero - self.w
            else: self.pos = e.y
            self.updateScale(btn=False)

    def scaleBtnUnclick(self, e):
        self.held = False
        if self.shownNumX is not None and not self.permText: self.parent.itemconfig(self.numText, text='')
        self.parent.itemconfig(self.scaleBtn, fill=self.colours[1])
        self.offHover(e)

    def updateScale(self, btn=True):
        self.parent.coords(self.scaleBtn, self.x0, self.pos-self.w, self.x1, self.pos+self.w)
        if self.shownNumX is not None and (not btn or self.permText):
            n = int(self.invertNum(self.getNum(self.pos)))
            self.parent.coords(self.numText, self.midX+self.shownNumX, self.pos)
            self.parent.itemconfig(self.numText, text=n)

    def resetScale(self, restoreColours=False):
        buttonBaseHeight = (self.scaleZero - (self.scaleHeight-self.buttonHeight)*(self.defaultNum/self.numRange)) if not self.invertScaleY else self.scaleMax + self.buttonHeight
        self.parent.coords(self.scaleBtn, self.x0, buttonBaseHeight-self.buttonHeight, self.x1, buttonBaseHeight)
        self.pos = buttonBaseHeight-self.w
        if self.shownNumX is not None:
            txt = int(self.invertNum(self.getNum(self.pos))) if self.permText else ''
            self.parent.itemconfig(self.numText, text=txt)
            self.parent.coords(self.numText, self.midX+self.shownNumX, buttonBaseHeight-(self.buttonHeight/2))
        if restoreColours: self.setColours(restoreDefaults=True)

class HorizontalScrollbar:
    def __init__(self, parent, x0, y0, x1, y1, sideButtonsWidth=8, buttonSpacing=2, numRange=100, defaultNum=0, interval=1, minScrollBtnWidth=2, colours=None, shownNumY=None, permanentText=False, invertScaleX=False, lock=False, hoverColourAlterations=0):
        self.parent = parent
        self.x0, self.x1 = x0, x1
        self.y0, self.y1 = y0, y1
        self.totalWidth = x1-x0
        if self.totalWidth < 1 or (y1-y0) < 1: raise ValueError('Object is too small!')
        self.midX, self.midY = (x1+x0)/2, (y1+y0)/2
        if 2*(sideButtonsWidth + buttonSpacing) > self.totalWidth: raise ValueError('Side button width + button spacing must not exceed total width of object.')
        else: self.sideButtonsWidth = sideButtonsWidth
        self.scaleWidth = self.totalWidth - 2*(sideButtonsWidth + buttonSpacing)
        self.scaleMax = self.midX - (self.scaleWidth/2)
        self.scaleZero = self.midX + (self.scaleWidth/2)
        self.setRange(numRange, defaultNum, interval, minScrollBtnWidth)
        self.shownNumY = shownNumY
        self.permText = permanentText
        if self.permText and self.shownNumY is None: self.shownNumY = 0
        self.invertScaleX = invertScaleX
        self.locked, self.held = False, False
        self.hoverAlt = hoverColourAlterations
        self.colours = ['#606060','#a3a3a3','#c3c3c3','#8f8f8f','#333333'] if colours is None else list(colours)
        self.colourDefaults = ('#606060','#a3a3a3','#c3c3c3','#8f8f8f','#333333') if colours is None else tuple(colours)
        self.draw(x0, y0, x1, y1, lock)

    def draw(self, x0, y0, x1, y1, lock):
        self.incrementBtn = self.parent.create_rectangle(x0, y0, x0+self.sideButtonsWidth, y1, fill=self.colours[1], width=1, outline=self.colours[0])
        self.scaleBack = self.parent.create_rectangle(self.scaleMax, y0, self.scaleZero, y1, fill=self.colours[3], width=1, outline=self.colours[0])
        self.decrementBtn = self.parent.create_rectangle(x1-self.sideButtonsWidth, y0, x1, y1, fill=self.colours[1], width=1, outline=self.colours[0])

        self.scaleBtn = self.parent.create_rectangle(0, 0, 0, 0, fill=self.colours[1], width=1, outline=self.colours[0])
        if self.shownNumY is not None: self.numText = self.parent.create_text(0, 0, text='', fill=self.colours[4], font=('Times New Roman', '10'))
        self.resetScale()
        if lock: self.lock()
        self.bindTags()

    def bindTags(self):
        bindList = ((self.scaleBack, self.scaleBtnClick, 0),
                    (self.scaleBack, self.scaleBtnClick, '<B1-Motion>'),
                    (self.scaleBtn, self.scaleBtnClick, 0),
                    (self.scaleBtn, self.scaleBtnClick, '<B1-Motion>'),
                    (self.numText, self.scaleBtnClick, '<B1-Motion>'),
                    (self.incrementBtn, self.incrementBtnClick, 0),
                    (self.decrementBtn, self.decrementBtnClick, 0),
                    (self.scaleBack, self.scaleBtnUnclick, 1),
                    (self.scaleBtn, self.scaleBtnUnclick, 1),
                    (self.numText, self.scaleBtnUnclick, 1),
                    (self.incrementBtn, lambda e: self.parent.itemconfig(self.incrementBtn, fill=self.colours[1]), 1),
                    (self.decrementBtn, lambda e: self.parent.itemconfig(self.decrementBtn, fill=self.colours[1]), 1))

        if self.hoverAlt is not None:
            bindList += ((self.scaleBack, self.onHover, 2),
                        (self.scaleBtn, self.onHover, 2),
                        (self.numText, self.onHover, 2),
                        (self.incrementBtn, self.onHover, 2),
                        (self.decrementBtn, self.onHover, 2),
                        (self.scaleBack, self.offHover, 3),
                        (self.scaleBtn, self.offHover, 3),
                        (self.numText, self.offHover, 3),
                        (self.incrementBtn, self.offHover, 3),
                        (self.decrementBtn, self.offHover, 3))

        for i in bindList:
            e = {0:"<ButtonPress-1>", 1:"<ButtonRelease-1>", 2:'<Enter>', 3:'<Leave>'}.get(i[2], i[2])
            self.parent.tag_bind(i[0], e, i[1])

    def setRange(self, numRange, defaultNum=None, interval=None, minWidth=None):
        d = defaultNum if defaultNum is not None else self.defaultNum
        i = interval if interval is not None else self.interval
        m = interval if minWidth is not None else self.minScrollBtnWidth
        if numRange < d: raise ValueError('To reduce graphical glitches, the number range cannot be less than the default number!(Currently {}) You may also pass in defaultNum=? to this method to redefine it.'.format(d))
        elif numRange < i: raise ValueError('Number range cannot be less than the interval!(Currently {}) You may also pass in interval=? to this method to redefine it.'.format(i))
        elif numRange < 0: raise ValueError('Number range MUST be zero or greater!')
        else:
            self.numRange = numRange
            w = self.scaleWidth/numRange
            self.buttonWidth = w if w > m else m
            self.w = self.buttonWidth/2
            if defaultNum is not None: self.setDefault(defaultNum)
            if interval is not None: self.setInterval(interval)

    def setDefault(self, defaultNum):
        if defaultNum > self.numRange: raise ValueError('Default number MUST be less than the number range! (Currently {})'.format(self.numRange))
        elif defaultNum < 0: raise ValueError('Default number MUST be zero or greater!')
        else: self.defaultNum = defaultNum

    def setInterval(self, interval):
        if interval > self.numRange: raise ValueError('Interval number MUST be less than the number range! (Currently {})'.format(self.numRange))
        elif interval < 0: raise ValueError('Interval number MUST be zero or greater!')
        else: self.interval = interval

    def setMinScrollBtnWidth(self, minWidth):
        if minWidth > self.numRange: raise ValueError('Minimum scroll button Width should be less than the number range! (Currently {})'.format(self.numRange))
        elif minWidth < 1: raise ValueError('Default number MUST be one or greater!')
        else: self.minScrollBtnWidth = minWidth

    def setColours(self, clist=None, border=None, buttonface=None, buttonclick=None, bg=None, text=None, restoreDefaults=False):
        if restoreDefaults: border, buttonface, buttonclick, bg, text = self.colourDefaults
        elif clist is not None: border, buttonface, buttonclick, bg, text = clist
        if border is not None and border is not self.colours[0]:
            self.colours[0] = border
            self.parent.itemconfig(self.decrementBtn, outline=self.colours[0])
            self.parent.itemconfig(self.incrementBtn, outline=self.colours[0])
            self.parent.itemconfig(self.scaleBtn, outline=self.colours[0])
            self.parent.itemconfig(self.scaleBack, outline=self.colours[0])
        if buttonface is not None and buttonface is not self.colours[1]:
            self.colours[1] = buttonface
            self.parent.itemconfig(self.decrementBtn, fill=self.colours[1])
            self.parent.itemconfig(self.incrementBtn, fill=self.colours[1])
            self.parent.itemconfig(self.scaleBtn, fill=self.colours[1])
        if buttonclick is not None and buttonclick is not self.colours[2]: self.colours[2] = buttonclick
        if bg is not None and bg is not self.colours[3]:
            self.colours[3] = bg
            self.parent.itemconfig(self.scaleBack, fill=self.colours[3])
        if text is not None and text is not self.colours[4]:
            self.colours[4] = text
            self.parent.itemconfig(self.numText, fill=self.colours[4])

    def shade(self, alt):
        newColourList = []
        for i in range(len(self.colours)):
            rgb, newCol = [self.colours[i][1:3], self.colours[i][3:5], self.colours[i][5:]], '#'
            for c in rgb:
                d = int(c, 16) + alt #Convert from base 16 to base 10 and adds decimal alteration
                if d < 0: d = 0 #Ensures new number is within range of a two digit hexadecimal number
                elif d > 255: d = 255
                h = "%X" % d #Converts back to hexadecimal
                if d < 16: h = '0' + h #Ensures the hexadecimal consists of two digits
                newCol += h #Adds onto new hexadecimal string
            newColourList.append(newCol)
        self.setColours(clist=newColourList)

    def getNum(self, pos): return (pos-(self.scaleMax+self.w))/(self.scaleWidth-self.buttonWidth) * self.numRange
    def invertNum(self, num): return self.numRange - num if self.invertScaleX else num
    def getValue(self): return int(self.invertNum(self.getNum(self.pos)))
    def getRange(self): return self.numRange
    def onHover(self, e):
        if not self.held and not self.locked and self.hoverAlt != 0: self.shade(self.hoverAlt)
    def offHover(self, e):
        if not self.held and not self.locked and self.hoverAlt != 0: self.setColours(restoreDefaults=True)

    def lock(self, e=None, alt=-32):
        if not self.locked:
            self.parent.itemconfig(self.scaleBtn, state='hidden')
            self.parent.itemconfig(self.numText, state='hidden')
            self.shade(alt)
            self.locked = True
        else: print('Scrollbar must be unlocked before it can be locked!')

    def unlock(self, e=None):
        if self.locked:
            self.parent.itemconfig(self.scaleBtn, state='normal')
            self.parent.itemconfig(self.numText, state='normal')
            self.setColours(self.colourDefaults)
            self.locked = False
        else: print('Scrollbar must be locked before it can be unlocked!')

    def incrementBtnClick(self, e):
        if not self.locked:
            self.parent.itemconfig(self.incrementBtn, fill=self.colours[2])
            if self.pos >= self.scaleMax+((self.interval+2)*self.w): self.pos -= (self.interval/self.numRange)*(self.scaleWidth-self.buttonWidth)
            else: self.pos = self.scaleMax + self.w
            self.updateScale()
        
    def decrementBtnClick(self, e):
        if not self.locked:
            self.parent.itemconfig(self.decrementBtn, fill=self.colours[2])
            if self.pos <= self.scaleZero-((self.interval+2)*self.w): self.pos += (self.interval/self.numRange)*(self.scaleWidth-self.buttonWidth)
            else: self.pos = self.scaleZero - self.w
            self.updateScale()

    def scaleBtnClick(self, e):
        if not self.locked:
            self.held = True
            self.parent.itemconfig(self.scaleBtn, fill=self.colours[2])
            if e.x < (self.scaleMax + self.w): self.pos = self.scaleMax + self.w
            elif e.x > (self.scaleZero - self.w): self.pos = self.scaleZero - self.w
            else: self.pos = e.x
            self.updateScale(btn=False)

    def scaleBtnUnclick(self, e):
        self.held = False
        if self.shownNumY is not None and not self.permText: self.parent.itemconfig(self.numText, text='')
        self.parent.itemconfig(self.scaleBtn, fill=self.colours[1])
        self.offHover(e)

    def updateScale(self, btn=True):
        self.parent.coords(self.scaleBtn, self.pos-self.w, self.y0, self.pos+self.w, self.y1)
        if self.shownNumY is not None and (not btn or self.permText):
            n = int(self.invertNum(self.getNum(self.pos)))
            self.parent.coords(self.numText, self.pos, self.midY+self.shownNumY)
            self.parent.itemconfig(self.numText, text=n)

    def resetScale(self, restoreColours=False):
        buttonBaseWidth = (self.scaleZero - (self.scaleWidth-self.buttonWidth)*(self.defaultNum/self.numRange)) if self.invertScaleX else self.scaleMax + self.buttonWidth
        self.parent.coords(self.scaleBtn, buttonBaseWidth-self.buttonWidth, self.y0, buttonBaseWidth, self.y1)
        self.pos = buttonBaseWidth-self.w
        if self.shownNumY is not None:
            txt = int(self.invertNum(self.getNum(self.pos))) if self.permText else ''
            self.parent.itemconfig(self.numText, text=txt)
            self.parent.coords(self.numText, buttonBaseWidth-(self.buttonWidth/2), self.midY+self.shownNumY)
        if restoreColours: self.setColours(restoreDefaults=True)


def callback(event):
    print("clicked at", event.x, event.y)
    s4.lock()

if(__name__=="__main__"):
    root = Tk()
    root.title("Scrollbar on a tkinter canvas")
    canvas = Canvas(root, bg='#FFFFFF', width=600, height=400, borderwidth=0, highlightthickness=0)
    canvas.pack()
    '''
    s0 = VerticalScrollbar(canvas, 100, 20, 115, 380, shownNumX=-20)
    s1 = VerticalScrollbar(canvas, 200, 20, 215, 380, numRange=10, shownNumX=20, interval=2)
    s2 = VerticalScrollbar(canvas, 300, 20, 315, 380, numRange=50, buttonSpacing=4, colours=('#A0A0A0','#E3E3E3','#F3F3F3','#BfBfBf','#777777'), sideButtonsHeight=20, shownNumX=0, permanentText=True, hoverColourAlterations=-40)
    s3 = VerticalScrollbar(canvas, 400, 20, 415, 380, numRange=500, shownNumX=20, invertScaleY=True, permanentText=True)
    s4 = VerticalScrollbar(canvas, 500, 20, 515, 380, numRange=5.0, shownNumX=20, interval=0.2, permanentText=True, lock=True)
    '''
    s0 = HorizontalScrollbar(canvas, 20, 100, 584, 115, shownNumY=-20)
    s1 = HorizontalScrollbar(canvas, 20, 150, 580, 165, numRange=10, shownNumY=20, interval=2)
    s2 = HorizontalScrollbar(canvas, 20, 200, 580, 215, numRange=50, buttonSpacing=4, colours=('#A0A0A0','#E3E3E3','#F3F3F3','#BfBfBf','#777777'), sideButtonsWidth=25, shownNumY=0, permanentText=True, hoverColourAlterations=-40)
    s3 = HorizontalScrollbar(canvas, 20, 250, 580, 265, numRange=500, shownNumY=-20, invertScaleX=True, permanentText=True)
    s4 = HorizontalScrollbar(canvas, 20, 300, 580, 315, numRange=5.0, shownNumY=20, interval=0.2, permanentText=True, lock=True)
    
    root.bind("<Button-1>", s4.unlock)
    root.bind("<Button-3>", callback)
    root.mainloop()
