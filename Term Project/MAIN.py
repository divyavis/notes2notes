import module_manager
module_manager.review()
from cmu_112_graphics import *
from tkinter import *
import random
import calendar
import os
from musicSetup import *
from journalReading import *

#add reset user button (DONE)
#make sure create playlist isn't clickable if no entry is in (DONE)
#logout button (DONE)
#get out button after playing songs (DONE)
#loading screen (DONE)
#collaborative journal --> collaborative playlist
#add note saying if u want create another playlist run app again
#see if i can restart app if u want to make a new playlist
#indicate on calendar screen when someone has made an entry
#decorate auth website
#add instructions to help mode
#mode.showMessage not working??
#google calendar syncing?
#public spotify playlists (DONE)
#nlp
#query by spotify username (DONE)
#get public spotify playlists of followers (DONE)
#other knob direction

#one global variable used is usernamePath to make sure Spotify is authenticated properly everytime app is opened
usernamePath = f"{os.getcwd()}/spotifyUsername.txt"

#from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

#modified from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

#from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def authUser():
    username = input("Enter your Spotify username and click 'Enter' when done: ")
    print("\n")
    confirmation = input(f"You typed '{username}'. Make sure it is the exact same username associated with your Spotify account. Is '{username}' correct? Type 'yes' or 'no' and click 'Enter' when done: ")
    if confirmation.lower() == 'yes':
        userMusic = MusicSetup(username)
        writeFile(usernamePath, username)
    elif confirmation.lower() == 'no':
        print("Please try again.")
        print("\n")
        authUser()
    else:
        print("Please type 'yes' or 'no' and try authenticating again.")
        print("\n")
        authUser()

