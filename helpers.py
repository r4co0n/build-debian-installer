#!/usr/bin/python
import re

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

ph = PreseedHelper()
print(ph.getPreseedString("debianInstaller_country"))
print(ph.getPreseedMatchString("debianInstaller_country"))
print(re.match(ph.getPreseedMatchString("debianInstaller_country"), "[debian-installer/country]"))
