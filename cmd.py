# -*- coding: utf-8 -*-
# by @m4xx1m
# regex - @D4n13l3k00

import re

class Command():
    def __init__(self, text):
        cm = re.compile(r"^\.(.*)\d*")
        self.arg = ""
        self.cmd = ""
        self.args = []
        if not bool(cm.findall(text)):
            return
        self.cmd = cm.findall(text)[0]
        self.arg = cm.sub("", text)
        self.args = self.arg.split(" ")
            
            
