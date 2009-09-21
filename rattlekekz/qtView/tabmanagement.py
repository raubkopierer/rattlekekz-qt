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

from PyQt4 import QtGui,QtCore

class TabManager():
    def __init__(self):
        self.ShownRoom=None
        self.lookupRooms=[]

    def changeTab(self, tabname):
        """changes the Tab to tabname"""
        Tab = self.getTab(tabname)
        self.tabs.setCurrentWidget(Tab)
        self.ShownRoom=tabname

    def getActiveTab(self):
        """returns the Active Tab"""
        return self.ShownRoom

    def getTab(self,tabname):
        """returns the object of a Tab"""
        for i in range(self.tabs.count()):
            if self.stringHandler(self.tabs.tabText(i)).lower()==self.stringHandler(tabname).lower():
                Tab=self.tabs.widget(i)
                break
        return Tab

    def getTabId(self,tabname):
        for i in range(self.tabs.count()):
            if self.stringHandler(self.tabs.tabText(i))==tabname:
                integer=i
                break
        return integer

    def addTab(self,tabname,tab,index=None):
        """adds a new Tab with tabname and the object"""
        try:
            self.getTab(tabname.lower())
        except:
            if index == None:
                self.tabs.addTab(tab(caller=self,room=tabname),tabname)
            else:
                self.tabs.insertTab(index,tab(caller=self,room=tabname),tabname)
            self.lookupRooms.append("stub")
            if self.tabs.count() == 1:
                self.ShownRoom = tabname

    def delTab(self,tabname):
        """deletes a Tab"""
        #if tabname.lower()==self.ShownRoom.lower():
        #    index=self.getTabId(self.ShownRoom)
        #    if index==0 or index==1:
        #        index=2
        #    else:
        #        index=index-1
        #    self.changeTab(self.tabs.widget(index))
        self.tabs.removeTab(self.getTabId(tabname))
        del self.lookupRooms[0]

    def highlightTab(self,tab,highlight):
        pass # TODO: Add this later on
