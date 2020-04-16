import os 

dirName = f"{os.getcwd()}/journalEntries"

if not os.path.exists(dirName):
    os.mkdir(dirName)
    
