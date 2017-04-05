#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Bot import *
from requests import get, post

class Example(WebHookBot):
    def __init__(self, name):
        super(Example, self).__init__(name)
        self.logger(f"Endpoint: {self.endpoint}")
        self.SLEEP_TIME = 10 

    def main(self):
        self.logger("I'm something else!")

ex = Example("example")
ex.run()
