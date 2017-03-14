#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from os import path, mkdir, system
from main.ui import Console
from main.handlers.color import banner
import platform
version = '1.0'
author  = 'Z3br4'
name = 'acc_tester'

def main():
    folderDB = path.expanduser('~/' + name + '-db')
    db_path = path.join(folderDB, name + '.db')
    if not path.exists(folderDB):
        mkdir(folderDB)
    if platform.system() == 'Windows':
    	system('cls')
    elif platform.system() == 'Linux':
    	system('clear')
    shell = Console(db_path)
    shell.cmdloop(banner(version,author))

if __name__ == "__main__":
    main()