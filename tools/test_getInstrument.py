#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import tkinter as gui
from tkinter import simpledialog

VERBOSE = "-v" in sys.argv

def setVerbose(value):
    global VERBOSE
    VERBOSE = value

def prompt(text="", initialvalue=""):
    win = gui.Tk()
    win.withdraw()
    pattern = gui.simpledialog.askstring(text, text, parent=win, initialvalue=initialvalue)
    win.destroy()
    return pattern

if __name__ == "__main__":

    print("VERBOSE = %s"%VERBOSE)
    
    running = True
    pattern = "easyclarinette"
    while running:
        pattern = prompt("Enter instrument to find or substitute", initialvalue=pattern)
        found = False
        if not pattern in (None, ""):
            instrument = pattern
            
            #~ else:
                #~ print("nothing found!")
        else: running = False

    