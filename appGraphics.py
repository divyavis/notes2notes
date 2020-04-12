from cmu_112_graphics import *
import random

class HomeMode(Mode):
    def redrawAll(mode, canvas):
        buttonHeight = mode.height/20
        font = f'Helvetica {int(buttonHeight/2)} bold'
        canvas.create_text(mode.width/2, mode.height/4, text='Welcome to Notes2Notes', font=font)
        canvas.create_text(mode.width/2, mode.height/3, text='Click "h" for instructions on how to use your journal', font=font)
        canvas.create_rectangle(mode.width/3, ((mode.height/2)-(buttonHeight/2)), (2*mode.width)/3, ((mode.height/2)+(buttonHeight/2)), fill="green")
        canvas.create_text(mode.width/2, mode.height/2, text='See your journal', font=font)

    def keyPressed(mode, event):
        if event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)
    
    def mousePressed(mode, event):
        buttonHeight = mode.height/20
        if (event.x >= mode.width/3 and event.x <= (2*mode.width)/3) and (event.y >= (mode.height/2)-(buttonHeight/2) and event.y <= (mode.height/2)+(buttonHeight/2)):
            mode.app.setActiveMode(mode.app.journalMode)

class JournalMode(Mode):
    def pointInGrid(mode, x, y):
        margin = mode.height/20
        return ((margin <= x <= mode.width-margin) and
            (margin <= y <= mode.height-margin))

    def getCell(mode, x, y):
        rows = 7
        cols = 5
        margin = mode.height/20
        if not mode.pointInGrid(x, y):
            return (-1, -1)
        gridWidth  = mode.width - 2*margin
        gridHeight = mode.height - 2*margin
        cellWidth  = gridWidth / cols
        cellHeight = gridHeight / rows
        row = int((y - margin) / cellHeight)
        col = int((x - margin) / cellWidth)
        return (row, col)

    def getCellBounds(mode, row, col):
        rows = 7
        cols = 5
        margin = mode.height/20
        gridWidth  = mode.width - 2*margin
        gridHeight = mode.height - 2*margin
        columnWidth = gridWidth / cols
        rowHeight = gridHeight / rows
        x0 = margin + col * columnWidth
        x1 = margin + (col+1) * columnWidth
        y0 = margin + row * rowHeight
        y1 = margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)
    
    def mousePressed(mode, event):
        selection = (-1, -1)
        (row, col) = mode.getCell(event.x, event.y)
        if selection == (row, col):
            selection = (-1, -1)
        else:
            selection = (row, col)
            mode.app.setActiveMode(mode.app.journalEntryMode)

    def redrawAll(mode, canvas):
        rows = 7
        cols = 5
        selection = (-1, -1)
        for row in range(rows):
            for col in range(cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill='cyan')
    
    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode) 

class JournalEntryMode(Mode):
    def redrawAll(mode, canvas):
        font = 'Arial 26 bold'
        canvas.create_text(mode.width/2, 250, text='journal entry', font=font)

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
        app.journalEntryMode = JournalEntryMode()
        app.setActiveMode(app.homeMode)

app = MyModalApp(width=800, height=800)