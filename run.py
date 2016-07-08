#!/usr/bin/python
from config import BuildInstallerConfig
from helpers import PreseedHelper

import os
import shutil
import re
from subprocess import check_call, check_output
from time import sleep
from importlib import import_module
import glob

class BuildInstaller(object):
  #. getiso.sh
  def _getIso(self):
    check_call([
      "wget",
      self.config.isoUrl,
      "-O", self.config.isoOutFileName
    ])
  
  def __getLoopDevicePart(self, loopDevice):
    return "%sp1" % (loopDevice)
  
  def _mountIso(self, iso, loopDeviceRe, infoMountPointRe):
    #loop_device=`udisksctl loop-setup --no-user-interaction -r -f "$GETISO_OUTFILENAME" | grep -o -e /dev/[a-zA-Z0-9]*\. -`
    print("iso: %s" % (iso) )
    loopSetupOutput = check_output([
                "udisksctl",
                "loop-setup",
                "--read-only",
                "-f", iso,
              ])
    print("loopSetupOutput: %s" % (loopSetupOutput))
    loopDeviceRe = loopDeviceRe % ( iso )
    loopDevice = re.search(loopDeviceRe, loopSetupOutput).group(1)
    print(loopDevice)
    loopDevicePart = None
    sleep(1)
    if loopDevice:
      loopDevicePart = self.__getLoopDevicePart(loopDevice)
      infoOutput = check_output([
                  "udisksctl",
                  "info",
                  "-b", loopDevicePart,
                ])
      mountPoint = re.search(infoMountPointRe, infoOutput).group(1)
      print(mountPoint)
    return ( loopDevice, mountPoint )
    
      #~ print(mountOutput)
      #~ mountRe = self.config.mountRe % ( self.loopDevicePart )
      #~ self.mountPoint = re.search(mountRe, mountOutput).group(1)
      #~ print(self.mountPoint)
    
  def _unmountIso(self, loopDevice):
    #sleep(1)
    #udisksctl unmount --no-user-interaction -b "$loop_device"p1
    loopDevicePart = self.__getLoopDevicePart(loopDevice)
    check_call([
      "udisksctl",
      "unmount",
      "--no-user-interaction",
      "-b", "%s" % (loopDevicePart),
    ])
    #udisksctl loop-delete --no-user-interaction -b "$loop_device"
    #~ check_call([
      #~ "udisksctl",
      #~ "loop-delete",
      #~ "--no-user-interaction",
      #~ "-b", "%s" % (loopDevice),
    #~ ])
  
  def _cleanDirectory(self, path):
    check_call([
      "find",
      path,
      "-mindepth", "1",
      "-delete",
    ])
  
  def _copyIso(self, src, dst):
    src = self.mountPoint
    dst = self.config.workingPath
    
    #cp -rT "$iso_mountpoint" "$WORKING_DIRECTORY"
    check_call([
      "cp",
      "-r",
      "-T",
      src,
      dst,
    ])
    
    #chmod -R u+w "$WORKING_DIRECTORY"
    check_call([
      "chmod",
      "-R",
      "u+w",
      dst,
    ])
    
  
  def _copyStaticPath(self):
    check_call([
      "cp",
      "-r",
      "-T",
      self.config.staticPath,
      self.config.workingPath,
    ])
  
  def _copyTemplateStaticPath(self):
    templateStaticPath = "%sstatic/" % ( self.templatePath )
    #~ cp -rv "${SOURCE_DIRECTORY}." "$WORKING_DIRECTORY"
    check_call([
      "cp",
      "-r",
      "-T",
      templateStaticPath,
      self.config.workingPath,
    ])
  
  def __promptForPassword(self, salt=None):
    cmd = [
        "mkpasswd",
        "-m", "sha-512",
      ]
    
    if salt:
      cmd.append("-S")
      cmd.append(salt)
    
    return check_output(cmd)
    
  def __getPassword(self, username):
    pwdHash = None
    pwdRepeatHash = None
    i = 0
    while not pwdHash or pwdHash != pwdRepeatHash:
      if i > 0:
        print("Password mismatch, please retry...")
      print("Enter password for %s:" % ( username ) )
      pwdHash = self.__promptForPassword()
      print("Repeat password for %s:" % ( username ) )
      salt = pwdHash.split("$", 3)[2]
      pwdRepeatHash = self.__promptForPassword(salt)
      i+=1
    return pwdHash.strip()
  
  def __getString(self, setting):
    return raw_input( "Enter value for %s preseed config parameter: " % (setting) ) 
  
  def _setBootEntry(self, settingsDict):
    bootTxtCfgTemplatePath = os.path.join(self.config.templatesPath, self.config.bootTxtCfgTemplateName)
    bootTxtCfgTemplate = None
    with open(bootTxtCfgTemplatePath, 'r') as bootTxtCfgTemplateFile:
      bootTxtCfgTemplate = bootTxtCfgTemplateFile.read()
    
    bootTxtCfg = bootTxtCfgTemplate
    label = "%s_%s.%s" % ( self.installType.lower(), settingsDict["netcfg_hostname"], settingsDict["netcfg_domain"] )
    preseedFile = os.path.join( "/cdrom", self.preseedCfgPath )
    
    bootTxtCfg = re.sub( r"""\[label\]""", label, bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[install-type\]""", self.installType, bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[netcfg/hostname\]""", settingsDict["netcfg_hostname"], bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[preseed/file\]""", preseedFile, bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[debian-installer/language\]""", settingsDict["debianInstaller_language"], bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[debian-installer/country\]""", settingsDict["debianInstaller_country"], bootTxtCfg )
    bootTxtCfg = re.sub( r"""\[debian-installer/locale\]""", settingsDict["debianInstaller_locale"], bootTxtCfg )
    
    
    bootTxtCfgPath = os.path.join( self.config.workingPath, "isolinux", "txt.cfg" )
    with open(bootTxtCfgPath, 'a') as bootTxtCfgFile:
      bootTxtCfgFile.write(bootTxtCfg)
  
  
  def __userQueryConfigValue(self, setting):
    settingType = self.config.availableSettings[setting]
    if settingType == "string":
      return self.__getString(setting)
    elif settingType == "string_passwordhash":
      return self.__getPassword("Root User")
    else:
      raise ValueError("No user-querying implemented for setting %s of type %s" % (setting, settingType) )
  
  def __getConfigValue(self, SpecificConf, DefaultConf, setting):
    defaultValue = getattr(DefaultConf, setting, None)
    presetValue = getattr(SpecificConf, setting, defaultValue)
    if presetValue == None:
      print( "No value for setting %s provided in neither template config nor defaults. Trying to find a user query mechanism for this setting..." % setting )
      return self.__userQueryConfigValue(setting)
    else:  
      return presetValue
  
  
  def __generateConfigDict(self, SpecificConf, DefaultConf, settings):
    settingsDict = {}
    for setting in settings:
      settingsDict[setting] = self.__getConfigValue(SpecificConf, DefaultConf, setting)
      
    return settingsDict
  
  
  def __mergePackageLists(self, packageListName, *Configs ):
    packageList = []
    for Config in Configs:
      packageList += getattr(Config, packageListName, [])
    return " ".join( list(set(packageList)) )
  
  def _generatePreseedCfg(self):
    preseedCfgTemplatePath = os.path.join(self.config.templatesPath, self.config.preseedCfgTemplateName)
    preseedCfgTemplate = None
    with open(preseedCfgTemplatePath, 'r') as preseedCfgTemplateFile:
      preseedCfgTemplate = preseedCfgTemplateFile.read()
    
    configDict = self.__generateConfigDict(
                      self.InstallTypeConfig,
                      self.config.PreseedDefaults,
                      self.config.availableSettings,
                    )
    
    print("%s" % (configDict))
    
    #preseedcfg="${WORKING_DIRECTORY}preseed/preseed_${INSTALL_TYPE}_${PRESEED_NETCFG_HOSTNAME}.cfg"
    self.preseedCfgPath = os.path.join(
        "preseed",
        "preseed_%s_%s.cfg" % ( self.installType.lower(), configDict["netcfg_hostname"] )
      )
    preseedCfgDeployPath = os.path.join(
        self.config.workingPath,
        self.preseedCfgPath
      )
    
    packagesString = self.__mergePackageLists("packages", self.config, self.InstallTypeConfig )
    print("packages: %s" % (packagesString))
    latePackagesString = self.__mergePackageLists("latePackages", self.config, self.InstallTypeConfig )
    print( "latePackages: %s" % (latePackagesString) )
    
    outlines = preseedCfgTemplate
    for settingName, configValue in configDict.items():
      print("%s: %s" % (settingName, configValue) )
      preseedMatchString = self.preseedHelper.getPreseedMatchString(settingName)
      outlines = re.sub( preseedMatchString, configValue, outlines )
    
    if packagesString != "":
      outlines = re.sub( r"""\[pkgsel/include\]""", packagesString, outlines )
    else:
      outlines = re.sub( r"""^.*?\[pkgsel/include\].*?\n""", "", outlines )
    with open(preseedCfgDeployPath, "w") as outFile:
      outFile.write(outlines)
    
    self._setBootEntry(configDict)
    
  def _generateIso(self):
    #~ genisoimage -r -V "Custom Debian Install CD" \
          #~ --cache-inodes \
          #~ -J -l -b "isolinux/isolinux.bin" \
          #~ -c "isolinux/boot.cat" --no-emul-boot \
          #~ -boot-load-size 4 -boot-info-table \
          #~ -o "$MAKEISO_FILE" "$WORKING_DIRECTORY"
    check_call([
      "genisoimage", "-r", "-V", "Custom Debian Install CD",
      "--cache-inodes",
      "-J", "-l", "-b", "isolinux/isolinux.bin",
      "-c", "isolinux/boot.cat", "--no-emul-boot",
      "-boot-load-size", "4", "-boot-info-table",
      "-o", self.config.destinationPath,
      self.config.workingPath,
    ])
  
  def _getTemplatePath(self, installType):
    return "%s%s_%s" % (self.config.templatesPath, installType, self.config.templatesExtension)
    
  
  def __init__(self):
    self.config = BuildInstallerConfig()
    self.preseedHelper = PreseedHelper()
    self.loopDevice = None
  
  def build(self):
    #self._getIso()
    
    try:
      print("Cleaning working directory %s" % (self.config.workingPath) ) 
      self._cleanDirectory(self.config.workingPath)

      print("Mounting source iso image %s" % (self.config.isoOutFileName) )
      self.loopDevice, self.mountPoint = self._mountIso(self.config.isoOutFileName, self.config.loopDeviceRe, self.config.infoMountPointRe)

      print("Copying source iso image data from '%s' to '%s'" % (self.mountPoint, self.config.workingPath) )
      self._copyIso(self.mountPoint, self.config.workingPath)
    finally:
      print("Unmounting source iso image")
      self._unmountIso(self.loopDevice)
    
    self._copyStaticPath()
    
    installTypePaths = glob.glob( self._getTemplatePath("*") )
    installTypePathDict = {}
    
    for installTypePath in installTypePaths:
      installTypeRe = self.config.installTypeRe % (self.config.templatesPath, self.config.templatesExtension)
      installType = re.search(installTypeRe, installTypePath).group(1)
      installTypePathDict[installType] = installTypePath
    
    for installType, installTypePath in installTypePathDict.items():
      
      self.installType = installType
      self.templatePath = installTypePath
      print( "%svalues" % ( self.templatePath.replace("/",".") ) )
      self.InstallTypeConfig = import_module( self.templatePath.replace("/",".")+".config" )
      #self._copyTemplateStaticPath()
      self._generatePreseedCfg()
    
    self._generateIso()


bi = BuildInstaller()
bi.build()
#~ 
#~ #. ./mountiso.sh
#~ # Empty working directory
#~ echo "Starting to empty working directory $WORKING_DIRECTORY"
#~ #rm -r "$WORKING_DIRECTORY"
#~ #mkdir "$WORKING_DIRECTORY"
#~ find "$WORKING_DIRECTORY" -mindepth 1 -delete
#~ echo "Finished emptying $WORKING_DIRECTORY"
#~ # Copy iso contents to working directory
#~ echo "Starting to copy contents of iso $GETISO_OUTFILENAME to working directory $WORKING_DIRECTORY"
#~ cp -rT "$iso_mountpoint" "$WORKING_DIRECTORY"
#~ echo "Finisehd copying contents of iso to working directory"
#~ . ./unmountiso.sh
#~ # Make all files writable for this user
#~ chmod -R u+w "$WORKING_DIRECTORY"
#~ cp -rv "${SOURCE_DIRECTORY}." "$WORKING_DIRECTORY"

#~ 
#~ . ./generate_preseedcfg.sh
#~ 
#~ genisoimage -r -V "Custom Debian Install CD" \
      #~ --cache-inodes \
      #~ -J -l -b "isolinux/isolinux.bin" \
      #~ -c "isolinux/boot.cat" --no-emul-boot \
      #~ -boot-load-size 4 -boot-info-table \
      #~ -o "$MAKEISO_FILE" "$WORKING_DIRECTORY"
