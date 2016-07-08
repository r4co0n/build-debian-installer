#!/usr/bin/python
import re

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PreseedHelper(object):
  def getPreseedString(self, setting):
    result = ""
    for c in setting:
      if c.isupper():
        result += "-"
        result += c.lower()
      elif c == "_":
        result += "/"
      else:
        result += c
    return  "[%s]" % result
  
  def getPreseedMatchString(self, setting):
    setting = self.getPreseedString(setting)
    return re.escape(setting)
  
  def getSettingString(self, preseedString):
    result = ""
    nextUpper = False
    for c in regexString:
      if nextUpper:
        c = c.upper()
        nextUpper = False
      if c == "-":
        nextUpper = True
      elif c == "/":
        result += "_"
      else:
        result += c
    return result

