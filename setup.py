#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='rattlekekz-qt',
      version='0.1',
      author="Christian Scharkus",
      author_email="cscharkus[at]gmail[dot]com",
      packages=['rattlekekz.qtView'],
      requires=['PyQt4','rattlekekz'],
      url="http://kekz.net/",
      license="GPL v3 or higher"
     )
