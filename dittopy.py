#!/usr/bin/env python3
import subprocess
from datetime import datetime
import getopt as go
import sys, os, fcntl, struct, stat
#import os.path
import time
import hashlib
import uuid
import sqlite3
import platform
from sqlite3 import Error
#import constants
import errno
from shutil import copy2
from pathlib import Path
from os.path import expanduser

def mount():
	directory = "/Volumes/RippedMusic"
	if not os.path.exists(directory):
		os.makedirs(directory)
	os.system("mount_smbfs //johnny:johnny66@mediaserver/iTunes /Volumes/RippedMusic")

def umount():
	os.system("umount /Volumes/RippedMusic")


def logFunctionDecorator(func):
    def inner(*args, **kwargs):
        #print("*" * 30)
        #print(args[0])
        func(*args, **kwargs)
        #print("*" * 30)
    return inner

def log(*args):
    #if (constants.DEBUG):
    if (executeDebug):
        print(args)

def error(*args):
    print('*** ERROR ***', args)


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def sz(fname):
    return Path(fname).stat().st_size

def md5(fname, bsize = 4096):

    #print("%s calculating md5 of %s with buffer size %d" % (getTime(),fname,bsize))

    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(bsize), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def validFile(filename):
    return not os.path.islink(filename) and (stat.S_ISREG(os.stat(filename).st_mode) or stat.S_ISDIR(os.stat(filename).st_mode))


def createDirIfNotExist(dirName):
    try:
        os.makedirs(dirName)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def stripRoot(rootDir,dirName):
    return dirName.replace(rootDir,"")


# Check if file exists and they are the 'same' -
# currently looking at size of file to determin if equal.
# Previously used md5 to check - but too slow.
# Returns True if destination file generated/updated
@logFunctionDecorator
def dittoFile(srcFile, dstFile, dstDir):
        #print('Ditto %s %s' % (srcFile, dstFile))
        if (os.path.exists(dstFile) and (sz(srcFile) == sz(dstFile))):
            return False
        else:
            copy2(srcFile, dstDir)
            return True ;


def skipFolder(folderName,blackList=(".","Automatically Add to")):
    for bar in blackList:
        if (folderName.startswith(bar)):
            return True
    return False

def dittoFiles(rootDir, destDir, ignore=(), verbose=True):
    if (verbose):	
    	print('scanFiles Starting %s' % rootDir)
    copied = 0
    total = 0
    skipped = 0

    for dirName, subdirList, fileList in os.walk(rootDir, topdown=True):
        localDirName = stripRoot(rootDir, dirName)
        destDirName = destDir + "/" + localDirName

        if (skipFolder(localDirName, ignore)):
            skipped += 1
            print(f"Skipping Folder '{localDirName}'")
            continue

        if (len(localDirName) > 0):
            createDirIfNotExist(destDirName)

        for fname in fileList:
            localfname = localDirName + "/" + fname
            sourceFileName = dirName + "/" + fname
            destFileName = destDirName + "/" + fname
            total += 1
            if (dittoFile(sourceFileName, destFileName, destDirName)):
                copied += 1

    return copied,total,skipped

try:
    with open('.dittoignore') as f:
        ignore = [line.rstrip() for line in f]
except:
    ignore = []


home = expanduser("~")
sambaVolume = 'iTunes/RippedMusic'
rippedVolume = '/Volumes/RippedMusic'
musicPath = '/Music/iTunes/iTunes Media/Music/'
try:

	mount()
	copied, total, skipped = dittoFiles(home + musicPath, rippedVolume, ignore, False)
	umount()
except:
	pass

print('Updated %s out of %s files (skipped %s folders)' % (copied, total, skipped))

