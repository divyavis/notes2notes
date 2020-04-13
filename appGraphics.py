from cmu_112_graphics import *
import random
import calendar

class HomeMode(Mode):
    def redrawAll(mode, canvas):
        buttonHeight = mode.height//20
        font = f'Helvetica {buttonHeight//2} bold'
        canvas.create_text(mode.width//2, mode.height//4, text='Welcome to Notes2Notes', font=font)
        canvas.create_text(mode.width//2, mode.height//3, text='Click "h" for instructions on how to use your journal', font=font)
        canvas.create_rectangle(mode.width//3, ((mode.height//2)-(buttonHeight//2)), (2*mode.width)//3, ((mode.height//2)+(buttonHeight//2)), fill="green")
        canvas.create_text(mode.width//2, mode.height//2, text='See your journal', font=font)

    def keyPressed(mode, event):
        if event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)
    
    def mousePressed(mode, event):
        buttonHeight = mode.height//20
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= (mode.height//2)-(buttonHeight//2) and event.y <= (mode.height//2)+(buttonHeight//2)):
            mode.app.setActiveMode(mode.app.journalMode)

class JournalMode(Mode):
    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def pointInGrid(mode, x, y):
        margin = mode.height//10
        return ((margin <= x <= mode.width-margin) and
            (margin <= y <= mode.height-margin))

    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCell(mode, x, y):
        rows = 5
        cols = 7
        margin = mode.height//10
        if not mode.pointInGrid(x, y):
            return (-1, -1)
        gridWidth  = mode.width - 2*margin
        gridHeight = mode.height - 2*margin
        cellWidth  = gridWidth / cols
        cellHeight = gridHeight / rows
        row = int((y - margin) / cellHeight)
        col = int((x - margin) / cellWidth)
        return (row, col)

    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCellBounds(mode, row, col):
        rows = 5
        cols = 7
        margin = mode.height//10
        gridWidth  = mode.width - 2*margin
        gridHeight = mode.height - 2*margin
        columnWidth = gridWidth / cols
        rowHeight = gridHeight / rows
        x0 = margin + col * columnWidth
        x1 = margin + (col+1) * columnWidth
        y0 = margin + row * rowHeight
        y1 = margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)
    
    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def mousePressed(mode, event):
        selection = (-1, -1)
        (row, col) = mode.getCell(event.x, event.y)
        if selection == (row, col):
            selection = (-1, -1)
        else:
            selection = (row, col)
            mode.app.setActiveMode(mode.app.entryMode)

    def redrawAll(mode, canvas):
        rows = 5
        cols = 7
        margin = mode.height//10
        selection = (-1, -1)
        mode.drawHeader(canvas, margin)
        for row in range(1):
            for col in range(cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                mode.drawDayText(canvas, margin, col, x0, x1)
        for row in range(rows):
            for col in range(cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill='cyan')
        mode.drawDates(canvas, margin, rows, cols)
    
    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode)

    def drawDayText(mode, canvas, margin, col, x0, x1):
        font = f'Helvetica {margin//5}'
        if col == 0:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Monday", font=font)
        if col == 1:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Tuesday", font=font)
        if col == 2:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Wednesday", font=font)
        if col == 3:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Thursday", font=font)
        if col == 4:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Friday", font=font)
        if col == 5:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Saturday", font=font)
        if col == 6:
            xDay = (x0 + x1)/2
            yDay = margin - 10
            canvas.create_text(xDay, yDay, text="Sunday", font=font)
    
    def drawHeader(mode, canvas, margin):
        font = f'Helvetica {margin//3} bold'
        todaysDate = str(datetime.date.today())
        currYear = int(todaysDate[:4])
        currMonth = int(todaysDate[5:7])
        if currMonth == 1:
            monthName = "January"
        elif currMonth == 2:
            monthName = "February"
        elif currMonth == 3:
            monthName = "March"
        elif currMonth == 4:
            monthName = "April"
        elif currMonth == 5:
            monthName = "May"
        elif currMonth == 6:
            monthName = "June"
        elif currMonth == 7:
            monthName = "July"
        elif currMonth == 8:
            monthName = "August"
        elif currMonth == 9:
            monthName = "September"
        elif currMonth == 10:
            monthName = "October"
        elif currMonth == 11:
            monthName = "November"
        elif currMonth == 12:
            monthName = "December"
        canvas.create_text(mode.width//2, margin//2, text=f"{monthName} {currYear}", font=font)

    def drawDates(mode, canvas, margin, rows, cols):
        font = f'Helvetica {margin//5}'
        todaysDate = str(datetime.date.today())
        currYear = int(todaysDate[:4])
        currMonth = int(todaysDate[5:7])
        monthRange = calendar.monthrange(currYear, currMonth)
        i = 1
        for row in range(rows):
            for col in range(cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                while i <= monthRange[1]:
                    if row == 0 and col == monthRange[0]:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        i += 1
                    elif row == 0 and col > monthRange[0]:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        i += 1
                    elif row > 0:
                        canvas.create_text(x0 + 15, y0 + 15, text=f"{i}", font=font)
                        i += 1
                    break

class EntryMode(Mode):
    def redrawAll(mode, canvas):
        font = 'Arial 26 bold'
        canvas.create_text(mode.width/2, 250, text='journal entry', font=font)
    
    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.journalMode)

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
        app.journalMode = JournalMode()
        app.helpMode = HelpMode()
        app.entryMode = EntryMode()
        app.setActiveMode(app.homeMode)

app = MyModalApp(width=800, height=800)
