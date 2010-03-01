#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
#import glob

setup(name='rattlekekz-qt',
      version='0.1',
      author="Christian Scharkus",
      author_email="cscharkus[at]gmail[dot]com",
      packages=['rattlekekz.qtView'],
      scripts=['bin/rattlekekz-qt'],
      requires=['PyQt4','rattlekekz'],
      url="http://kekz.net/",
      license="GPL v3 or higher",
      data_files=[("share/emoticons/rattlekekz",glob.glob("share/emoticons/*.png"))]
     )