class HomeMode(Mode):
    def appStarted(mode):
        mode.buttonHeight = mode.height//20
        #mode.path = f"{os.getcwd()}/spotifyUsername.txt"
        #from https://images.unsplash.com/photo-1494232410401-ad00d5433cfa?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb
        mode.image1 = mode.loadImage('cassetteTape.jpeg')
        mode.image2 = mode.scaleImage(mode.image1, 1/3)
        mode.manila = rgbString(250, 240, 190)
        mode.darkGray = rgbString(40, 40, 40)
        mode.seafoamGreen = rgbString(160, 214, 181)

    def drawQuarterNote(mode, canvas):
        canvas.create_oval((mode.width//2)-(mode.width//36), (18*mode.height)//20, (mode.width//2)+(mode.width//36), (19*mode.height)//20, fill=mode.seafoamGreen, outline=mode.seafoamGreen)
        canvas.create_rectangle((mode.width//2-mode.width//12) + ((2*mode.width)//20), (16*mode.height)//20, (mode.width//2-mode.width//12)+((2*mode.width)//18), (23*mode.height)//25, outline=mode.seafoamGreen, fill=mode.seafoamGreen)   

    def redrawAll(mode, canvas):
        font = f'ComicSansMS {mode.buttonHeight//2} bold'
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill=mode.manila)
        canvas.create_image(mode.width//2, mode.height//4, image=ImageTk.PhotoImage(mode.image2))
        canvas.create_text(mode.width//2, (mode.height//2)+(4*mode.buttonHeight), text='Click "h" for instructions on how to use your journal', font=font, fill=mode.darkGray)
        canvas.create_rectangle(mode.width//3, ((mode.height//2)-(mode.buttonHeight//2)), (2*mode.width)//3, ((mode.height//2)+(mode.buttonHeight//2)), fill=mode.darkGray)
        canvas.create_text(mode.width//2, mode.height//2, text='See your journal', font=font, fill=mode.manila)
        if not os.path.exists(usernamePath):
            rectFill = mode.darkGray
            textFill = mode.manila
            canvas.create_rectangle(mode.width//3, ((mode.height//2+(2*mode.buttonHeight))-(mode.buttonHeight//2)), (2*mode.width)//3, ((mode.height//2+(2*mode.buttonHeight))+(mode.buttonHeight//2)), fill=rectFill, outline=rectFill)
            canvas.create_text(mode.width//2, (mode.height//2)+(2*mode.buttonHeight), text='Run app again to login to Spotify', font=f'ComicSansMS {mode.buttonHeight//3} bold', fill=textFill)
        else:
            rectFill = mode.seafoamGreen
            textFill = mode.darkGray
            canvas.create_rectangle(mode.width//3, ((mode.height//2+(2*mode.buttonHeight))-(mode.buttonHeight//2)), (2*mode.width)//3, ((mode.height//2+(2*mode.buttonHeight))+(mode.buttonHeight//2)), fill=rectFill, outline=rectFill)
            canvas.create_text(mode.width//2, (mode.height//2)+(2*mode.buttonHeight), text='Log out of Spotify', font=font, fill=textFill)
        mode.drawQuarterNote(canvas)

    def keyPressed(mode, event):
        if event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)
    
    def mousePressed(mode, event):
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= (mode.height//2)-(mode.buttonHeight//2) and event.y <= (mode.height//2)+(mode.buttonHeight//2)):
            mode.app.setActiveMode(mode.app.calendarMode)
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= (mode.height//2+(2*mode.buttonHeight))-(mode.buttonHeight//2) and event.y <= (mode.height//2+(2*mode.buttonHeight))+(mode.buttonHeight//2)):
            if os.path.exists(usernamePath):
                username = readFile(usernamePath)
                os.remove(f".cache-{username}")
                os.remove(usernamePath)
            else:
                pass
    
    def checkAuth(mode):
        username = mode.getUserInput("Enter your Spotify username")
        if username != None:
            mode.userMusic = MusicSetup(username)
            if mode.userMusic.gotAuth:
                mode.writeFile(mode.path, username)
                return None
            else:
                mode.showMessage('Authentication failed. Please try again.')
                mode.checkAuth()

class JournalMode(Mode):
    selection = (-1, -1)
    todaysDate = str(datetime.date.today())
    currYear = int(todaysDate[:4])
    currMonth = int(todaysDate[5:7])
    currDate = int(todaysDate[8:])
    monthInt = currMonth
    monthName = None
    monthRange = calendar.monthrange(currYear, monthInt)
    dateStartCol = monthRange[0]
    lastDate = monthRange[1]
    clickedDate = None
    endCol = ((dateStartCol + lastDate) % 7) - 1
    if endCol < 0:
        dateEndCol = 7
    else:
        dateEndCol = endCol
    rows = ((dateStartCol + lastDate)//7) + 1
    dateLocSet = set()
    monthlyPlaylist = False

class CalendarMode(JournalMode):
    def appStarted(mode):
        mode.margin = mode.height//8
        mode.cols = 7
        mode.manila = rgbString(250, 240, 190)
        mode.seafoamGreen = rgbString(160, 214, 181)
        mode.darkGray = rgbString(40, 40, 40)
          
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
        mode.gridWidth  = mode.width - 2*mode.margin
        mode.gridHeight = mode.height - 2*mode.margin
        mode.columnWidth = mode.gridWidth / mode.cols
        mode.rowHeight = mode.gridHeight / JournalMode.rows
        x0 = mode.margin + col * mode.columnWidth
        x1 = mode.margin + (col+1) * mode.columnWidth
        y0 = mode.margin + row * mode.rowHeight
        y1 = mode.margin + (row+1) * mode.rowHeight
        return (x0, y0, x1, y1)
    
    #modified from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def mousePressed(mode, event):
        (row, col) = mode.getCell(event.x, event.y)
        JournalMode.selection = (row, col)
        for elem in JournalMode.dateLocSet:
            if row == elem[0] and col == elem[1]:
                JournalMode.clickedDate = elem[2]
        if JournalMode.clickedDate != None:
            if JournalMode.monthInt < JournalMode.currMonth or JournalMode.clickedDate <= JournalMode.currDate:
                if row == 0 and col >= JournalMode.dateStartCol:
                    mode.app.setActiveMode(mode.app.entryMode)
                elif 0 < row < JournalMode.rows-1:
                    mode.app.setActiveMode(mode.app.entryMode)
                elif row == JournalMode.rows-1 and col <= JournalMode.dateEndCol:
                    mode.app.setActiveMode(mode.app.entryMode)
        if (event.x >= (2*mode.margin)//3 and event.x <= (4*mode.margin)//3) and (event.y >= (mode.margin + mode.gridHeight + (mode.margin//4)) and event.y <= (mode.margin + mode.gridHeight + (3*(mode.margin//4)))):
            if JournalMode.monthInt > 1:
                JournalMode.monthInt -= 1
                JournalMode.monthRange = calendar.monthrange(JournalMode.currYear, JournalMode.monthInt)
                JournalMode.dateStartCol = JournalMode.monthRange[0]
                JournalMode.lastDate = JournalMode.monthRange[1]
                JournalMode.endCol = ((JournalMode.dateStartCol + JournalMode.lastDate) % 7) - 1
                if JournalMode.endCol < 0:
                    JournalMode.dateEndCol = 7
                else:
                    JournalMode.dateEndCol = JournalMode.endCol
                JournalMode.rows = ((JournalMode.dateStartCol + JournalMode.lastDate)//7) + 1
                JournalMode.dateLocSet = set()
        if (event.x >= (mode.width-((4*mode.margin)//3)) and event.x <= (mode.width - ((2*mode.margin)//3))) and (event.y >= (mode.margin + mode.gridHeight + (mode.margin//4)) and event.y <= (mode.margin + mode.gridHeight + (3*(mode.margin//4)))):
            if JournalMode.monthInt < JournalMode.currMonth:
                JournalMode.monthInt += 1
                JournalMode.monthRange = calendar.monthrange(JournalMode.currYear, JournalMode.monthInt)
                JournalMode.dateStartCol = JournalMode.monthRange[0]
                JournalMode.lastDate = JournalMode.monthRange[1]
                JournalMode.endCol = ((JournalMode.dateStartCol + JournalMode.lastDate) % 7) - 1
                if JournalMode.endCol < 0:
                    JournalMode.dateEndCol = 7
                else:
                    JournalMode.dateEndCol = JournalMode.endCol
                JournalMode.rows = ((JournalMode.dateStartCol + JournalMode.lastDate)//7) + 1
                JournalMode.dateLocSet = set()
        if (event.x >= mode.width//2-mode.margin and event.x <= mode.width//2+mode.margin) and (event.y >= mode.height-(mode.margin//2) and event.y <= mode.height-(mode.margin//4)):
            if os.path.exists(usernamePath):
                dirName = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}"
                if not os.path.exists(dirName):
                    pass
                elif len(os.listdir(dirName)) < 2:
                    pass
                else:
                    JournalMode.monthlyPlaylist = True
                    mode.app.setActiveMode(mode.app.playlistMode)

    def redrawAll(mode, canvas):
        if JournalMode.monthInt < JournalMode.currMonth:
            mode.nextMonthButton(canvas)
        mode.drawHeader(canvas)
        for row in range(1):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                mode.drawDayText(canvas, col, x0, x1)
        for row in range(JournalMode.rows):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1, fill=mode.manila)
        mode.drawDates(canvas)
        canvas.create_text(mode.width//2, (mode.height-(3*mode.margin)//4), text='Click "b" to go back to the home screen', font=f'ComicSansMS {mode.margin//5} bold')
        mode.prevMonthButton(canvas)
        canvas.create_rectangle(mode.width//2-mode.margin, mode.height-(mode.margin//2), mode.width//2+mode.margin, mode.height-(mode.margin//4), fill=mode.seafoamGreen)
        canvas.create_text(mode.width//2, mode.height-(2*mode.margin)//5, text="Create playlist", font=f'ComicSansMS {mode.margin//6} bold')

    def prevMonthButton(mode, canvas):
        canvas.create_rectangle((2*mode.margin)//3, (mode.margin + mode.gridHeight + (mode.margin//4)), (4*mode.margin)//3, (mode.margin + mode.gridHeight + (3*(mode.margin//4))), fill=mode.seafoamGreen)
        canvas.create_text(mode.margin, (mode.margin + mode.gridHeight + (mode.margin//2)), text="<--", font=f'ComicSansMS {mode.margin//3} bold', fill=mode.darkGray)
    
    def nextMonthButton(mode, canvas):
        canvas.create_rectangle((mode.width-((4*mode.margin)//3)), (mode.margin + mode.gridHeight + (mode.margin//4)), (mode.width - ((2*mode.margin)//3)), (mode.margin + mode.gridHeight + (3*(mode.margin//4))), fill=mode.seafoamGreen)
        canvas.create_text(mode.margin+mode.gridWidth, (mode.margin + mode.gridHeight + (mode.margin//2)), text="-->", font=f'ComicSansMS {mode.margin//3} bold', fill=mode.darkGray)

    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode)

    def drawDayText(mode, canvas, col, x0, x1):
        font = f'ComicSansMS {mode.margin//8}'
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
        font = f'ComicSansMS {mode.margin//4} bold'
        if JournalMode.monthInt == 1:
            JournalMode.monthName = "January"
        elif JournalMode.monthInt == 2:
            JournalMode.monthName = "February"
        elif JournalMode.monthInt == 3:
            JournalMode.monthName = "March"
        elif JournalMode.monthInt == 4:
            JournalMode.monthName = "April"
        elif JournalMode.monthInt == 5:
            JournalMode.monthName = "May"
        elif JournalMode.monthInt == 6:
            JournalMode.monthName = "June"
        elif JournalMode.monthInt == 7:
            JournalMode.monthName = "July"
        elif JournalMode.monthInt == 8:
            JournalMode.monthName = "August"
        elif JournalMode.monthInt == 9:
            JournalMode.monthName = "September"
        elif JournalMode.monthInt == 10:
            JournalMode.monthName = "October"
        elif JournalMode.monthInt == 11:
            JournalMode.monthName = "November"
        elif JournalMode.monthInt == 12:
            JournalMode.monthName = "December"
        canvas.create_text(mode.width//2, mode.margin//2, text=f"{JournalMode.monthName} {JournalMode.currYear}", font=font)

    def drawDates(mode, canvas):
        font = f'ComicSansMS {mode.margin//8} bold'
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
        mode.path = None
        mode.manila = rgbString(250, 240, 190)
        mode.seafoamGreen = rgbString(160, 214, 181)
        mode.darkGray = rgbString(40, 40, 40)

    def mousePressed(mode, event):
        dirName = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}"
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        if (event.x >= 2*mode.margin and event.x <= (mode.width//2)-mode.margin) and (event.y >= mode.margin and event.y <= (mode.margin + mode.buttonHeight)):
            mode.root = Tk()
            mode.root.geometry(f"{mode.width}x{mode.height//2}")
            mode.root.title(f"{JournalMode.monthName} {JournalMode.clickedDate}, {JournalMode.currYear}")
            mode.textEntry = Text(mode.root)
            #sideScrollbar = Scrollbar(textEntry)
            #sideScrollbar.pack(side=RIGHT)
            #sideScrollbar.config(command=textEntry.yview)
            #textEntry.config(yscrollcommand=sideScrollbar.set)
            mode.textEntry.pack()
            loadButton = Button(mode.root, command = mode.load, width = mode.width//2, text = "Load Previous")
            loadButton.pack()
            saveButton = Button(mode.root, command = mode.save, width = mode.width//2, text = "Save")
            saveButton.pack()
            exitButton = Button(mode.root, command = mode.end, width = mode.width//2, text = "Exit")
            exitButton.pack()
        if (event.x >= (mode.width//2)+mode.margin and event.x <= mode.width-(2*mode.margin)) and (event.y >= mode.margin and event.y <= (mode.margin + mode.buttonHeight)):
            if os.path.exists(usernamePath):
                mode.app.setActiveMode(mode.app.playlistMode)

    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.calendarMode)

    #modified from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    def readFile(mode, path):
        try:
            with open(path, "rt") as f:
                return f.read()
        except:
            return None
    
    def formatTxt(mode):
        mode.path = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}/{JournalMode.monthName}{JournalMode.clickedDate}{JournalMode.currYear}.txt"
        journalEntry = mode.readFile(mode.path)
        return journalEntry

    def redrawAll(mode, canvas):
        font = f'ComicSansMS {mode.buttonHeight//2}'
        canvas.create_text(mode.width//2, mode.margin//2, text=f"{JournalMode.monthName} {JournalMode.clickedDate}, {JournalMode.currYear}", font=f'ComicSansMS {(2*mode.buttonHeight)//3} bold')
        canvas.create_rectangle(2*mode.margin, mode.margin, (mode.width//2)-mode.margin, (mode.margin + mode.buttonHeight), fill=mode.seafoamGreen)
        textCenterX1 = 2*mode.margin + (((mode.width//2)-mode.margin) - (2*mode.margin))//2
        canvas.create_text(textCenterX1, (mode.margin + mode.buttonHeight//2), text='Make/edit journal entry', font=f'ComicSansMS {mode.buttonHeight//3}')
        textCenterX2 = ((mode.width//2)+mode.margin) + ((mode.width-(2*mode.margin)) - ((mode.width//2)+mode.margin))//2
        canvas.create_rectangle((mode.width//2)+mode.margin, mode.margin, mode.width-(2*mode.margin), (mode.margin + mode.buttonHeight), fill=mode.seafoamGreen)
        canvas.create_text(textCenterX2, (mode.margin + mode.buttonHeight//2), text='Create playlist', font=f'ComicSansMS {mode.buttonHeight//3}')
        canvas.create_rectangle(mode.margin, (2*mode.margin), (mode.width-mode.margin), (mode.height-mode.margin), fill=mode.manila)
        if mode.formatTxt() != None:
            canvas.create_text(mode.margin+5, (2*mode.margin)+5, text=mode.formatTxt(), anchor= "nw", width=mode.width-((2*mode.margin)+5), font="Helvetica 15")
        canvas.create_text(mode.width//2, (mode.height-(mode.margin//2)), text='Click "b" to go back to calendar screen. Only create a playlist when journal entry is fully complete!', font=f'ComicSansMS {mode.margin//5}')

    #modified from https://stackoverflow.com/questions/14824163/how-to-get-the-input-from-the-tkinter-text-widget
    def save(mode):
        path = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}/{JournalMode.monthName}{JournalMode.clickedDate}{JournalMode.currYear}.txt"
        textInput = mode.textEntry.get("1.0", "end-1c")
        mode.writeFile(path, textInput)

    #from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    def writeFile(mode, path, contents):
        with open(path, "wt") as f:
            f.write(contents)

    def load(mode):
        path = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}/{JournalMode.monthName}{JournalMode.clickedDate}{JournalMode.currYear}.txt"
        textInput = mode.readFile(path)
        if textInput != None:
            mode.textEntry.insert(INSERT, textInput)
        else:
            mode.textEntry.insert(INSERT, "No previous entry made. Edit this and save to make a new entry.")

    def end(mode):
        mode.root.destroy()

class PlaylistMode(JournalMode):
    #ask y showMessage isn't working (Exception: 'DailyPlaylistMode' object has no attribute '_root')
    maxSongs = ""
    descrip = ""
    friendUser = ""
    publicButton = None
    monthJournal = ""
    dayJournal = ""
    myMusic = None
    friendMusic = None
    spotifyMusic = None

    def appStarted(mode):
        mode.margin = mode.height//12
        mode.manila = rgbString(250, 240, 190)
        mode.seafoamGreen = rgbString(160, 214, 181)
        mode.buttonHeight = mode.height//20
        mode.buttonWidth = mode.width//5
        mode.darkGray = rgbString(40, 40, 40)
        if JournalMode.monthlyPlaylist == True:
            dirName = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}"
            dirList = os.listdir(dirName)
            journalAnalysis = JournalSetup()
            for entry in dirList:
                smallJournal = journalAnalysis.readSingleEntry(f"{os.getcwd()}/journalEntries/{JournalMode.monthName}/{entry}")
                if smallJournal == "":
                    continue
                else:
                    PlaylistMode.monthJournal += '\n' + smallJournal
            if len(PlaylistMode.monthJournal) <= 20:
                PlaylistMode.monthJournal == ""
                JournalMode.monthlyPlaylist = False
                mode.app.setActiveMode(mode.app.calendarMode)
        else:
            journalPath = f"{os.getcwd()}/journalEntries/{JournalMode.monthName}/{JournalMode.monthName}{JournalMode.clickedDate}{JournalMode.currYear}.txt"
            if os.path.exists(journalPath):
                journalAnalysis = JournalSetup()
                PlaylistMode.dayJournal = journalAnalysis.readSingleEntry(journalPath)
                if PlaylistMode.dayJournal == "":
                    PlaylistMode.dayJournal = ""
                    mode.app.setActiveMode(mode.app.entryMode)
            else:
                mode.app.setActiveMode(mode.app.entryMode)
        if not os.path.exists(usernamePath):
            #add message about connecting spotify
            mode.app.setActiveMode(mode.app.homeMode)

    def drawHeader(mode, canvas):
        font = f'ComicSansMS {mode.margin//2} bold'
        canvas.create_text(mode.width//2, mode.margin, text="Playlist Preferences", font=font)

    def drawPublicButton(mode, buttonFill, canvas):
        canvas.create_rectangle(mode.width//2 - mode.buttonHeight - mode.buttonWidth, 4*mode.margin + mode.buttonHeight, (mode.width//2 - mode.buttonHeight), (4*mode.margin + 2*mode.buttonHeight), fill=buttonFill, outline=mode.darkGray)
        textCenterX = ((mode.width//2 - mode.buttonHeight)-mode.buttonWidth) + mode.buttonWidth//2
        canvas.create_text(textCenterX, ((4*mode.margin + mode.buttonHeight) + mode.buttonHeight//2), text="Public", font=f'ComicSansMS {mode.margin//4}')

    def drawPrivateButton(mode, buttonFill, canvas):
        canvas.create_rectangle(mode.width//2 + mode.buttonHeight, 4*mode.margin + mode.buttonHeight, mode.width//2 + mode.buttonHeight + mode.buttonWidth, (4*mode.margin + 2*mode.buttonHeight), fill=buttonFill, outline=mode.darkGray)
        textCenterX = ((mode.width//2 + mode.buttonHeight)+mode.buttonWidth) - mode.buttonWidth//2
        canvas.create_text(textCenterX, ((4*mode.margin + mode.buttonHeight) + mode.buttonHeight//2), text="Private", font=f'ComicSansMS {mode.margin//4}')

    def myMusicButton(mode, buttonFill, canvas):
        canvas.create_rectangle(mode.width//5, 2*mode.margin + mode.buttonHeight, mode.width//5 + mode.buttonWidth, (2*mode.margin + 2*mode.buttonHeight), fill=buttonFill, outline=mode.darkGray)
        canvas.create_text(mode.width//5 + mode.buttonWidth//2, (2*mode.margin + mode.buttonHeight) + mode.buttonHeight//2, text="My music", font=f'ComicSansMS {mode.margin//5}')

    def friendMusicButton(mode, buttonFill, buttonText, canvas):
        canvas.create_rectangle(mode.width//2 - mode.buttonWidth//2, 2*mode.margin + mode.buttonHeight, mode.width//2 + mode.buttonWidth//2, (2*mode.margin + 2*mode.buttonHeight), fill=buttonFill, outline=mode.darkGray)
        canvas.create_text(mode.width//2, (2*mode.margin + mode.buttonHeight) + mode.buttonHeight//2, text=buttonText, font=f'ComicSansMS {mode.margin//5}')

    def spotifyMusicButton(mode, buttonFill, canvas):
        canvas.create_rectangle(mode.width - mode.width//5 - mode.buttonWidth, 2*mode.margin + mode.buttonHeight, mode.width - mode.width//5, (2*mode.margin + 2*mode.buttonHeight), fill=buttonFill, outline=mode.darkGray)
        canvas.create_text(mode.width - mode.width//5 - mode.buttonWidth//2, (2*mode.margin + mode.buttonHeight) + mode.buttonHeight//2, text="Spotify music", font=f'ComicSansMS {mode.margin//5}')

    def redrawAll(mode, canvas):
        mode.drawHeader(canvas)
        canvas.create_text(mode.width//2, 2*mode.margin, text="Songs from: ", font=f'ComicSansMS {mode.margin//3} bold')
        mode.myMusicButton(mode.manila, canvas)
        mode.friendMusicButton(mode.manila, "Friend's music", canvas)
        mode.spotifyMusicButton(mode.manila, canvas)
        if PlaylistMode.myMusic == True and PlaylistMode.friendMusic == False and PlaylistMode.spotifyMusic == False:
            mode.myMusicButton(mode.seafoamGreen, canvas)
        elif PlaylistMode.myMusic == False and PlaylistMode.friendMusic == True and PlaylistMode.spotifyMusic == False:
            friendUsername = f'"{PlaylistMode.friendUser}"'
            mode.friendMusicButton(mode.seafoamGreen, friendUsername, canvas)
        elif PlaylistMode.myMusic == False and PlaylistMode.friendMusic == False and PlaylistMode.spotifyMusic == True:
            mode.spotifyMusicButton(mode.seafoamGreen, canvas)
        canvas.create_text(mode.width//2, 4*mode.margin, text="Playlist type:", font=f'ComicSansMS {mode.margin//3} bold')
        mode.drawPublicButton(mode.manila, canvas)
        mode.drawPrivateButton(mode.manila, canvas)
        if PlaylistMode.publicButton == True:
            mode.drawPublicButton(mode.seafoamGreen, canvas)
        elif PlaylistMode.publicButton == False:
            mode.drawPrivateButton(mode.seafoamGreen, canvas)
        canvas.create_text(mode.width//2, 6*mode.margin, text="Max number of songs in playlist (skip if no preference):", font=f'ComicSansMS {mode.margin//3} bold')
        canvas.create_rectangle(mode.width//3, 6*mode.margin+mode.buttonHeight, (2*mode.width)//3, 6*mode.margin+(2*mode.buttonHeight), fill=mode.manila)
        if (PlaylistMode.maxSongs != None and isinstance(PlaylistMode.maxSongs, str) and PlaylistMode.maxSongs.isdigit()):
            maxSongText = f"Max songs: {PlaylistMode.maxSongs}"
            canvas.create_text(mode.width//2, (6*mode.margin+mode.buttonHeight)+mode.buttonHeight//2, text=maxSongText, font=f'ComicSansMS {mode.margin//4}')
        elif (PlaylistMode.maxSongs != None and isinstance(PlaylistMode.maxSongs, int)):
            maxSongText = f"Max songs: {PlaylistMode.maxSongs}"
            canvas.create_text(mode.width//2, (6*mode.margin+mode.buttonHeight)+mode.buttonHeight//2, text=maxSongText, font=f'ComicSansMS {mode.margin//4}')
        else:
            maxSongText = "Click here to enter"
            canvas.create_text(mode.width//2, (6*mode.margin+mode.buttonHeight)+mode.buttonHeight//2, text=maxSongText, font=f'ComicSansMS {mode.margin//4}')
            PlaylistMode.maxSongs = ""
        canvas.create_text(mode.width//2, 8*mode.margin, text="Custom description (skip if no preference):", font=f'ComicSansMS {mode.margin//3} bold')
        canvas.create_rectangle(mode.margin, 8*mode.margin+mode.buttonHeight, mode.width-mode.margin, 8*mode.margin+(3*mode.buttonHeight), fill=mode.manila)
        if PlaylistMode.descrip != None and PlaylistMode.descrip != "":
            descripText = PlaylistMode.descrip
            canvas.create_text(mode.margin+5, (8*mode.margin+mode.buttonHeight)+5, width=mode.width-mode.margin-10, anchor="nw", text=descripText, font=f'Helvetica 15')
        else:
            descripText = "Click here to enter custom description"
            canvas.create_text(mode.width//2, 8*mode.margin+(2*mode.buttonHeight), text=descripText, font=f'ComicSansMS {mode.margin//4} bold')
        canvas.create_rectangle(mode.width//3, 10*mode.margin+mode.buttonHeight//2, (2*mode.width)//3, 10*mode.margin+(2*mode.buttonHeight), fill=mode.darkGray)
        canvas.create_text(mode.width//2, (10*mode.margin+mode.buttonHeight//2)+(2*mode.buttonHeight)//3, text="Create Playlist", fill=mode.seafoamGreen, font=f"ComicSansMS {mode.margin//3} bold")
        canvas.create_text(mode.width//2, mode.height - mode.margin//2, text='Click "b" to go back to the calendar screen', font=f'ComicSansMS {mode.margin//4} bold')

    def mousePressed(mode, event):
        if (event.x >= mode.width//5 and event.x <= mode.width//5 + mode.buttonWidth) and (event.y >= 2*mode.margin + mode.buttonHeight and event.y <= (2*mode.margin + 2*mode.buttonHeight)):
            PlaylistMode.myMusic = True
            PlaylistMode.friendMusic = False
            PlaylistMode.spotifyMusic = False
        if (event.x >= mode.width//2 - mode.buttonWidth//2 and event.x <= mode.width//2 + mode.buttonWidth//2) and (event.y >= 2*mode.margin + mode.buttonHeight and event.y <= (2*mode.margin + 2*mode.buttonHeight)):
            PlaylistMode.friendUser = mode.getUserInput("Enter your friend's Spotify username and press 'ok' when done")
            if PlaylistMode.friendUser == None:
                PlaylistMode.friendUser = ""
                PlaylistMode.myMusic = None
                PlaylistMode.friendMusic = None
                PlaylistMode.spotifyMusic = None
            else:
                PlaylistMode.myMusic = False
                PlaylistMode.friendMusic = True
                PlaylistMode.spotifyMusic = False
        if (event.x >= mode.width - mode.width//5 - mode.buttonWidth and event.x <= mode.width - mode.width//5) and (event.y >= 2*mode.margin + mode.buttonHeight and event.y <= (2*mode.margin + 2*mode.buttonHeight)):
            PlaylistMode.myMusic = False
            PlaylistMode.friendMusic = False
            PlaylistMode.spotifyMusic = True
        if (event.x >= mode.width//2 - mode.buttonHeight - mode.buttonWidth and event.x <= (mode.width//2 - mode.buttonHeight)) and (event.y >= 4*mode.margin + mode.buttonHeight and event.y <= (4*mode.margin + 2*mode.buttonHeight)):
            PlaylistMode.publicButton = True
        if (event.x >= mode.width//2 + mode.buttonHeight and event.x <= mode.width//2 + mode.buttonHeight + mode.buttonWidth) and (event.y >= 4*mode.margin + mode.buttonHeight and event.y <= (4*mode.margin + 2*mode.buttonHeight)):
            PlaylistMode.publicButton = False
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= 6*mode.margin+mode.buttonHeight and event.y <= 6*mode.margin+(2*mode.buttonHeight)):
            PlaylistMode.maxSongs = mode.getUserInput("Enter the max number of songs you want in your playlist (as digits)")
            if PlaylistMode.maxSongs == None:
                PlaylistMode.maxSongs = ""
        if (event.x >= mode.margin and event.x <= mode.width-mode.margin) and (event.y >= 8*mode.margin+mode.buttonHeight and event.y <= 8*mode.margin+(3*mode.buttonHeight)):
            PlaylistMode.descrip = mode.getUserInput("Enter your custom description for your playlist")
            if PlaylistMode.descrip == None:
                PlaylistMode.descrip = ""
        if (event.x >= mode.width//3 and event.x <= (2*mode.width)//3) and (event.y >= (10*mode.margin+mode.buttonHeight//2) and event.y <= 10*mode.margin+(2*mode.buttonHeight)):
            if PlaylistMode.publicButton == True or PlaylistMode.publicButton == False:
                if PlaylistMode.myMusic == True and PlaylistMode.friendMusic == False and PlaylistMode.spotifyMusic == False:
                    mode.app.setActiveMode(mode.app.loadingMode)
                elif PlaylistMode.myMusic == False and PlaylistMode.friendMusic == True and PlaylistMode.spotifyMusic == False:
                    mode.app.setActiveMode(mode.app.loadingMode)
                elif PlaylistMode.myMusic == False and PlaylistMode.friendMusic == False and PlaylistMode.spotifyMusic == True:
                    mode.app.setActiveMode(mode.app.loadingMode)

    def keyPressed(mode, event):
        if event.key == 'b':
            JournalMode.monthlyPlaylist = False
            PlaylistMode.publicButton = None
            PlaylistMode.maxSongs = ""
            PlaylistMode.descrip = ""
            PlaylistMode.monthJournal = ""
            PlaylistMode.dayJournal = ""
            mode.app.setActiveMode(mode.app.calendarMode)

class LoadingMode(PlaylistMode):
    def appStarted(mode):
        mode.seafoamGreen = rgbString(160, 214, 181)
        mode.manila = rgbString(250, 240, 190)
        mode.darkGray = rgbString(40, 40, 40)
        mode.done = False
        mode.drawn = False
        mode.buttonHeight = mode.height//20
        mode.trackIDs = []
        dirName = f"{os.getcwd()}/dogImages"
        imageList = []
        #filter on extension (png or jpg)
        filters = ['.jpg', '.png']
        for item in os.listdir(dirName):
            if any(item.endswith(f) for f in filters):
                imageList.append(item)
        imageChoice = random.choice(imageList)
        mode.image1 = mode.loadImage(f"{os.getcwd()}/dogImages/{imageChoice}")
        mode.image2 = mode.scaleImage(mode.image1, 2/3)
        mode.timerDelay = 50
    
    def timerFired(mode):
        if mode.done == False and mode.drawn == True:
            if JournalMode.monthlyPlaylist == True:
                journalAnalysis = JournalSetup()
                relevantWords = journalAnalysis.getRelevantWords(PlaylistMode.monthJournal)
            else:
                journalAnalysis = JournalSetup()
                relevantWords = journalAnalysis.getRelevantWords(PlaylistMode.dayJournal)
            username = readFile(usernamePath)
            userMusic = MusicSetup(username)
            if PlaylistMode.myMusic == True:
                userMusic.makeUserSongSet()
            elif PlaylistMode.friendMusic == True:
                userMusic.makeFriendSongSet(PlaylistMode.friendUser)
            elif PlaylistMode.spotifyMusic == True:
                userMusic.makeFriendSongSet("spotify")
            songList = userMusic.getTitleMatchedSongs(relevantWords)
            lyricDict = userMusic.getSongLyrics(songList)
            wordCounts = journalAnalysis.countWordOccurrencesInSong(lyricDict)
            songScores = journalAnalysis.scoreSongs()
            rankedSongs = journalAnalysis.rankSongs(songScores)
            if (isinstance(PlaylistMode.maxSongs, str) and PlaylistMode.maxSongs != "" and PlaylistMode.maxSongs.isdigit()):
                PlaylistMode.maxSongs = int(PlaylistMode.maxSongs)
                rankedSongs = journalAnalysis.eliminateNonMatches(rankedSongs, maxSongs=PlaylistMode.maxSongs)
            elif (isinstance(PlaylistMode.maxSongs, int)):
                rankedSongs = journalAnalysis.eliminateNonMatches(rankedSongs, maxSongs=PlaylistMode.maxSongs)
            else:
                rankedSongs = journalAnalysis.eliminateNonMatches(rankedSongs)
            mode.trackIDs = userMusic.getPlaylistTrackIDs(rankedSongs)
            if PlaylistMode.descrip != "":
                if PlaylistMode.publicButton == True or PlaylistMode.publicButton == False:
                    if JournalMode.monthlyPlaylist == False:
                        userMusic.createPlaylist(mode.trackIDs, JournalMode.monthName, day=JournalMode.clickedDate, publicP= PlaylistMode.publicButton, descrip=PlaylistMode.descrip)
                    else:
                        userMusic.createPlaylist(mode.trackIDs, JournalMode.monthName, publicP= PlaylistMode.publicButton, descrip=PlaylistMode.descrip)
                JournalMode.monthlyPlaylist = False
            else:
                keywords = journalAnalysis.getKeywordsUsed()
                keywords = (", ").join(keywords)
                if PlaylistMode.publicButton == True or PlaylistMode.publicButton == False:
                    if JournalMode.monthlyPlaylist == False:
                        userMusic.createPlaylist(mode.trackIDs, JournalMode.monthName, day=JournalMode.clickedDate, publicP= PlaylistMode.publicButton, descrip=f"keywords: {keywords}")
                    else:
                        userMusic.createPlaylist(mode.trackIDs, JournalMode.monthName, publicP= PlaylistMode.publicButton, descrip=f"keywords: {keywords}")
                JournalMode.monthlyPlaylist = False
            mode.done = True
            PlaylistMode.maxSongs = ""
            PlaylistMode.descrip = ""
            PlaylistMode.publicButton = None
            PlaylistMode.monthJournal = ""
            PlaylistMode.dayJournal = ""
            PlaylistMode.friendUser = ""
            PlaylistMode.myMusic = None
            PlaylistMode.friendMusic = None
            PlaylistMode.spotifyMusic = None
    
    def keyPressed(mode, event):
        if event.key == 'b':
            mode.done = False
            mode.drawn = False
            mode.trackIDs = []
            mode.app.setActiveMode(mode.app.calendarMode)

    def mousePressed(mode, event):
        if (event.x >= mode.width//3 and event.x <= 2*(mode.width//3)) and (event.y >= mode.height//2-(mode.buttonHeight//2) and event.y <= mode.height//2+(mode.buttonHeight//2)):
            username = readFile(usernamePath)
            userMusic = MusicSetup(username)
            userMusic.playSongs(mode.trackIDs)

    def redrawAll(mode, canvas):
        if mode.done == False:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill=mode.manila)
            canvas.create_text(mode.width//2, mode.height//5, text="LOADING PLAYLIST...", fill=mode.seafoamGreen, font=f'ComicSansMS {mode.height//20}')
            canvas.create_text(mode.width//2, mode.height//4, text="(this may take a couple of minutes)", fill=mode.seafoamGreen, font=f'ComicSansMS {mode.height//30}')
            canvas.create_image(mode.width//2, mode.height//2, image=ImageTk.PhotoImage(mode.image2))
            mode.drawn = True
        else:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill=mode.manila)
            canvas.create_text(mode.width//2, mode.height//3, text="Playlist created! Open up your Spotify app to check it out!", fill=mode.darkGray, font=f'ComicSansMS {mode.height//35}')
            canvas.create_rectangle(mode.width//3, mode.height//2-(mode.buttonHeight//2), 2*(mode.width//3), mode.height//2+(mode.buttonHeight//2), fill=mode.darkGray)
            canvas.create_text(mode.width//2, mode.height//2, text="Play Songs", font=f'ComicSansMS {mode.buttonHeight//2}', fill=mode.seafoamGreen)
            canvas.create_text(mode.width//2, mode.height-(mode.height//10), font=f'ComicSansMS {mode.height//35}', text='Click "b" to go back to the calendar screen!')

class HelpMode(Mode):
    def redrawAll(mode, canvas):
        font = 'ComicSansMS 26 bold'
        canvas.create_text(mode.width/2, 250, text='(Insert helpful message here)', font=font)
        canvas.create_text(mode.width/2, 350, text='Click "b" to go back to the home screen!', font=font)

    def keyPressed(mode, event):
        if event.key == 'b':
            mode.app.setActiveMode(mode.app.homeMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.homeMode = HomeMode()
        app.calendarMode = CalendarMode()
        app.helpMode = HelpMode()
        app.entryMode = EntryMode()
        app.playlistMode = PlaylistMode()
        app.loadingMode = LoadingMode()
        app.setActiveMode(app.homeMode)

if not os.path.exists(usernamePath):
    authUser()

app = MyModalApp(width=800, height=800)
