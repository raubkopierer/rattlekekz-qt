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

import sys,os
from glob import glob
from re import search
import re,urllib

#twisted/qt
from PyQt4 import QtGui,QtCore
import qt4reactor
app = QtGui.QApplication(sys.argv)
qt4reactor.install()
from twisted.internet import reactor
from twisted.internet.defer import DeferredSemaphore
from twisted.web.client import getPage

from rattlekekz.core.pluginmanager import iterator
from rattlekekz.qtView.tabs import *
from rattlekekz.qtView.widgets import *
from rattlekekz.qtView.tabmanagement import TabManager

rev=search("\d+",revision).group()
# flachzange, als ich dir objektorientierte programmierung erklärt habe meinte ich damit nicht du solltest alles
# was dir aus dem hirn trieft in eine grosse klasse laufen lassen, für sowas gibt es taschentücher.
# aus dem kram hier muss man min 2-3 klassen machen, ich würd mal damit anfangen den parser in eine kekzparser
# klasse zu refaktoren. und hab bitte den anstand dann für jede klasse auch ne eigene datei zu machen.
class View(TabManager,iterator):
    def __init__(self,controller):
        self.name,self.version="rattlekekz-qt",20100806  # Diese Variablen werden vom View abgefragt
        self.controller=controller
        self.revision=rev
        self.alert=app.alert
        TabManager.__init__(self)
        self.spaces=re.compile(r"  {1,}")
        self.urls=re.compile(r"(?=\b)((?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|edu|pro|asia|cat|coop|int|tel|post|xxx|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?)(?=\b)",re.I)
        self.blubb=lambda x:chr(ord(x)-43)
        self.plugins={}
        self._setup()
        self.addTab("$login",rattlekekzLoginTab)
        self.changeTab("$login")
        self.main.show()
        self.smilie_data=self.readSmilies()
        self.loading_data=open(sys.prefix+os.sep+'share'+os.sep+'emoticons'+os.sep+'rattlekekz'+os.sep+'loading.png').read()
        self.loading_image=QtGui.QImage()
        self.loading_image.loadFromData(self.loading_data,"PNG")
        self.images={}
        self.pendingImages=[]
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
                     "blue":"0000FF",
                     "green":"008000",
                     "gray":"696969",
                     "cyan":"00FFFF",
                     "magenta":"FF00FF",
                     "orange":"FFA500",
                     "pink":"FFC0CB",
                     "yellow":"FFFF00",
                     "normal":"000000",
                     "normalaway":"696969",
                     "greenaway":"4D804D",
                     "blueaway":"5050E6",
                     "orangeaway":"E5B151",
                     "redaway":"E65151"}
        self.imageLock = DeferredSemaphore(1)

    def _setup(self):
        self.main=rattlekekzMainWidget()
        self.main.setWindowTitle(self.name)
        self.main.setMenuBar(rattlekekzMenuBar())
        self.main.setStatusBar(rattlekekzStatusBar())
        self.menu=self.main.menuBar()
        self.status=self.main.statusBar()
        self.main.setCentralWidget(QtGui.QTabWidget())
        self.tabs=self.main.centralWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        #self.tabs.setMinimumSize(400,550)
        self.main.connect(self.tabs,QtCore.SIGNAL("tabCloseRequested(int)"),self.closeTab)
        self.main.connect(self.main,QtCore.SIGNAL("closed()"),self.quit)
        self.main.connect(self.menu,QtCore.SIGNAL("quit()"),self.quit)
        self.main.connect(self.menu,QtCore.SIGNAL("config()"),self.openConfig)
        self.main.connect(self.tabs,QtCore.SIGNAL("currentChanged(int)"),self.activateTab)
        self.main.connect(self.main,QtCore.SIGNAL("gotFocus()"),self.changeFocus)

    def readSmilies(self):
        data=[]
        for i in glob(sys.prefix+os.sep+'share'+os.sep+'emoticons'+os.sep+'rattlekekz'+os.sep+'*.png'):
            data.append((QtCore.QUrl("smilie://"+i.split(os.sep)[-1]),QtGui.QImage(i,"PNG")))
        return data

    def activateTab(self,integer):
        self.ShownRoom=self.stringHandler(self.tabs.tabText(integer))
        self.tabs.tabBar().setTabTextColor(integer,QtCore.Qt.black)
        self.tabs.widget(integer).gotFocus()

    def closeTab(self,integer):
        if isinstance(self.tabs.widget(integer),rattlekekzMsgTab):
            self.sendStr(self.stringHandler(self.tabs.tabText(integer)),"/part")
        else:
            if isinstance(self.tabs.widget(integer),rattlekekzInfoTab):
                text = self.stringHandler(self.tabs.tabText(integer))
                if text.startswith("whois"):
                    self.controller.closedWhois(text.split(" ")[1])
            self.tabs.removeTab(integer)
            del self.lookupRooms[0]

    def changeFocus(self):
        self.tabs.widget(self.getTabId(self.ShownRoom)).gotFocus()

    def getRooms(self):
        rooms=[]
        for i in range(self.tabs.count()):
            room = self.stringHandler(self.tabs.tabText(i))
            if not room.startswith("#") and not room.startswith("whois: "):
                rooms.append(room)
        return rooms

    def quit(self):
        self.iterPlugins('quitConnection')
        reactor.stop()

    def openConfig(self):
        print "STUB: implement config tab"

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
                image=self.controller.loadImage(text[i])
                if image[0] == "image":
                    self.pendingImages.append(str(image[1]))
                msg.append("<img src='image://"+str(image[1])+".jpg'>")
                #try:
                #    image=urllib.urlretrieve(text[i])[0]
                #    msg.append("<img src='"+self.stringHandler(image)+"'>")
                #except:
                #    msg.append(self.escapeText("<image url is invalid>"))
                #image=urllib2.urlopen(text[i]).read()
                #for y in range(self.tabs.count()):
                #    if isinstance(self.tabs.widget(y),rattlekekzPrivTab):
                #        self.tabs.widget(y).output.document().addResource(QtGui.QTextDocument.ImageResource,QtCore.QUrl("mydata://"+self.stringHandler(text[i])),QVariant(image))
                #        msg.append(("<img src='"+"mydata://"+self.stringHandler(text[i])+"'>"))
                continue
            if len(format[i]) > 1:
                if format[i][0] == "ownnick":
                    if not "red" in format[i][1]:
                        color = "red"
                    else:
                        color = "green"
                    msg.append("<font color='#"+self.colors[color]+"'><b>"+text[i]+"</b></font>")
                    continue
            #if text[i].isspace() or text[i]=="":   # NOTE: If there are any bugs with new rooms and the roomop-message THIS could be is the reason ;)
            #    continue                           # 
            if text[i] == "":                       #
                continue                            #
            text[i]=self.urls.sub(r'<a href="\1">\1</a>',text[i])
            form=format[i].split(",")
            color=""
            font=([],[])
            for a in form:
                if a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow","white","reset"]:
                    if a != "reset":
                        color=a
                    else:
                        color=""
                if a == "bold":
                    font[0].append("<b>")
                    font[1].append("</b>")
                if a == "italic":
                    font[0].append("<i>")
                    font[1].append("</i>")
                if a == "sb":
                    text[i]="<img src='"+"smilie://"+self.stringHandler(text[i])+".png' />"
                if a == "button":
                    color=""
                    font[0].append("<a href='button:"+text[i]+"'>")
                    font[1].append("</a>")
                    text[i] = "["+text[i]+"]"
            if color != "":
                msg.append("<font color='#"+self.colors[color]+"'>"+"".join(font[0])+text[i]+"".join(font[1])+"</font>")
            else:
                msg.append("".join(font[0])+text[i]+"".join(font[1]))
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

    def loadedImage(self,id,image_data):
        id=str(id)
        image=QtGui.QImage()
        image.loadFromData(image_data)
        if self.images.has_key(id):
            tab = self.getTab(self.images[id])
            self.imageLock.run(tab.refreshImage,id,image)
        else:
            reactor.callLater(10,self.loadedImage,id,image_data)

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
                        i=str(i).decode("utf_8","replace")
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
                    return string.decode("utf_8","replace")

    def finishedReadingConfigfile(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        self.isConnected=True
        self.status.showMessage("connected")
        self.addTab("$login",rattlekekzLoginTab)
        self.getTab("$login").receivedPreLoginData(rooms,array)

    def updateRooms(self,rooms):
        try:
            tab=self.getTab("$login")
        except:
            pass
        else:
            tab.updateRooms(rooms)

    def startConnection(self,host,port):
        self.controller.startConnection(host,port)

    def addRoom(self,room,tab):
        tablist={"ChatRoom":rattlekekzMsgTab,
                 "PrivRoom":rattlekekzPrivTab,
                 "InfoRoom":rattlekekzInfoTab,
                 "WhoisRoom":rattlekekzInfoTab,
                 "MailRoom":rattlekekzMailTab,
                 "SecureRoom":rattlekekzSecureTab,
                 "EditRoom":rattlekekzWhoisEditTab,
                 "MailEditRoom":rattlekekzMailEditTab}
        self.addTab(room,tablist[tab])

    def newTopic(self,room,topic):
        self.getTab(room).newTopic(topic)

    def sendLogin(self, nick, passwd, room):
        self.getTab("$login").grayOut()
        self.iterPlugins('sendLogin', [nick, passwd, room])

    def registerNick(self, nick, passwd, email):
        self.iterPlugins('registerNick', [nick, passwd, email])

    def changePassword(self, oldPassword, newPassword):
        self.iterPlugins('changePassword', [oldPassword, newPassword])

    def updateProfile(self, newName, newLocation, newHomepage, newHobbies, newSignature, passwd):
        self.iterPlugins('updateProfile', [newName, newLocation, newHomepage, newHobbies, newSignature, passwd])

    def startedConnection(self):
        self.status.showMessage("connecting ...")

    def connectionLost(self,reason):
        self.status.showMessage(self.stringHandler("connection lost",True))

    def connectionFailed(self):
        self.status.showMessage("connection attempt failed")

    def successLogin(self,nick,status,room,reconnected=False):
        self.nickname=nick
        self.addTab(room,rattlekekzMsgTab)
        if not reconnected:
            self.ShownRoom=room
            self.changeTab(room)
        try:
            self.delTab("$login")
        except:
            pass

    def successRegister(self):
        self.status.showMessage("nick registered")

    def successNewPassword(self):
        self.status.showMessage("password changed")

    def receivedProfile(self,name,location,homepage,hobbies,signature):
        self.changeTab("$edit")
        self.getTab("$edit").receivedProfile(name,location,homepage,hobbies,signature)

    def successNewProfile(self):
        self.status.showMessage("profile updated")

    def securityCheck(self, infotext):
        pass

    def receivedPing(self,deltaPing):
        self.status.showMessage(self.stringHandler("Ping: "+str(deltaPing)+" ms",True))

    def printMsg(self,room,msg):
        #print "<%s> %s" % (self.stringHandler(room),"".join(self.stringHandler(msg)))
        msg = "".join(msg)
        ids=re.findall(r"<img\s+src='image://(\d+)\.jpg'\s*>",msg)
        if len(ids) != 0:
            if isinstance(self.getTab(room),(rattlekekzPrivTab,rattlekekzInfoTab,rattlekekzMailTab)):
                for i in ids:
                    self.images[i]=room
                    if i in self.pendingImages:
                        image=QtGui.QImage()
                        image.loadFromData(self.controller.getImage(int(i)))
                        self.getTab(room).addImage(i,image)
                        self.pendingImages.remove(i)
                    else:
                        self.getTab(room).addImage(i,self.loading_image)
        self.getTab(room).addLine(msg)

    def gotException(self, message):
        self.status.showMessage(message)

    def gotLoginException(self,message):
        try:
            tab = self.getTab("$login")
        except:
            pass
        else:
            tab.grayOut(False)
            tab.prelogin=True
            tab.gotFocus()
        self.status.showMessage(message)

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

    def minorInfo(self,room,nick):
        """this method is used to determine wether a new info-tab must be opened to display e.g. a bot message"""
        pre=None
        if nick=="":
            pre="Info:°nn°"
        if not isinstance(self.getTab(self.ShownRoom),rattlekekzMsgTab):
            self.addRoom("$info","InfoRoom")
            self.changeTab("$info")
            return (pre,"$info")
        elif room=="":
            return (pre,self.ShownRoom)
        else:
            return (pre,room)
        #if isinstance(self.getTab(self.ShownRoom),self.rattlekekzMsgTab):
        #    self.getTab(self.ShownRoom).addLine("Info: "+self.stringHandler(message))
        #else:
        #    self.addTab("$infos",rattlekekzInfoTab)
        #    self.changeTab("$infos")
        #    self.getTab(self.ShownRoom).addLine("Info: "+self.stringHandler(message))

    def receivedWhois(self,nick,array):
        title=u"whois: "+self.stringHandler(nick,True)
        out = map(lambda x:"".join(self.deparse(x)), array)
        try:
            tab = self.getTab(title)
        except:
            self.addRoom(title,"WhoisRoom")
            self.changeTab(title)
        self.getTab(title).addWhois()
        for msg in out:
            self.printMsg(title,msg)
        self.highlightTab(title,2)

    def MailInfo(self,info):
        pass

    def openLinkTab(self,room,links):
        room,links=self.stringHandler(room,True),self.stringHandler(links,True)
        self.addTab("$links of "+room,rattlekekzInfoTab)
        self.changeTab("$links of "+room)
        for i in links:
            self.getTab("$links of "+room).addLine('<a href="'+i+'">'+i+'</a>')

    def openMailEditTab(self,receiver=""):
        tabname="$mail_to"
        if receiver!="":
            tabname=tabname+" "+receiver
        self.addTab(tabname,rattlekekzMailEditTab)
        self.getTab(tabname).setContent(receiver)
        self.changeTab(tabname)

    def openMailTab(self):
        self.addTab("$mails",rattlekekzMailTab)
        self.changeTab("$mails")

    def getMail(self,index):
        self.iterPlugins('getMail', [index])

    def refreshMaillist(self):
        self.iterPlugins('refreshMaillist')

    def receivedMails(self,userid,mailcount,mails):
        self.openMailTab()
        self.getTab("$mails").receivedMails(userid,mailcount,mails)

    def printMail(self,user,date,mail):
        self.openMailTab()
        header = u"Mail by "+user+" from "+date+u": °np° ---begin of mail ---- °np°" 
        end = u"°np°---end of mail---°np°"
        mail = header + self.stringHandler(mail,True) + end
        msg = self.deparse(mail)
        self.getTab("$mails").addLine(msg)

    def sendStr(self,channel,string):
        self.iterPlugins('sendStr', [channel, string])

    def sendMail(self,nick,msg):
        self.iterPlugins('sendMail', [nick, msg])

    def timestamp(self, string):
        return "<font color='#"+self.colors["green"]+"'>"+string+"</font>"

    def colorizeText(self, color, text):
        return "<font color='#"+self.colors[color]+"'>"+text+"</font>"

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)
