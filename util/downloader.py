#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###

###
# Set up logging
import logging
from util import color_stream

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
import urllib2

def removeAfter(string):
    """
    Remove any funny strings after the extenion when downloading
    """
    m = re.sub('\%20','_','%s' % string)
    if m:
        n = re.sub('\%20','_','%s' % m)
        return re.sub('\?.*','','%s' % n)
    else:
        return re.sub('\?.*','','%s' % string)


###
# Download the source Tarball
def get_the_thing(
  url,
  cksum
):
    """
    This will download the file provided in the url variable in the toml config file util/download_links.toml
    * in the util/download_links.toml file under the [app_url] section url needs to be set to your source code
    * this creates a directory called SRC/ and unpacks the app into it
    """

    file_name = url.split('/')[-1]
    my_working_dir = os.getcwd()
    u = urllib2.urlopen(url)
    f = open(my_working_dir+"/"+removeAfter(file_name), 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    logger.info("Downloading: %s Bytes: %s", file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    f.close()

    # Check that the file is the file we thought it was with the sha512 chksum
    if cksum == None:
        logger.info('no checksums to use')
    else:
        ####
        # This section is not finished
        ####
        logger.info('Checking the checksums...')
        myappdir = "SRC"
        logger.info(myappdir)
        build_dir = my_working_dir+"/"+myappdir
        m = hashlib.sha512()
        m.update(open(file_name,'rb').read())
        ret_str = m.hexdigest()
        if ret_str != conf_source_chk_sum:
            logger.warn("ERROR: The downloaded archive %s does not match the sha512 checksum!", file_name)
            logger.warn("sha512 checksum from %s %s", url, tomcat_chksum)
            logger.critical("local tar archive %s sha512 checksum %s", file_name, ret_str)
            sys.exit()

    #logger.info("Extracting tar file: %s"+"/"+"%s", my_working_dir, file_name)
    #tar = tarfile.open(file_name)
    #tar.extractall(path=build_dir)
    #tar.close()

    #return build_dir


