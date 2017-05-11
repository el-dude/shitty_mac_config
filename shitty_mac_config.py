#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###

###
# Set up logging
import logging
from util import color_stream
from util import downloader

handler = color_stream.ColorizingStreamHandler()
handler.setFormatter(logging.Formatter(\
"%(asctime)s [%(levelname)5s] %(name)s - %(message)s"))
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.WARN)
logger = logging.getLogger(__name__)
# will apply to all child modules of this package, as well
logger.setLevel(logging.DEBUG)
###

import os, platform, sys, re, shutil, errno
import glob
import subprocess
import urllib2
import zipfile
import fnmatch
import pytoml as toml

###
# For the record this is terrible...
c_path  = os.getcwd()
config  = c_path+"/"+"util/download_links.toml"
pkg_source = c_path+"/"+"PKGS/"
with open(config, 'rb') as fin:
    config_obj = toml.load(fin)

urls_source_chk_sum = None
urls = config_obj["app_urls"]
os.chdir(pkg_source)
### Testing
# added this for testing so we need not keep downloading files
if not any(fname.endswith('.dmg') for fname in os.listdir('.')):
    for val in urls:
        #print(urls[val])
        downloader.get_the_thing(urls[val],urls_source_chk_sum)
else:
    logger.info("all ready downloaded files")
###


def dmg_reg_install(name):
    """
    Ths will install apps from a .dmg
    """
    m               = re.sub('\.dmg','','%s' % name)
    mount_path      = "/Volumes/"+m
    dmg_conv_cdr    = re.sub('\.dmg','.cdr','%s' % name)
    cdr_path        = os.getcwd()+"/"+dmg_conv_cdr
    dmg_path        = os.getcwd()+"/"+name
    mounted_app_dir = mount_path+'/*.app'
    app_dir         = "/Applications"
    dmg_before_cmds = [
        ["/usr/bin/hdiutil", "attach", "-mountpoint", mount_path, dmg_path],
        ["/usr/bin/hdiutil", "convert", dmg_path, "-format", "UDTO", "-o", dmg_conv_cdr],
        ["/usr/bin/hdiutil", "detach", mount_path],
        ["/usr/bin/hdiutil", "attach", "-mountpoint", mount_path, cdr_path]
    ]

    logger.info("starting to install app: %s" % name)
    for cmd in dmg_before_cmds:
        logger.info(subprocess.check_output(cmd))

    the_app_to_install = glob.glob(mounted_app_dir)[0]
    logger.info("THe glob is: %s" % the_app_to_install)
    dmg_after_cmds = [
        ["sudo", "rsync", "-av", the_app_to_install, app_dir],
        ["/usr/bin/hdiutil", "detach", mount_path]
    ]
    logger.info("Syncing the App(%s) to /Applications" % name)
    for cmd in dmg_after_cmds:
        logger.info(subprocess.check_output(cmd))


# Very terrible vagrant & VirtualBox needs this
def dmg_pkg_install(name):
    """
    This func will install the .pkg in the .dmg packages
    """
    m               = re.sub('\.dmg','','%s' % name)
    mount_path      = "/Volumes/"+m
    dmg_conv_cdr    = re.sub('\.dmg','.cdr','%s' % name)
    cdr_path        = os.getcwd()+"/"+dmg_conv_cdr
    dmg_path        = os.getcwd()+"/"+name
    mounted_app_dir = mount_path+"/*.pkg"
    app_dir         = "/Applications"
    dmg_before_cmds = [
        ["/usr/bin/hdiutil", "attach", "-mountpoint", mount_path, dmg_path],
        ["/usr/bin/hdiutil", "convert", dmg_path, "-format", "UDTO", "-o", dmg_conv_cdr],
        ["/usr/bin/hdiutil", "detach", mount_path],
        ["/usr/bin/hdiutil", "attach", "-mountpoint", mount_path, cdr_path]
    ]

    logger.info("starting to install app: %s" % name)
    for cmd in dmg_before_cmds:
        logger.info(subprocess.check_output(cmd))

    the_app_to_install = glob.glob(mounted_app_dir)[0]
    logger.info("THe glob is: %s" % the_app_to_install)
    dmg_after_cmds = [
        ["sudo", "/usr/sbin/installer", "-pkg", the_app_to_install, "-target", "/"],
        ["/usr/bin/hdiutil", "detach", mount_path]
    ]

    logger.info("Syncing the App(%s) to /Applications" % name)
    for cmd in dmg_after_cmds:
        logger.info(subprocess.check_output(cmd))

# zip package installer
def zip_pkg_install(name):
    """
    Install zip file packages.
    """
    zip_path    = os.getcwd()+"/"+name
    app_path    = os.getcwd()+"/"+"*.app"
    app_dir     = "/Applications"
    zip_ref     = zipfile.ZipFile(zip_path, 'r')
    logger.info("starting to install app: %s" % name)
    zip_ref.extractall(app_dir)
    zip_ref.close()


### Check if it is one of the following
# if it is a zip file
# if it is a dmg and is one of the ones with pkg's
# if it is terreform

apps_path = os.getcwd() #+"/PKGS"
dirs = os.listdir(apps_path)
for app in dirs:
    dmg     = fnmatch.fnmatch(app, '*.dmg')
    zipp    = fnmatch.fnmatch(app, '*.zip')
    if dmg:
        if fnmatch.fnmatch(app, 'vagrant*'):
            logger.info("Installing the Vagrant package: %s" % app)
            #print("Vagrant: "+app)
            dmg_pkg_install(app)

        elif fnmatch.fnmatch(app, 'VirtualBox*'):
            logger.info("Installing the VirtBox Package: %s" % app)
            #print("VirtBox: "+app)
            dmg_pkg_install(app)

        else:
            #print("DMG: "+app)
            logger.info("Installing the App: %s" % app)
            dmg_reg_install(app)

    if zipp:
        #print("Zip: "+app)
        if fnmatch.fnmatch(app, 'terraform*'):
            logger.info("Installing Terraform version: %s" % app)
            tf_app_path = apps_path+"/"+app
            appdir_name = re.sub('\.zip','','%s' % app)
            newpath = '/usr/local/%s' % appdir_name
            logger.info("Checking for directory path: %s" % newpath)
            if not os.path.exists(newpath):
                logger.info("Creating directory: %s" % newpath)
                os.makedirs(newpath)

            logger.info("Unzipping %s" % tf_app_path)
            zip_ref = zipfile.ZipFile(tf_app_path, 'r')
            zip_ref.extractall(newpath)
            zip_ref.close()
            logger.info("Creating the symlinks for Terraform")
            os.symlink(newpath+'/terraform', '/usr/local/terraform')
        else:
            zip_pkg_install(app)





