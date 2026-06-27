#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

LOAD_JSON_VERSION = "1.0"

def loadJson(filename, default_fname = "defaultConfig.json"):
    if not os.path.exists(filename):
        filename = default_fname
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
    return default

if __name__ == '__main__':

    from sys import argv

    print("%s v.%s"%(argv[0], LOAD_JSON_VERSION) )

    """ U N I T A R Y    T E S T ***---"""

    config = loadJson("config.json")
    
    print(config)


