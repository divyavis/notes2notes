from cmu_112_graphics import *
import tkinter
import random
import calendar
import os

class HomeMode(Mode):
    def appStarted(mode):
        mode.buttonHeight = mode.height//20
    
    def redrawAll(mode, canvas):
        font = f'Helvetica {mode.buttonHeight//2} bold'
        canvas.create_text(mode.width//2, mode.height//4, text='Welcome to Notes2Notes', font=font)
        canvas.create_text(mode.width//2, mode.height//3, text='Click "h" for instructions on how to use your journal', font=font)
        canvas.create_rectangle(mode.width//3, ((mode.height//2)-(mode.buttonHeight//2)), (2*mode.width)//3, ((mode.height//2)+(mode.buttonHeight//2)), fill="green")
        canvas.create_text(mode.width//2, mode.height//2, text='See your journal', font=font)

    def keyPressed(mode, event):
        if event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)
    
    def mousePressed(mode, event):
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= (mode.height//2)-(mode.buttonHeight//2) and event.y <= (mode.height//2)+(mode.buttonHeight//2)):
            mode.app.setActiveMode(mode.app.calendarMode)

class JournalMode(Mode):
    selection = (-1, -1)
    todaysDate = str(datetime.date.today())
    currYear = int(todaysDate[:4])
    currMonth = int(todaysDate[5:7])
    monthName = None
    monthRange = calendar.monthrange(currYear, currMonth)
    dateStartCol = monthRange[0]
    lastDate = monthRange[1]
    endCol = ((dateStartCol + lastDate) % 7) - 1
    if endCol < 0:
        dateEndCol = 7
    else:
        dateEndCol = endCol
    rows = ((dateStartCol + lastDate)//7) + 1
    dateLocSet = set()
    text = ''
    textList = []
    timerDelay = 100
    index = 0
    cursor = ""
    cursorColor = "white"

class CalendarMode(JournalMode):
    def appStarted(mode):
        mode.margin = mode.height//10
        mode.cols = 7
        
    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def pointInGrid(mode, x, y):
        return ((mode.margin <= x <= mode.width-mode.margin) and
            (mode.margin <= y <= mode.height-mode.margin))

    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCell(mode, x, y):
        if not mode.pointInGrid(x, y):
            return (-1, -1)
        gridWidth  = mode.width - 2*mode.margin
        gridHeight = mode.height - 2*mode.margin
        cellWidth  = gridWidth / mode.cols
        cellHeight = gridHeight / mode.rows
        row = int((y - mode.margin) / cellHeight)
        col = int((x - mode.margin) / cellWidth)
        return (row, col)

    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCellBounds(mode, row, col):
        gridWidth  = mode.width - 2*mode.margin
        gridHeight = mode.height - 2*mode.margin
        columnWidth = gridWidth / mode.cols
        rowHeight = gridHeight / JournalMode.rows
        x0 = mode.margin + col * columnWidth
        x1 = mode.margin + (col+1) * columnWidth
        y0 = mode.margin + row * rowHeight
        y1 = mode.margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)
    
    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def mousePressed(mode, event):
        (row, col) = mode.getCell(event.x, event.y)
        JournalMode.selection = (row, col)
        if row == 0 and col >= JournalMode.dateStartCol:
            mode.app.setActiveMode(mode.app.entryMode)
        elif 0 < row < JournalMode.rows-1:
            mode.app.setActiveMode(mode.app.entryMode)
        elif row == JournalMode.rows-1 and col <= JournalMode.dateEndCol:
            mode.app.setActiveMode(mode.app.entryMode)

    def redrawAll(mode, canvas):
        mode.drawHeader(canvas)
        for row in range(1):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                mode.drawDayText(canvas, col, x0, x1)
        for row in range(JournalMode.rows):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill='cyan')
        mode.drawDates(canvas)
    
    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode)

    def drawDayText(mode, canvas, col, x0, x1):
        font = f'Helvetica {mode.margin//5}'
        xDay = (x0 + x1)/2
        yDay = mode.margin - 10
        if col == 0:
            canvas.create_text(xDay, yDay, text="Monday", font=font)
        if col == 1:
            canvas.create_text(xDay, yDay, text="Tuesday", font=font)
        if col == 2:
            canvas.create_text(xDay, yDay, text="Wednesday", font=font)
        if col == 3:
            canvas.create_text(xDay, yDay, text="Thursday", font=font)
        if col == 4:
            canvas.create_text(xDay, yDay, text="Friday", font=font)
        if col == 5:
            canvas.create_text(xDay, yDay, text="Saturday", font=font)
        if col == 6:
            canvas.create_text(xDay, yDay, text="Sunday", font=font)
    
    def drawHeader(mode, canvas):
        font = f'Helvetica {mode.margin//3} bold'
        if JournalMode.currMonth == 1:
            JournalMode.monthName = "January"
        elif JournalMode.currMonth == 2:
            JournalMode.monthName = "February"
        elif JournalMode.currMonth == 3:
            JournalMode.monthName = "March"
        elif JournalMode.currMonth == 4:
            JournalMode.monthName = "April"
        elif JournalMode.currMonth == 5:
            JournalMode.monthName = "May"
        elif JournalMode.currMonth == 6:
            JournalMode.monthName = "June"
        elif JournalMode.currMonth == 7:
            JournalMode.monthName = "July"
        elif JournalMode.currMonth == 8:
            JournalMode.monthName = "August"
        elif JournalMode.currMonth == 9:
            JournalMode.monthName = "September"
        elif JournalMode.currMonth == 10:
            JournalMode.monthName = "October"
        elif JournalMode.currMonth == 11:
            JournalMode.monthName = "November"
        elif JournalMode.currMonth == 12:
            JournalMode.monthName = "December"
        canvas.create_text(mode.width//2, mode.margin//2, text=f"{JournalMode.monthName} {JournalMode.currYear}", font=font)

    def drawDates(mode, canvas):
        font = f'Helvetica {mode.margin//5}'
        i = 1
        for row in range(JournalMode.rows):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                while i <= JournalMode.lastDate:
                    if row == 0 and col == JournalMode.dateStartCol:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        JournalMode.dateLocSet.add((row, col, i))
                        i += 1
                    elif row == 0 and col > JournalMode.dateStartCol:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        JournalMode.dateLocSet.add((row, col, i))
                        i += 1
                    elif row > 0:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        JournalMode.dateLocSet.add((row, col, i))
                        i += 1
                    break

class EntryMode(JournalMode):
    def appStarted(mode):
        mode.margin = mode.height//10
        mode.buttonHeight = mode.height//20

    def redrawAll(mode, canvas):
        font = f'Helvetica {mode.buttonHeight//2}'
        (row, col) = JournalMode.selection
        date = None
        for elem in JournalMode.dateLocSet:
            if row == elem[0] and col == elem[1]:
                date = elem[2]
        canvas.create_text(mode.width//2, mode.margin//2, text=f"{JournalMode.monthName} {date}, {JournalMode.currYear}", font=f"{font} bold")
        canvas.create_rectangle(mode.width//3, mode.margin, (2*mode.width)//3, (mode.margin + mode.buttonHeight), fill="green")
        canvas.create_text(mode.width//2, (mode.margin + mode.buttonHeight//2), text='Make/edit journal entry', font=font)
    
    def mousePressed(mode, event):
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= mode.margin and event.y <= (mode.margin + mode.buttonHeight)):
            mode.app.setActiveMode(mode.app.textMode)

class TextMode(JournalMode):
    def appStarted(mode):
        window = Tk()
        width = mode.width
        height = mode.height
        window.geometry(f"{width}x{height}")
        textScreen = Text(window)
        sideScrollbar = Scrollbar(textScreen)
        window.mainloop()

class HelpMode(Mode):
    def redrawAll(mode, canvas):
        font = 'Arial 26 bold'
        canvas.create_text(mode.width/2, 250, text='(Insert helpful message here)', font=font)
        canvas.create_text(mode.width/2, 350, text='Press "b" to go back to the home screen!', font=font)

    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.homeMode = HomeMode()
        app.calendarMode = CalendarMode()
        app.helpMode = HelpMode()
        app.entryMode = EntryMode()
        app.textMode = TextMode()
        app.setActiveMode(app.homeMode)

app = MyModalApp(width=800, height=800)
