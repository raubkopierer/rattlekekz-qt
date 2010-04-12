#!/usr/bin/env python
# -*- coding: utf-8 -*-

copyright = """
    Copyright 2009 Christian Scharkus

    This file is part of rattlekekz-qt.

    rattlekekz-qt is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    rattlekekz-qt is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with rattlekekz-qt.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4 import QtCore,QtGui
from rattlekekz.qtView.widgets import *
import webbrowser,re

class rattlekekzBaseTab(QtGui.QWidget):
    def __init__(self,parent=None,caller=None,room=None):
        QtGui.QWidget.__init__(self,parent)
        self.room,self.parent=room,caller
        self.defaultWidget=self
        self.highlight=0

    def clickedURL(self,url):
        self.defaultWidget.setFocus()
        string = url.toString().toLower()
        if string.startsWith("button:"):
            self.parent.sendStr(self.parent.stringHandler(self.room),self.parent.stringHandler(string[7:]))
            #if string == "/joininvite":
            #    self.parent.sendStr(self.parent.stringHandler(self.room),"/joininvite")
            #elif string == "/goinvite":
            #    self.parent.sendStr(self.parent.stringHandler(self.room),"/goinvite")
        elif not url.isRelative():
            self.parent.controller.openURL(url.toString())
        else:
            self.parent.controller.openURL("http://"+url.toString())

    def gotFocus(self):
        self.highlight=0
        self.defaultWidget.setFocus()

    def fu(self):
        print "fu"

class rattlekekzLoginTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        self.Box = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight,self)
        self.Box.addWidget(QtGui.QListWidget())
        Form = QtGui.QFormLayout()
        Form.addRow("Nickname",QtGui.QLineEdit())
        Form.addRow("Password",QtGui.QLineEdit())
        Form.addRow("Rooms",QtGui.QLineEdit())
        Form.addRow(QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight))
        Form.itemAt(6).layout().addWidget(QtGui.QPushButton("&Login"))
        Form.itemAt(6).layout().addWidget(QtGui.QPushButton("&Register"))
        self.Box.addLayout(Form)
        self.roomList = self.Box.itemAt(0).widget() # QListWidget
        self.roomList.setSelectionMode(self.roomList.MultiSelection)
        self.roomList.setAlternatingRowColors(True)
        self.roomList.setFixedWidth(140)
        self.nickInput = self.Box.itemAt(1).layout().itemAt(1).widget() # QLineEdit
        self.defaultWidget=self.nickInput
        self.passInput = self.Box.itemAt(1).layout().itemAt(3).widget() # QLineEdit
        self.roomInput = self.Box.itemAt(1).layout().itemAt(5).widget() # QLineEdit
        self.loginButton = self.Box.itemAt(1).layout().itemAt(6).layout().itemAt(0).widget() # QPushButton
        self.registerButton = self.Box.itemAt(1).layout().itemAt(6).layout().itemAt(1).widget() # QPushButton
        self.passInput.setEchoMode(QtGui.QLineEdit.Password)
        self.loginButton.setDisabled(True)
        self.connect(self.roomList,QtCore.SIGNAL("itemSelectionChanged()"),self.selectRooms)
        self.connect(self.loginButton,QtCore.SIGNAL("clicked()"),self.sendLogin)
        self.connect(self.registerButton,QtCore.SIGNAL("clicked()"),self.registerNick)
        self.connect(self.nickInput,QtCore.SIGNAL("returnPressed()"),self.returnPressed)
        self.connect(self.passInput,QtCore.SIGNAL("returnPressed()"),self.returnPressed)
        self.connect(self.roomInput,QtCore.SIGNAL("returnPressed()"),self.returnPressed)
        self.prelogin=False

    def receivedPreLoginData(self,rooms,array):
        self.loginButton.setEnabled(True)
        self.prelogin=True
        self.updateRooms(rooms)

    def updateRooms(self,rooms):
        list=[]
        for i in rooms:
            list.append(i["name"]+" ("+str(i["users"])+"/"+str(i["max"])+")")
        self.roomList.clear()
        self.roomList.addItems(list)

    def sendLogin(self):
        nick,password,rooms=self.parent.stringHandler([self.nickInput.text(),self.passInput.text(),self.roomInput.text()])
        if self.prelogin:
            self.prelogin=False
            self.parent.sendLogin(nick,password,rooms)

    def selectRooms(self):
        rooms=[]
        for i in self.roomList.selectedItems():
            rooms.append(self.parent.stringHandler(i.text(),True).split(" ")[0])
            self.roomInput.setText(u",".join(rooms))

    def registerNick(self):
        self.parent.addTab("$register",rattlekekzRegTab)
        self.parent.changeTab("$register")

    def returnPressed(self):
        if self.focusWidget() != self.roomInput:
            self.focusNextChild()
        else:
            self.sendLogin()

    def grayOut(self,gray=True):
        if gray:
            map(lambda x: x.setDisabled(True),[self.loginButton,self.nickInput,self.passInput,self.roomInput,self.roomList,self.registerButton])
        else:
            map(lambda x: x.setEnabled(True),[self.loginButton,self.nickInput,self.passInput,self.roomInput,self.roomList,self.registerButton])

class rattlekekzRegTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        self.Form = QtGui.QFormLayout(self)
        self.Form.addRow("Nickname",QtGui.QLineEdit())
        self.Form.addRow("Password",QtGui.QLineEdit())
        self.Form.addRow("Password",QtGui.QLineEdit())
        self.Form.addRow("E-Mail",QtGui.QLineEdit())
        self.Form.addRow(QtGui.QPushButton("&Register"))
        self.nickInput = self.Form.itemAt(1).widget() # QLineEdit
        self.defaultWidget=self.nickInput
        self.passwordInput = self.Form.itemAt(3).widget() # QLineEdit
        self.passwordCheck = self.Form.itemAt(5).widget() # QLineEdit
        self.passwordInput.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordCheck.setEchoMode(QtGui.QLineEdit.Password)
        self.mailInput = self.Form.itemAt(7).widget() # QLineEdit
        self.registerButton = self.Form.itemAt(8).widget() # QPushButton
        self.connect(self.registerButton,QtCore.SIGNAL("clicked()"),self.registerNick)

    def registerNick(self):
        if self.passwordInput.text() == self.passwordCheck.text():
            nick,passwd,mail = map(lambda x: x.strip(),self.parent.stringHandler([self.nickInput.text(),self.passwordInput.text(),self.mailInput.text()]))
            if nick != "" != mail:
                self.parent.registerNick(nick,passwd,mail)
                print "STUB: register nick"
            else:
                print "STUB: Nick or Mail empty"
        else:
            "STUB: Passwords not matching"

class rattlekekzPrivTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(rattlekekzOutputWidget())
        self.Box0.addWidget(rattlekekzEditWidget())
        self.output=self.Box0.itemAt(0).widget() # QTextBrowser
        self.output.addSmilies(self.parent.smilie_data)
        self.input=self.Box0.itemAt(1).widget() # QTextEdit
        self.defaultWidget=self.input
        self.connect(self.input,QtCore.SIGNAL("returnPressed()"),self.sendStr)
        self.connect(self.output,QtCore.SIGNAL("anchorClicked(const QUrl&)"),self.clickedURL)

    def sendStr(self):
        input = "~n~".join(self.parent.stringHandler(self.input.toPlainText()).split("\n"))
        if input != "":
            self.parent.sendStr(self.parent.stringHandler(self.room),input)
            self.input.setText("")

    def addLine(self,msg):
        self.output.append(self.parent.stringHandler(msg,True))

    def addImage(self,id_list,qimage):
        for i in id_list:
            self.output.document().addResource(self.output.document().ImageResource,QtCore.QUrl("image://"+i+".jpg"),qimage)

    def refreshImage(self,id,qimage):
        self.output.document().addResource(self.output.document().ImageResource,QtCore.QUrl("image://"+id+".jpg"),qimage)
        v=self.output.verticalScrollBar().value()
        vmax=self.output.verticalScrollBar().maximum()
        h=self.output.horizontalScrollBar().value()
        self.output.reload()
        html = self.output.toHtml()
        self.output.setHtml(html)
        if v==vmax:
            v=self.output.verticalScrollBar().maximum()
        self.output.verticalScrollBar().setValue(v)
        self.output.horizontalScrollBar().setValue(h)

class rattlekekzMsgTab(rattlekekzPrivTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(QtGui.QLineEdit())
        self.Box0.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal))
        self.Box0.itemAt(1).widget().addWidget(rattlekekzOutputWidget())
        self.Box0.itemAt(1).widget().addWidget(QtGui.QListWidget())
        self.Box0.addWidget(rattlekekzEditWidget())
        self.Box0.itemAt(1).widget().setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.userList = self.Box0.itemAt(1).widget().widget(1)
        self.userList.setFixedWidth(140)
        self.topicLine=self.Box0.itemAt(0).widget() # QLineEdit
        self.output=self.Box0.itemAt(1).widget().widget(0) # QTextBrowser
        self.output.addSmilies(self.parent.smilie_data)
        self.input=self.Box0.itemAt(2).widget() # QTextEdit
        self.input.setFixedHeight(QtGui.QFontInfo(self.input.currentFont()).pixelSize()*6)
        self.defaultWidget=self.input
        self.connect(self.input,QtCore.SIGNAL("tabPressed()"),self.complete)
        self.connect(self.input,QtCore.SIGNAL("returnPressed()"),self.sendStr)
        self.connect(self.topicLine,QtCore.SIGNAL("returnPressed()"),self.setTopic)
        self.connect(self.output,QtCore.SIGNAL("anchorClicked(const QUrl&)"),self.clickedURL)
        self.connect(self.userList,QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWhois)

    def openWhois(self,item):
        string=self.parent.stringHandler(item.text())
        if not string.startswith("("):
            self.parent.sendStr(self.parent.stringHandler(self.room),"/w "+string)
        else:
            self.parent.sendStr(self.parent.stringHandler(self.room),"/w "+string[1:-1])

    def listUser(self,users,color=True):
        """takes a list of users and updates the Userlist of the room"""
        self.completion=[]
        new=[]
        self.userList.clear()
        if color:
            for i in users:
                self.completion.append(i[0])
                if i[2] == 'normal':
                    self.color='normal'
                elif i[2] == 'special':
                    self.color='green'
                elif i[2] == 'chanop':
                    self.color='blue'
                elif i[2] == 'chatop':
                    self.color='orange'
                elif i[2] == 'admin':
                    self.color='red'
                if i[1] == True:
                    self.color=self.color+'away'
                    item=QtGui.QListWidgetItem(self.parent.stringHandler("("+i[0]+")",True))
                else:
                    item=QtGui.QListWidgetItem(self.parent.stringHandler(i[0],True))
                item.setTextColor(QtGui.QColor(int(self.parent.colors[self.color][:2],16),int(self.parent.colors[self.color][2:4],16),int(self.parent.colors[self.color][4:],16)))
                new.append(item)
            for i in new:
                self.userList.addItem(i)
        else:
            for i in users:
                self.completion.append(i[0])
                if i[2] in 'x':
                    self.color=' '
                elif i[2] in 's':
                    self.color='~'
                elif i[2] in 'c':
                    self.color='$'
                elif i[2] in 'o':
                    self.color='@'
                elif i[2] in 'a':
                    self.color='%'
                if i[1]:
                    new.append(self.color+"("+i[0]+")")
                else:
                    new.append(self.color+i[0])
            new = self.parent.stringHandler(new,True)
            self.userList.addItems(new)
        self.completion=self.parent.stringHandler(self.completion,True)
        #self.input.completer().model().setStringList(self.completion)

    def complete(self):
        at=False
        cursor=self.input.textCursor()
        input = self.parent.stringHandler(self.input.toPlainText(),True)
        input,crap=input[:cursor.position()],input[cursor.position():]
        input=re.match(r"((?:\n|.)*?)(\s?)(\S+?$)",input)
        if input:
            sep = input.group(2)
            nick = input.group(3).lower()
            input = [input.group(1)]
            if nick.startswith("@"):
                nick = nick[1:]
                at=True
            solutions=[]
            newInput = nick
            if nick != "":
                for i in self.completion:
                    if nick in i[:len(nick)].lower():
                        solutions.append(i)
                if len(solutions) != 0 and len(solutions) != 1:
                    solutions.sort(key=lambda x: len(x))
                    for x in range(len(solutions[0])):
                        if solutions[0][x] != solutions[1][x]:
                            break
                        else:
                            newInput=solutions[0][:x+1]
                    if at:
                        newInput=u"@"+newInput
                    input.append(newInput)
                    self.input.setText(self.parent.stringHandler(sep.join(input)+crap,True))
                    cursor.setPosition(len(self.input.toPlainText())-len(crap))
                    self.input.setTextCursor(cursor)
                    self.addLine(u" ".join(solutions))
                elif len(solutions) is not 0:
                    if at:
                        solutions[0]=u"@"+solutions[0]
                    input.append(solutions[0])
                    if len(input) is not 1:
                        self.input.setText(sep.join(input)+u" "+crap)
                    else:
                        self.input.setText(sep.join(input)+u", "+crap)
                    cursor.setPosition(len(self.input.toPlainText())-len(crap))
                    self.input.setTextCursor(cursor)

    def setTopic(self):
        if self.topicLine.hasAcceptableInput():
            input = self.parent.stringHandler(self.topicLine.text())
            self.parent.sendStr(self.parent.stringHandler(self.room),"/topic "+input)

    def newTopic(self,topic):
        self.topicLine.setText(self.parent.stringHandler(topic,True))
        self.addLine(self.parent.stringHandler("Topic: "+"".join(self.parent.deparse(topic)),True))

class rattlekekzMailTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(QtGui.QSplitter(QtCore.Qt.Horizontal))
        self.Box0.itemAt(0).widget().addWidget(QtGui.QListWidget())
        self.Box0.itemAt(0).widget().addWidget(QtGui.QTextBrowser())
        Box1 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box1.addWidget(QtGui.QPushButton("re&fresh"))
        Box1.addWidget(QtGui.QPushButton("&Response"))
        Box1.addWidget(QtGui.QPushButton("&new Mail"))
        Box1.addWidget(QtGui.QPushButton("delete Mail"))
        Box1.addWidget(QtGui.QPushButton("delete readed Mails"))
        self.Box0.addLayout(Box1)
        self.mailList = self.Box0.itemAt(0).widget().widget(0)
        self.defaultWidget=self.mailList
        #self.mailList.setFixedWidth(140)
        self.mailOutput = self.Box0.itemAt(0).widget().widget(1)
        self.refreshButton=self.Box0.itemAt(1).layout().itemAt(0).widget()
        self.responseButton=self.Box0.itemAt(1).layout().itemAt(1).widget()
        self.newButton=self.Box0.itemAt(1).layout().itemAt(2).widget()
        self.deleteButton=self.Box0.itemAt(1).layout().itemAt(3).widget()
        self.readedButton=self.Box0.itemAt(1).layout().itemAt(4).widget()
        self.connect(self.refreshButton,QtCore.SIGNAL("clicked()"),self.parent.refreshMaillist)
        self.connect(self.responseButton,QtCore.SIGNAL("clicked()"),self.respondMail)
        self.connect(self.newButton,QtCore.SIGNAL("clicked()"),self.newMail)
        self.connect(self.deleteButton,QtCore.SIGNAL("clicked()"),self.delMail)
        self.connect(self.readedButton,QtCore.SIGNAL("clicked()"),self.delReadedMail)
        self.connect(self.mailList,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),self.getMail)

    def receivedMails(self,userid,mailcount,mails):
        post=[]
        for i in mails:
            if i["unread"]==1:
                post.append(self.parent.stringHandler(str(i["index"])+".: von "+i["from"]+", um "+i["date"]+" (unread): \n"+i["stub"],True))
            else:
                post.append(self.parent.stringHandler(str(i["index"])+".: von "+i["from"]+", um "+i["date"]+": \n"+i["stub"],True))
        self.mailList.clear()
        self.mailList.addItems(post)

    def getMail(self,widget):
        index = widget.listWidget().row(widget)
        self.parent.getMail(index)
        print "get mail",index

    def newMail(self):
        self.parent.openMailEditTab()

    def respondMail(self):
        self.parent.status.showMessage("STUB: implement response")

    def delMail(self):
        self.parent.status.showMessage("STUB: implement delete")

    def delReadedMail(self):
        self.parent.status.showMessage("STUB: implement delete")

    def addLine(self,msg):
        self.mailOutput.setHtml(u"")
        print msg
        self.mailOutput.append("".join(self.parent.stringHandler(msg,True)))

class rattlekekzMailEditTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        Box = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        Box.addLayout(QtGui.QFormLayout())
        Box.itemAt(0).layout().addRow("mail to: ",QtGui.QLineEdit())
        Box.addWidget(QtGui.QTextEdit())
        Box.addWidget(QtGui.QPushButton("&Send"))
        self.receiver=Box.itemAt(0).layout().itemAt(1).widget()
        self.input=Box.itemAt(1).widget()
        self.input.setAcceptRichText(False)
        self.send=Box.itemAt(2).widget()
        self.defaultWidget=self.receiver
        self.connect(self.send,QtCore.SIGNAL("clicked()"),self.sendMail)

    def setContent(self,receiver="",content=""):
        self.receiver.setText(receiver)
        self.input.setText(content)

    def responseMail(self,mail):
        self.parent.status.showMessage("STUB: implement response")

    def sendMail(self):
        receiver,input=self.parent.stringHandler([self.receiver.text(),self.input.toPlainText()])
        input=input.replace("\n","~n~")
        self.parent.sendMail(receiver,input)

    def addImage(self,id_list,qimage):
        for i in id_list:
            self.output.document().addResource(self.document().ImageResource,QtCore.QUrl("image://"+i+".jpg"),qimage)

    def refreshImage(self,id,qimage):
        self.output.document().addResource(self.output.document().ImageResource,QtCore.QUrl("image://"+id+".jpg"),qimage)
        v=self.output.verticalScrollBar().value()
        vmax=self.output.verticalScrollBar().maximum()
        h=self.output.horizontalScrollBar().value()
        self.output.reload()
        html = self.output.toHtml()
        self.output.setHtml(html)
        if v==vmax:
            v=self.output.verticalScrollBar().maximum()
        self.output.verticalScrollBar().setValue(v)
        self.output.horizontalScrollBar().setValue(h)

class rattlekekzInfoTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        Box = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        Box.addWidget(rattlekekzOutputWidget())
        self.output = Box.itemAt(0).widget()
        self.defaultWidget=self.output
        self.output.setHtml("")
        self.output.setReadOnly(True)
        self.connect(self.output,QtCore.SIGNAL("anchorClicked(const QUrl&)"),self.clickedURL)

    def addWhois(self):
        self.output.setHtml("")

    def addImage(self,id_list,qimage):
        for id in id_list:
            self.output.document().addResource(self.output.document().ImageResource,QtCore.QUrl("image://"+id+".jpg"),qimage)

    def refreshImage(self,id,qimage):
        self.output.document().addResource(self.output.document().ImageResource,QtCore.QUrl("image://"+id+".jpg"),qimage)
        v=self.output.verticalScrollBar().value()
        vmax=self.output.verticalScrollBar().maximum()
        h=self.output.horizontalScrollBar().value()
        self.output.reload()
        html = self.output.toHtml()
        self.output.setHtml(html)
        if v==vmax:
            v=self.output.verticalScrollBar().maximum()
        self.output.verticalScrollBar().setValue(v)
        self.output.horizontalScrollBar().setValue(h)

    def addLine(self,msg):
        self.output.append(self.parent.stringHandler(msg,True))

class rattlekekzSecureTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)

class rattlekekzWhoisEditTab(rattlekekzBaseTab):
    def __init__(self,parent=None,caller=None,room=None):
        rattlekekzBaseTab.__init__(self,parent,caller,room)
        Box = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        Box.addLayout(QtGui.QFormLayout())
        for i in ["password","new password","new password 2x","name","location","homepage","hobbies"]:
            Box.itemAt(0).layout().addRow(i+": ",QtGui.QLineEdit())
        Box.addWidget(QtGui.QLabel("signature:"))
        Box.addWidget(QtGui.QTextEdit())
        Box.addLayout(QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight))
        Box.itemAt(3).layout().addWidget(QtGui.QPushButton("&update"))
        Box.itemAt(3).layout().addWidget(QtGui.QPushButton("cha&nge password"))
        self.password=Box.itemAt(0).layout().itemAt(1).widget()
        self.newpassword1=Box.itemAt(0).layout().itemAt(3).widget()
        self.newpassword2=Box.itemAt(0).layout().itemAt(5).widget()
        self.name=Box.itemAt(0).layout().itemAt(7).widget()
        self.location=Box.itemAt(0).layout().itemAt(9).widget()
        self.homepage=Box.itemAt(0).layout().itemAt(11).widget()
        self.hobbies=Box.itemAt(0).layout().itemAt(13).widget()
        self.signature=Box.itemAt(2).widget()
        self.updateButton=Box.itemAt(3).layout().itemAt(0).widget()
        self.passwordButton=Box.itemAt(3).layout().itemAt(1).widget()
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.newpassword1.setEchoMode(QtGui.QLineEdit.Password)
        self.newpassword2.setEchoMode(QtGui.QLineEdit.Password)
        self.connect(self.updateButton,QtCore.SIGNAL("clicked()"),self.updateProfile)
        self.connect(self.passwordButton,QtCore.SIGNAL("clicked()"),self.updatePassword)

    def receivedProfile(self,name,location,homepage,hobbies,signature):
        self.name.setText(self.parent.stringHandler(name,True))
        self.location.setText(self.parent.stringHandler(location,True))
        self.homepage.setText(self.parent.stringHandler(homepage,True))
        self.hobbies.setText(self.parent.stringHandler(hobbies,True))
        self.signature.setText(self.parent.stringHandler(signature,True))

    def updateProfile(self):
        password=self.parent.stringHandler(self.password.text())
        name=self.parent.stringHandler(self.name.text())
        location=self.parent.stringHandler(self.location.text())
        homepage=self.parent.stringHandler(self.homepage.text())
        hobbies=self.parent.stringHandler(self.hobbies.text())
        signature=self.parent.stringHandler(self.signature.toPlainText())
        self.parent.updateProfile(name,location,homepage,hobbies,signature,password)

    def updatePassword(self):
        password=self.parent.stringHandler(self.password.text())
        newpassword1=self.parent.stringHandler(self.newpassword1.text())
        newpassword2=self.parent.stringHandler(self.newpassword1.text())
        if newpassword1 == newpassword2:
            print "sending passwords"
            self.parent.changePassword(password,newpassword1)
        else:
            self.parent.status.showMessage("new passwords don't match!")
