#!/usr/bin/python

import xml.etree.ElementTree as ET
import glob
import os
import hashlib
import sys
import datetime
import time
import re
import json

# Nicely indents the XML output
def indent(elem, level=0):
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
def get_onefile(filename):
    # Open file
    f = open(filename, 'rt')

    # Try to parse file
    try:
        root = ET.parse(f).getroot()
        planets = root.findall(".//planet")
    except ET.ParseError as error:
        print('{}, {}'.format(filename, error))
        return
    finally:
        f.close()
   
    date = "20/00/00"
    for planet in planets:
        datep = planet.find("./lastupdate")
        if date<datep.text:
            date = datep.text
    return date

def update_onefile(filename, date):
    # Open file
    f = open(filename, 'rt')

    # Try to parse file
    try:
        root = ET.parse(f).getroot()
        planets = root.findall(".//planet")
    except ET.ParseError as error:
        print('{}, {}'.format(filename, error))
        return
    finally:
        f.close()
   
    for planet in planets:
        datep = planet.find("./lastupdate")
        new = planet.find("./new")
        if new is not None:
            planet.remove(new)
        if datep.text == date:
            ET.SubElement(planet, "new").text = "1"

    # Cleanup XML
    indent(root)

    # Write XML to file.
    with open(filename, 'wb') as outfile:
        ET.ElementTree(root).write(outfile, encoding="UTF-8", xml_declaration=False)

if __name__=="__main__":
    folder = "systems"
    if len(sys.argv)>1:
        folder = sys.argv[1]

    date = "20/00/00"
    for filename in glob.glob(folder+"/*.xml"):
        datep = get_onefile(filename)
        if date<datep:
            date = datep
    
    for filename in glob.glob(folder+"/*.xml"):
        update_onefile(filename, date)







