#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import glob

setup(name='rattlekekz-qt',
      version='20100423',
      author="Christian Scharkus",
      author_email="cscharkus[at]gmail[dot]com",
      packages=['rattlekekz.qtView','twisted.plugins'],
      py_modules=['qt4reactor'],
      scripts=['bin/rattlekekz-qt'],
      url="http://github.com/raubkopierer/rattlekekz-qt",
      license="GPL v3 or higher",
      data_files=[("share/emoticons/rattlekekz",glob.glob("rattlekekz/emoticons/*.png"))]
     )
