    def appStarted(mode):
        mode.text = ''
        mode.textList = []
        mode.timerDelay = 100
        mode.margin = mode.height//10
        mode.index = 0
        mode.cursor = ""
        mode.cursorColor = "white"

    def timerFired(mode):
        if mode.cursorColor == "white":
            mode.cursorColor = "black"
        else:
            mode.cursorColor = "white"

    def keyPressed(mode, event):
        if event.key == "Backspace" or event.key == 'Delete':
            if mode.textList != []:
                mode.index -= 1
                mode.textList.pop(mode.index)
        elif len(mode.textList) >= 1 and len(mode.textList) % 50 == 0:
            mode.textList.insert(mode.index, '\n')
            mode.index += 1
        elif event.key == "Enter" or event.key == "Return":
            mode.textList.insert(mode.index, '\n')
            mode.index += 1
        elif event.key == "Space":
            mode.textList.insert(mode.index, " ")
            mode.index += 1
        elif event.key == "Left":
            mode.index -= 1
        elif event.key == "Right":
            mode.index += 1
        else:
            mode.textList.insert(mode.index, event.key)
            mode.index += 1
        mode.cursor = (mode.index*" ") + "I"
        mode.text = ''.join(mode.textList)

    def helper(mode, textList):
        #take in a list and it iterates through list until it finds cursor
        #for loop that does range with len find index where to split
        #returns a tuple with both lists
        #in redraw all join first then last draw cursor in between

    def redrawAll(mode, canvas):
        canvas.create_rectangle(mode.margin, mode.margin, (2*mode.width)//3, mode.height-mode.margin)
        canvas.create_text(mode.margin, mode.margin, text = mode.text, anchor = 'nw', font = "Times 15")
        canvas.create_text(mode.margin, mode.margin, text = mode.cursor, anchor = 'nw', font = "Times 15", fill=mode.cursorColor)sorColor)