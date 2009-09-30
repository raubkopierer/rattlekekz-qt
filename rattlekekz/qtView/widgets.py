#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui

class rattlekekzEditWidget(QtGui.QLineEdit):
    def __init__(self,text="",parent=None):
        QtGui.QLineEdit.__init__(self,text,parent)
        self.history=[]
        self.historyIndex=-1
        self.current=None

    def event(self,event):
        taken=False
        if event.type() != QtCore.QEvent.KeyPress:
            if QtGui.QLineEdit.event(self,event):
                taken=True
        elif event.key() != QtCore.Qt.Key_Tab:
            if event.key() != QtCore.Qt.Key_Backtab:
                if self.keyPressEvent(event):
                    taken=True
            else:
                taken=True
        elif event.modifiers().__eq__(QtCore.Qt.NoModifier):
            self.emit(QtCore.SIGNAL("tabPressed()"))
            taken=True
        else:
            if QtGui.QLineEdit.event(self,event):
                taken=True
        return taken

    def keyPressEvent(self,event):
        taken=False
        if event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
            taken=True
            self.returnPressed()
        elif event.matches(QtGui.QKeySequence.MoveToPreviousLine):
            taken=True
            self.scrollUp()
        elif event.matches(QtGui.QKeySequence.MoveToNextLine):
            taken=True
            self.scrollDown()
        else:
            if QtGui.QLineEdit.keyPressEvent(self,event):
                taken=True
        return taken

    def returnPressed(self):
        if self.historyIndex>0:
            self.history.pop(self.historyIndex)
        self.history.insert(0,self.text())
        self.historyIndex=-1
        self.current=None
        self.emit(QtCore.SIGNAL("returnPressed()"))

    def scrollUp(self):
        if self.historyIndex+1<len(self.history):
            if self.historyIndex==-1:
                self.current=(self.text(),self.cursorPosition())
            self.historyIndex+=1
            self.setText(self.history[self.historyIndex])
            self.setCursorPosition(self.history[self.historyIndex])

    def scrollDown(self):
        if self.historyIndex>0:
            self.historyIndex-=1
            self.setText(self.history[self.historyIndex])
            self.setCursorPosition(len(self.history[self.historyIndex]))
        elif self.current!=None:
            self.setText(self.current[0])
            self.setCursorPosition(self.current[1])
            self.current=None
            self.historyIndex=-1

class rattlekekzMainWidget(QtGui.QMainWindow):
    def closeEvent(self,event):
        self.emit(QtCore.SIGNAL("closed()"))

class rattlekekzOutputWidget(QtGui.QTextBrowser):
    def __init__(self,parent=None):
        QtGui.QTextBrowser.__init__(self,parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.setHtml(u"")

    def addSmilies(self,images):
        for i in images:
            self.document().addResource(self.document().ImageResource,i[0],i[1])

class rattlekekzFileMenu(QtGui.QMenu):
    def __init__(self,title="",parent=None):
        QtGui.QMenu.__init__(self,title,parent)
        self.addAction("Config")#,self.actionTriggered)
        self.addAction("Quit")#,self.actionTriggered)

    def actionTriggered(self,action):
        if action.text() == "Quit":
            self.emit(QtCore.SIGNAL("quit()"))