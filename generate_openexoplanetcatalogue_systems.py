#!/usr/bin/python 
import urllib.request
import sys
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools
import math
import datetime
import csv
import html
import cleanup
import glob

#####################
# Open Exoplanet Catalogue
# Only checking for new planets
#####################

def parse():
    print("Reading previous planet list")
    previous_planets = {}
    with open("openexoplanetcatalogue_previous_planets.xml", 'rt') as f:
        previous_planets_root = ET.parse(f).getroot()
        for planet in previous_planets_root.findall(".//planet"):
            name = planet.findtext("./name")
            first_seen = planet.findtext("./first_seen")
            previous_planets[name] = first_seen


    print("Now checking if any changes occured")
    new_planets_found_today = [] 

    for filename in glob.glob("../open_exoplanet_catalogue/systems/*.xml"):
        f = open(filename, 'rt')
        root = ET.parse(f).getroot()
        systemname = root.findtext("./name")
        changed = False
        for planet in root.findall(".//planet"):
            name = planet.findtext("./name")
            markasnew = False
            #markasnew = True
            if name in previous_planets:
                d1 = datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")
                d2 = datetime.datetime.strptime(previous_planets[name], "%Y-%m-%d")
                age = (d1-d2)
                if age.days <= 5 and previous_planets[name]!="2023-10-09":
                    markasnew = True

            if name not in previous_planets:
                new_planet = ET.SubElement(previous_planets_root, "planet")
                ET.SubElement(new_planet, "name").text = name
                ET.SubElement(new_planet, "first_seen").text = datetime.datetime.today().strftime('%Y-%m-%d')
                new_planets_found_today.append(name)
                markasnew = True
            if markasnew:
                ET.SubElement(planet, "new").text = "1"
                changed = True
                print("New planet found: " + name)
                
        if changed:
            ET.ElementTree(root).write(filename) 
            cleanup.checkonefile(filename)
    
    xmltools.indent(previous_planets_root)
    ET.ElementTree(previous_planets_root).write("openexoplanetcatalogue_previous_planets.xml") 


if __name__=="__main__":
    parse()
