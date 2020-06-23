#!/usr/bin/python 
import urllib.request
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools
import html
import glob

def create_list():
    allsystems = {}
    for f in glob.iglob('systems_exoplanetarchive/*.xml'):
        system = ET.parse(f)
        for planet in system.findall(".//planet"):
            lastupdate = planet.findtext("lastupdate")
            if len(lastupdate)>1:
                allsystems[f] = lastupdate
    sk = sorted(allsystems, key=allsystems.get, reverse=True)
    # newest systems
    for i in range(10):
        k = sk[i]
        print(k, allsystems[k])




if __name__=="__main__":
    create_list()
