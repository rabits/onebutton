#!/usr/bin/env python

from lib.jsonrpctcp import config
from lib.jsonrpctcp import connect

if __name__ == '__main__':
    config.append_string = '\n'
    c = connect('localhost', 8888)
    print(c.getversion())
    pass
