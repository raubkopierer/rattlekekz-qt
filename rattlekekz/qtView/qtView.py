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

revision = "Git has no revisions 1"

import sys
from re import search
import re,urllib

#twisted/qt
from PyQt4 import QtGui,QtCore
import qt4reactor
app = QtGui.QApplication(sys.argv)
qt4reactor.install()
from twisted.internet import reactor
from twisted.web.client import getPage

from rattlekekz.core.pluginmanager import iterator
from rattlekekz.qtView.tabs import *
from rattlekekz.qtView.tabmanagement import TabManager

rev=search("\d+",revision).group()

class View(TabManager,iterator):
    def __init__(self,controller):
        self.name,self.version="rattlekekz","0.1 Nullpointer Exception"  # Diese Variablen werden vom View abgefragt
        self.controller=controller
        self.revision=rev
        TabManager.__init__(self)
        self.spaces=re.compile("  {1,}")
        self.urls=re.compile("(?P<url>(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?)",re.I)
        self.blubb=lambda x:chr(ord(x)-43)
        self.plugins={}
        self._setup()
        self.addTab("$login",rattlekekzLoginTab)
        self.changeTab("$login")
        self.main.show()
        self.smilies={"s6":":-)",
                 "s4":":-(",
                 "s1":":-/",
                 "s8":"X-O",
                 "s7":"(-:",
                 "s9":"?-|",
                 "s10":"X-|",
                 "s11":"8-)",
                 "s2":":-D",
                 "s3":":-P",
                 "s5":";-)",
                 "sxmas":"o:)",
                 "s12":":-E",
                 "s13":":-G"}
        self.colors={"red":"FF0000",
                     "blue":"020285",
                     "green":"015401",
                     "gray":"696969",
                     "cyan":"00FFFF",
                     "magenta":"FF00FF",
                     "orange":"FFA500",
                     "pink":"FFC0CB",
                     "yellow":"FFFF00",
                     "normal":"000000",
                     "normalaway":"696969",
                     "greenaway":"215421",
                     "blueaway":"222285",
                     "yellowaway":"FFA500",
                     "redaway":"FF2020"}

    def _setup(self):
        class mainWin(QtGui.QMainWindow):
            def closeEvent(self,event):
                self.emit(QtCore.SIGNAL("closed()"))
        self.main=mainWin()
        self.main.setWindowTitle(self.name)
        self.menu=self.main.menuBar()
        self.menu.addMenu("&File") # TODO: add shit
        self.main.setCentralWidget(QtGui.QTabWidget())
        self.tabs=self.main.centralWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMinimumSize(400,350)
        self.main.connect(self.tabs,QtCore.SIGNAL("tabCloseRequested(int)"),self.closeTab)
        self.main.connect(self.main,QtCore.SIGNAL("closed()"),self.quit)

    def closeTab(self,integer):
        if isinstance(self.tabs.widget(integer),rattlekekzMsgTab):
            self.sendStr(self.stringHandler(self.tabs.tabText(integer)),"/part")
        else:
            self.tabs.removeTab(integer)
            del self.lookupRooms[0]

    def quit(self):
        self.iterPlugins('quitConnection')
        reactor.stop()
        sys.exit()

    def deparse(self,msg):
        text,format=self.controller.decode(msg)
        msg=[]
        for i in range(len(text)):
            text[i] = self.escapeText(text[i])
            if format[i] == "newline":
                msg.append("<br>")
                continue
            if format[i] == "hline":
                msg.append("<hr>")
                continue
            if format[i] == "imageurl":
                try:
                    image=urllib.urlretrieve(text[i])[0]
                    msg.append("<img src='"+self.stringHandler(image)+"'>")
                except:
                    msg.append(self.escapeText("<image url is invalid>"))
                #image=urllib2.urlopen(text[i]).read()
                #for y in range(self.tabs.count()):
                #    if isinstance(self.tabs.widget(y),rattlekekzPrivTab):
                #        self.tabs.widget(y).output.document().addResource(QtGui.QTextDocument.ImageResource,QtGui.QUrl("mydata://"+self.stringHandler(text[i])),QVariant(image))
                #        msg.append(("<img src='"+"mydata://"+self.stringHandler(text[i])+"'>"))
                continue
            if len(format[i]) > 1:
                if format[i][0] == "ownnick":
                    if not "green" in format[i][1]:
                        color = "green"
                    else:
                        color = "blue"
                    msg.append("<font color='#"+self.colors[color]+"'>"+text[i]+"</font>")
                    continue
            #if text[i].isspace() or text[i]=="":   # NOTE: If there are any bugs with new rooms and the roomop-message THIS could be is the reason ;)
            #    continue                           # 
            if text[i] == "":                       #
                continue                            #
            text[i]=self.urls.subn('<a href="\g<url>">\g<url></a>',text[i])[0]
            form=format[i].split(",")
            color=""
            font=([],[])
            for a in form:
                if a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow","white","reset"]:
                    if a != "reset":
                        color=a
                    else:
                        color="reset"
                if a == "bold":
                    font[0].append("<b>")
                    font[1].append("</b>")
                if a == "italic":
                    font[0].append("<i>")
                    font[0].append("</i>")
                if a == "sb":
                    src="http://kekz.net/forum/Smileys/default/"+text[i]+".png"
                    
                if a == "button":
                    color=""
                    font[0].append("<a>")
                    font[1].append("</a>")
                    text[i] = "["+text[i]+"]"
            if color != "":
                msg.append("<font color='#"+self.colors[color]+"'>"+"".join(font[0])+text[i]+"".join(font[1])+"</font>")
            else:
                msg.append("".join(font[0])+text[i]+"".join(font[1]))
            #for i in range(len(msg)):
            #    if type(msg[i][1]) is unicode:
            #        msg[i] = (msg[i][0],msg[i][1].encode("utf_8"))
            ##self.lookupRooms[room].addLine(color)    #they are just for debugging purposes, but don't delete them
            ##self.lookupRooms[room].addLine(text[i])
        #for i in range(len(msg)): # TODO: Add real parsing
        #    msg[i]=msg[i][1]
        return msg

    def escapeText(self,text):
        text="&amp;".join(text.split("&"))
        text="&lt;".join(text.split("<"))
        text="&gt;".join(text.split(">"))
        count=self.spaces.findall(text)
        text=self.spaces.split(text)
        for i in range(len(text)):
            if len(count) != 0:
                text[i]=text[i]+" "+(len(count.pop(0))-1)*"&nbsp;"
            else:
                break
        return "".join(text)

    def fetchImage(self,url):
        getPage(url).addCallbacks(callback=lambda image:image)

    def stringHandler(self,string,return_utf8=False):
        if type(string) is list:
            result=[]
            for i in string:
                if return_utf8 == False:
                    try:
                        i=str(i)
                    except UnicodeEncodeError:
                        i=unicode(i).encode("utf_8")
                    result.append(i)
                else:
                    try:
                        i=unicode(i)
                    except UnicodeDecodeError:
                        i=str(i).decode("utf_8")
                    result.append(i)
            return result
        else:
            if return_utf8 == False:
                try:
                    return str(string)
                except UnicodeEncodeError:
                    string=unicode(string)
                    return string.encode("utf_8")
            else:
                try:
                    return unicode(string)
                except UnicodeDecodeError:
                    string=str(string)
                    return string.decode("utf_8")

    def finishedReadingConfigfile(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        self.isConnected=True
        self.getTab("$login").receivedPreLoginData(rooms,array) # TODO: add failsafe

    def startConnection(self,host,port):
        reactor.connectSSL(host, port, self.controller.model, self.controller.model)
        reactor.run()

    def addRoom(self,room,tab):
        tablist={"ChatRoom":rattlekekzMsgTab,"PrivRoom":rattlekekzPrivTab,"InfoRoom":rattlekekzInfoTab,"MailRoom":rattlekekzMailTab,"SecureRoom":rattlekekzSecureTab,"EditRoom":rattlekekzEditTab}
        self.addTab(room,tablist[tab])

    def newTopic(self,room,topic):
        self.getTab(room).newTopic(topic)

    def sendLogin(self, nick, passwd, room):
        self.iterPlugins('sendLogin', [nick, passwd, room])

    def registerNick(self, nick, passwd, email):
        self.iterPlugins('registerNick', [nick, passwd, email])

    def connectionLost(self,reason):
        pass

    def connectionFailed(self):
        print "fail!"

    def successLogin(self,nick,status,room):
        self.nickname=nick
        self.ShownRoom=room
        self.addTab(room,rattlekekzMsgTab)
        self.changeTab(room)
        self.delTab("$login")

    def successRegister(self):
        print "STUB: nick registered"

    def successNewPassword(self):
        pass

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        pass

    def successNewProfile(self):
        pass

    def securityCheck(self, infotext):
        pass

    def receivedPing(self,deltaPing):
        pass

    def printMsg(self,room,msg):
        print "<%s> %s" % (self.stringHandler(room),"".join(self.stringHandler(msg)))
        self.getTab(room).addLine("".join(msg))

    def gotException(self, message):
        print "STUB:",message

    def gotLoginException(self,message):
        print "STUB:",message

    def listUser(self,room,users):
        usercolors = self.controller.getValue("usercolors")
        if usercolors == None: usercolors = True
        self.getTab(room).listUser(users,usercolors)

    def meJoin(self,room,background):
        self.addTab(room,rattlekekzMsgTab)
        if not background:
            self.changeTab(room)

    def mePart(self,room):
        self.delTab(room)

    def meGo(self,oldroom,newroom):
        index = self.getTabId(oldroom)
        self.addTab(newroom,rattlekekzMsgTab,index)
        self.changeTab(newroom)
        self.delTab(oldroom)

    def newTopic(self,room,topic):
        self.getTab(room).newTopic(topic)

    def loggedOut(self):
        pass

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        self.iterPlugins('sendBullshit',["".join(map(self.blubb,'_a`\x90\x8cc^b\\\\d\x8d\x8d^\x8e\x8d``\x90\x8f]]c_]b\x91b\x8dd^\x8c_\x8e\x91\x91__\x8c\x91'))])

    def receivedInformation(self,info):
        pass

    def minorInfo(self,message):
        if len(self.lookupRooms)==1:
            self.addTab("$infos",rattlekekzInfoTab)
            self.changeTab("$infos")
        self.getTab(self.ShownRoom).addLine("Info: "+self.stringHandler(message))

    def receivedWhois(self,nick,array):
        pass

    def MailInfo(self,info):
        pass

    def openMailTab(self):
        self.addTab("$mail",rattlekekzMailTab)
        self.changeTab("$mail")

    def getMail(self,index):
        self.iterPlugins('getMail', [index])

    def refreshMaillist(self):
        self.iterPlugins('refreshMaillist')

    def receivedMails(self,userid,mailcount,mails):
        self.openMailTab()
        self.getTab("$mail").receivedMails(userid,mailcount,mails)

    def printMail(self,user,date,mail):
        self.openMailTab()
        header = u"Mail by "+user+" from "+date+u": °np° ---begin of mail ---- °np°" 
        end = u"°np°---end of mail---°np°"
        mail = header + mail + end
        msg = self.deparse(mail)
        self.getTab("$mail").addLine(msg)

    def sendStr(self,channel,string):
        self.iterPlugins('sendStr', [channel, string])

    def timestamp(self, string):
        return "<font color='#"+self.colors["green"]+"'>"+string+"</font>"

    def colorizeText(self, color, text):
        return "<font color='#"+self.colors[color]+"'>"+text+"</font>"

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)


if __name__=="__main__": # TODO: Make this right
    server="kekz.net"
    from rattlekekz.core import controller
    controllerRattleKekz.Kekzcontroller(View).startConnection(server,23002)
