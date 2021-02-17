# dittopy

*dittopy* - a Python utility (version 3+) which 'merges' a source folder into a destination folder. New folders and files are copied over - but only 'changes' in source files are copied over their original destination files.

Currently a change is detected by comparing the size of files - but this can easily be changed to using a hashing function.
Since the main purpose of this utility was to update 'ripped' music onto a NAS drive - the 'size' strategy works very well.


A '.dittyignore' is read which contains a list of folder names which can be ignored (one folder name per line).
