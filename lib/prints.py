#!/usr/bin/env python3

#A simple python library to print things beautifully.

def success(text):
    print('[+] \033[92m',text, '\033[0m')

def info(text):
    print('[*] \033[96m',text, '\033[0m')

def infor(text):
    print('[*] \033[96m',text, '\033[0m', end = '\r')

def warning(text):
    print('[+] \033[93m',text, '\033[0m')

def fail(text):
    print('[!] \033[91m',text, '\033[0m')
