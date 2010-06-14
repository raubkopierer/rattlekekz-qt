#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui

class rattlekekzEditWidget(QtGui.QTextEdit):
    def __init__(self,text="",parent=None):
        QtGui.QTextEdit.__init__(self,text,parent)
        self.history=[]
        self.historyIndex=-1
        self.current=None
        self.setAcceptRichText(False)

    # event like event and keyPressEvent methods have to return True if they've taken the element and false if they didn't
    def event(self,event):
        if event.type() != QtCore.QEvent.KeyPress:
            if QtGui.QTextEdit.event(self,event):
                return True
        elif event.modifiers() in (QtCore.Qt.ControlModifier,QtCore.Qt.ControlModifier|QtCore.Qt.ShiftModifier):
            if QtCore.Qt.Key_Backtab != event.key() != QtCore.Qt.Key_Tab:
                if self.keyPressEvent(event):
                    return True
        elif event.key() == QtCore.Qt.Key_Tab:
            self.emit(QtCore.SIGNAL("tabPressed()"))
            return True
        elif event.key() == QtCore.Qt.Key_Backtab:
            return True
        else:
            if self.keyPressEvent(event):
                return True
        return False

    def keyPressEvent(self,event):
        if event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
            self.returnPressed()
            return True
        elif event.matches(QtGui.QKeySequence.MoveToPreviousLine):
            self.scrollUp()
            return True
        elif event.matches(QtGui.QKeySequence.MoveToNextLine):
            self.scrollDown()
            return True
        else:
            if QtGui.QTextEdit.keyPressEvent(self,event):
                return True
        return False

    def returnPressed(self):
        if self.historyIndex>0:
            self.history.pop(self.historyIndex)
        self.history.insert(0,self.toHtml())
        self.historyIndex=-1
        self.current=None
        self.emit(QtCore.SIGNAL("returnPressed()"))

    def scrollUp(self):
        if self.historyIndex+1<len(self.history):
            if self.historyIndex==-1:
                self.current=(self.toHtml(),self.textCursor().position())
            self.historyIndex+=1
            self.setText(self.history[self.historyIndex])
            cursor=self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            self.setTextCursor(cursor)

    def scrollDown(self):
        cursor=self.textCursor()
        if self.historyIndex>0:
            self.historyIndex-=1
            self.setText(self.history[self.historyIndex])
            cursor.movePosition(QtGui.QTextCursor.End)
            self.setTextCursor(cursor)
        elif self.current!=None:
            self.setText(self.current[0])
            cursor.setPosition(self.current[1])
            self.setTextCursor(cursor)
            self.current=None
            self.historyIndex=-1

class rattlekekzMainWidget(QtGui.QMainWindow):
    def closeEvent(self,event):
        self.emit(QtCore.SIGNAL("closed()"))

    def changeEvent(self,event):
        if event.type() == event.ActivationChange:
            self.emit(QtCore.SIGNAL("gotFocus()"))
        else:
            QtGui.QMainWindow.changeEvent(self,event)

class rattlekekzOutputWidget(QtGui.QTextBrowser):
    def __init__(self,parent=None):
        QtGui.QTextBrowser.__init__(self,parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.setHtml(u"")

    def addSmilies(self,images):
        for i in images:
            self.document().addResource(self.document().ImageResource,i[0],i[1])

class rattlekekzMenuBar(QtGui.QMenuBar):
    def __init__(self,parent=None):
        QtGui.QMenuBar.__init__(self,parent)
        self.fileMenu=self.addMenu("&File")
        self.fileMenu.addAction("Config")
        self.fileMenu.addAction("Quit")
        self.connect(self.fileMenu,QtCore.SIGNAL("triggered(QAction *)"),self.actionTriggered)

    def actionTriggered(self,action):
        string = action.text()
        if string == "Config":
            self.emit(QtCore.SIGNAL("config()"))
        elif string == "Quit":
            self.emit(QtCore.SIGNAL("quit()"))

class rattlekekzStatusBar(QtGui.QStatusBar):
    def __init__(self,parent=None):
        QtGui.QMenuBar.__init__(self,parent)