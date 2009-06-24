#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Copyright (C) 2009 RaNaN, Willnix
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License,
#or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
###
import os
import sys
import time

from module.remote.ClientSocket import SocketThread

class pyLoadCli:
    def __init__(self, adress, port, pw):
        self.thread = SocketThread(adress, int(port), pw, self)
        self.getch = _Getch()
        self.input = ""
        self.pos = [0,0]
        self.inputline = 0
        self.menuline = 0

        self.links_added = 0

        os.system("clear")
        self.println(1, blue("py") + yellow("Load") + white(" Command Line Interface"))
        self.println(2, "")

        self.file_list = {}
        self.thread.push_exec("get_links")

        self.start()

    def start(self):
        while True:
            #inp = raw_input()
            inp = self.getch.impl()
            if ord(inp) == 3:
                os.system("clear")
                sys.exit() # ctrl + c
            elif ord(inp) == 13:
                self.handle_input()
                self.input = ""   #enter
                self.print_input()
            elif ord(inp) == 127:
                self.input = self.input[:-1] #backspace
                self.print_input()
            elif ord(inp) == 27: #ugly symbol
                pass
            else:
                self.input += inp
                self.print_input()

    def format_time(self, seconds):
        seconds = int(seconds)
        
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return "%.2i:%.2i:%.2i" % (hours, minutes, seconds)

    def println(self, line, content):
        print "\033[" + str(line) + ";0H\033[2K" + str(content) + "\033[" + str((self.inputline if self.inputline > 0 else self.inputline + 1) - 1) + ";0H"

    def print_input(self):
        self.println(self.inputline, white(" Input: ") + self.input)
        self.println(self.inputline+1, "")
        self.println(self.inputline+2, "")
        self.println(self.inputline+3, "")
        self.println(self.inputline+4, "")

    def data_arrived(self, obj):
        """Handle incoming data"""
        if obj.command == "update":
            #print updated information
            self.println(1, blue("py") + yellow("Load") + white(" Command Line Interface"))
            self.println(2, "")
            self.println(3, white("%s Downloads:" % (len(obj.data))))
            line = 4
            speed = 0
            for download in obj.data:
                if download["status"] == "downloading":
                    percent = download["percent"]
                    z = percent / 4
                    speed += download['speed']
                    self.println(line, cyan(download["name"]))
                    line += 1
                    self.println(line, blue("[") + yellow(z * "#" + (25-z) * " ") + blue("] ") + green(str(percent) + "%") + " Speed: " + green(str(int(download['speed'])) + " kb/s") + " Finished in: " + green(self.format_time(download['eta'])))
                    line += 1
                if download["status"] == "waiting":
                    self.println(line, cyan(download["name"]))
                    line += 1
                    self.println(line, "waiting: " + green(self.format_time(download["wait_until"]- time.time())))
                    line += 1
            self.println(line, "")
            line += 1
            self.println(line, "Status: " + red("paused") if obj.status['pause'] else "Status: " + red("running") + " total Speed: " + red(str(int(speed)) + " kb/s") + " Files in queue: " + red(str(obj.status["queue"])))
            line += 1
            self.println(line, "")
            line += 1
            self.menuline = line
            
            self.build_menu()
        elif obj.command == "file_list" or obj.function == "get_links":
            self.file_list = obj.data

    def build_menu(self):
        line = self.menuline
        self.println(line, white("Menu:"))
        line += 1 
        if self.pos[0] == 0:# main menu
            self.println(line, "")
            line += 1
            self.println(line, mag("1.") + " Add Links")
            line += 1
            self.println(line, mag("2.") + " Remove Links")
            line += 1
            self.println(line, mag("3.") + " Pause Server")
            line += 1
            self.println(line, mag("4.") + " Kill Server")
            line += 1
            self.println(line, mag("5.") + " Quit")
            line += 1
            self.println(line, "")
            line += 1
            self.println(line, "")
        elif self.pos[0] == 1:#add links    
            self.println(line, "Parse the links you want to add.")
            line += 1
            self.println(line, "")
            line += 1
            self.println(line, "")
            line += 1
            self.println(line, "Links added: " + mag(str(self.links_added)))
            line += 1
            self.println(line, "")
            line += 1
            self.println(line, "")
            line += 1
            self.println(line, mag("0.") + " back to main menu")
            line += 1
            self.println(line, "")
        elif self.pos[0] == 2:#remove links
            self.println(line, "Type the number of the link you want to delete.")
            line += 1
            i = 0
            for id in range(self.pos[1],self.pos[1]+5):
                    if id < 0 or id >= len(self.file_list['order']):
                        continue
                    item = self.file_list['order'][id]
                    self.println(line, mag(str(item)) + ": " + self.file_list[item].url)
                    line += 1
                    i += 1
            for x in range(5-i):
                self.println(line,"")
                line += 1

            self.println(line, mag("p") +" - previous" + " | " + mag("n") + " - next")
            line += 1
            self.println(line, mag("0.") + " back to main menu")
        
        self.inputline = line + 1
        self.print_input()

    def handle_input(self):
        inp = self.input
        if inp == "0":
            self.pos = [0,0]
            self.build_menu()
            return True

        if self.pos[0] == 0:
            if inp == "1":
                self.links_added = 0
                self.pos[0] = 1
            elif inp == "2":
                self.pos[0] = 2
                self.pos[1] = 0
            elif inp == "3":
                self.pos[0] = 3
            elif inp == "4":
                self.pos[0] = 4
            elif inp == "5":
                os.system('clear')
                sys.exit()
        elif self.pos[0] == 1: #add links
            if inp[:7] == "http://":
                self.thread.push_exec("add_links", [(inp, None)])
                self.links_added += 1
        elif self.pos[0] == 2: #remove links
            if inp == "p":
                self.pos[1] -= 5
            elif inp == "n":
                self.pos[1] += 5
            else:
                self.thread.push_exec("remove_links", [[inp]])

        self.build_menu()

class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

def blue(string):
    return "\033[1;34m" + string + "\033[0m"

def green(string):
    return "\033[1;32m" + string + "\033[0m"

def yellow(string):
    return "\033[1;33m" + string + "\033[0m"

def red(string):
    return "\033[1;31m" + string + "\033[0m"

def cyan(string):
    return "\033[1;36m" + string + "\033[0m"

def mag(string):
    return "\033[1;35m" + string + "\033[0m"

def white(string):
    return "\033[1;37m" + string + "\033[0m"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        #address = raw_input("Adress:")
        #port = raw_input("Port:")
        #password = raw_input("Password:")
        address = "localhost"
        port = "7272"
        password = "pwhere"
        cli = pyLoadCli(address, port, password)
    else:
        cli = pyLoadCli( * sys.argv[1:])
