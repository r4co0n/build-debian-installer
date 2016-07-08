#!/usr/bin/python

class BuildInstallerConfig(object):
  
  isoUrl = 'http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-8.4.0-amd64-netinst.iso'
  isoOutFileName = 'debian.iso'
  
  loopDeviceRe = r"""^Mapped file %s as (/dev/[a-zA-Z0-9]*)\.\n$"""
  infoMountPointRe = r"""\n\s*MountPoints:\s*(/.*)\n"""
  installTypeRe = r"""^%s(.*)_%s$"""
  
  workingPath = 'cd-image/'
  staticPath = 'static/'
  templatesPath = 'templates/'
  templatesExtension = 'template'
  
  
  #~ installTypes = [
    #~ 'installGenerator',
    #~ 'odoo',
    #~ 'odoo-web',
    #~ 'docker',
  #~ ]
  
  preseedCfgTemplateName='preseed.cfg.stub'
  bootTxtCfgTemplateName='txt.cfg.stub'
  destinationPath = 'custom.iso'
  
    
  packages=[
    "etckeeper",
    "debian-goodies",
  ]
  latePackages=[
    "needrestart",
    "apt-listbugs",
  ]
  
  #~ availableSettings = [
    #~ "debianInstaller_language",
    #~ "debianInstaller_country",
    #~ "debianInstaller_locale",
    
    #~ "netcfg_hostname",
    #~ "netcfg_domain",
    
    #~ "passwd_rootPasswordCrypted",
    #~ "passwd_userFullname",
    #~ "passwd_username",
    #~ "passwd_userPasswordCrypted",
    
    #~ #"mirror_country",
    #~ #"mirror_http_hostname",
  #~ ]
  
  availableSettings = {
    "debianInstaller_language": "string",
    "debianInstaller_country": "string",
    "debianInstaller_locale": "string",
    
    "netcfg_hostname": "string",
    "netcfg_domain": "string",
    
    "passwd_rootPasswordCrypted": "string_passwordhash",
    "passwd_userFullname": "string",
    "passwd_username": "string",
    "passwd_userPasswordCrypted": "string_passwordhash",
    
    #"mirror_country",
    #"mirror_http_hostname",
  }
  #~ regexDict= {
    #~ "debianInstaller_language": r"""\[debian-installer/language\]""",
    #~ "debianInstaller_country": r"""\[debian-installer/country\]""",
    #~ "debianInstaller_locale": r"""\[debian-installer/locale\]""",
    
    #~ "netcfg_hostname": r"""\[netcfg/hostname\]""",
    #~ "netcfg_domain": r"""\[netcfg/domain\]""",
    
    #~ "passwd_rootPasswordCrypted": r"""\[passwd/root-password-crypted\]""",
    #~ "passwd_userFullname": r"""\[passwd/user-fullname\]""",
    #~ "passwd_username": r"""\[passwd/username\]""",
    #~ "passwd_userPasswordCrypted": r"""\[passwd/user-password-crypted\]""",
    
    #~ "mirror_country": None,
    #~ "mirror_http_hostname": None,
    
  #~ }
  
  class PreseedDefaults(object):
    debianInstaller_language = None
    debianInstaller_country = "DE"
    debianInstaller_locale = "en_GB.utf8"
    
    netcfg_hostname = "unnamed-host"
    netcfg_domain = ""
    
    passwd_userFullname = "Service User"
    passwd_username = "service"
    
    mirror_country = "manual"
    mirror_http_hostname = "ftp.de.debian.org"
  

