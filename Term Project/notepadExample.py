from tkinter import *
from tkinter import ttk
import re

class App(object):
    def __init__(self):
        self.root = Tk()
        self.root.title = "Notepad Application"
    
        self.MyTextWidget = Text(self.root)
        self.MyTextWidget.pack()
        
        self.openFile()
      
        self.root.mainloop()
     
    def openFile(self):
        myFile = open("myTextFile.txt")
        self.MyTextWidget.delete(0.0, END)
        self.MyTextWidget.insert(0.0, myFile.read())
        myFile.close()
    
App()