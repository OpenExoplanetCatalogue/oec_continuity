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
# Exoplanet EU
#####################
url_exoplaneteu = "http://exoplanet.eu/catalog/csv/"

def get():
    if "download" in sys.argv:
        answer = "y"
    else:
        answer = input("download new version?").lower()
    if answer=="y":
        urllib.request.urlretrieve (url_exoplaneteu, "exoplaneteu.csv")

def add_elem_with_errors(node, name, errorminus="", errorplus="", value=""):
    if len(errorplus)>0 and len(errorminus)>0 and len(value)>0:
        if float(errorplus) == 0. and float(value)==float(errorminus):
            ET.SubElement(node, name, upperlimit=value.strip()).text = ""
            return
        if float(errorminus) == 0. and float(value)==float(errorplus):
            ET.SubElement(node, name, lowerlimit=value.strip()).text = ""
            return
    if "nan" in errorminus or "inf" in errorminus:
        errorminus = ""
    if "e" in errorminus :
        errorminus = "%f"%float(errorminus)
    if "e" in errorplus :
        errorplus = "%f"%float(errorplus)
    if "nan" in errorplus or "inf" in errorplus:
        errorplus = ""
    if len(errorminus)==0 or len(errorplus)==0:
        ET.SubElement(node, name).text = value.strip()
        return
    if float(errorminus)==0. or float(errorplus)==0.:
        ET.SubElement(node, name).text = value.strip()
        return

    ET.SubElement(node, name, errorminus=errorminus.strip().replace("-",""), errorplus=errorplus.strip()).text = value.strip()


def parse():
    # delete old data
    xmltools.ensure_empty_dir("systems_exoplaneteu")

    # parse data into default xml format
    f = open("exoplaneteu.csv")

    with open("exoplaneteu.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(reader)
        for row in reader:
            p = {key: value for key, value in zip(headers, row)}

            
            systemnames = []
            if len(p["star_name"]):
                systemnames.append(p["star_name"].strip())
            if len(p["star_alternate_names"]):
                for extraname in p["star_alternate_names"].split(","):
                    systemnames.append(extraname.strip())
            if len(systemnames)==0:
                pname = p["name"]
                if pname[-2:] == " b":
                    pname = pname[:-2]
                systemnames.append(pname)
         
            systemnames[0] = systemnames[0].replace("/","-")
            outputfilename = systemnames[0]
            outputfilename = "systems_exoplaneteu/"+outputfilename+".xml"

            if os.path.exists(outputfilename):
                system = ET.parse(outputfilename).getroot()
                star = system.find(".//star")
            else:
                system = ET.Element("system")
                for sn in systemnames:
                    ET.SubElement(system, "name").text = sn
                
                try:
                    ra = float(p["ra"])/360.*24.
                except:
                    ra = 0.
                if ra!=0.:
                    rah = math.floor(ra)
                    ra -= rah
                    ram = math.floor(ra*60.)
                    ra -= ram/60.
                    ras = ra*60*60
                    ET.SubElement(system, "rightascension").text = "%02.0f %02.0f %05.2f"% (rah, ram, ras)
                else:
                    ET.SubElement(system, "rightascension").text = "00 00 00.00" # special object?
                
                try:
                    dec = float(p["dec"])
                except:
                    dec = 0.
                if dec>0.:
                    decd = math.floor(dec)
                    dec -= decd
                    decm = math.floor(dec*60.)
                    dec -= decm/60.
                    decs = dec*60*60
                    ET.SubElement(system, "declination").text = "+%02.0f %02.0f %05.2f"% (decd, decm, decs)
                elif dec<0.:
                    dec *= -1
                    decd = math.floor(dec)
                    dec -= decd
                    decm = math.floor(dec*60.)
                    dec -= decm/60.
                    decs = dec*60*60
                    ET.SubElement(system, "declination").text = "-%02.0f %02.0f %05.2f"% (decd, decm, decs)
                else:
                    ET.SubElement(system, "declination").text = "+00 00 00.00"


                if len(p["star_distance"])>1:
                    add_elem_with_errors(system, "distance", errorminus=p['star_distance_error_min'], errorplus=p['star_distance_error_max'], value=p["star_distance"])

                star = ET.SubElement(system,"star")
                for sn in systemnames:
                    ET.SubElement(star, "name").text = sn
                add_elem_with_errors(star,"radius",p['star_radius_error_min'], p['star_radius_error_max'],p["star_radius"])

                add_elem_with_errors(star, "magV", "", "",value= p["mag_v"])
                add_elem_with_errors(star, "magI", "", "",value= p["mag_i"])
                add_elem_with_errors(star, "magJ", "", "",value= p["mag_j"])
                add_elem_with_errors(star, "magH", "", "",value= p["mag_h"])
                add_elem_with_errors(star, "magK", "", "",value= p["mag_k"])
                add_elem_with_errors(star, "mass", errorminus=p['star_mass_error_min'], errorplus=p['star_mass_error_max'],value= p["star_mass"])
                add_elem_with_errors(star, "temperature", errorminus=p['star_teff_error_min'], errorplus=p['star_teff_error_max'],value= p["star_teff"])
                add_elem_with_errors(star, "metallicity", errorminus=p['star_metallicity_error_min'], errorplus=p['star_metallicity_error_max'],value= p["star_metallicity"])
                ET.SubElement(star, "spectraltype").text = p["star_sp_type"].replace(" ","")

            planet = ET.SubElement(star,"planet")
            for name in [p["name"]]+p["alternate_names"].split(","):
                ET.SubElement(planet, "name").text = name.strip()
            add_elem_with_errors(planet, "semimajoraxis", errorminus=p["semi_major_axis_error_min"], errorplus=p["semi_major_axis_error_max"], value= p["semi_major_axis"])
            add_elem_with_errors(planet, "eccentricity", errorminus=p['eccentricity_error_min'], errorplus=p['eccentricity_error_max'], value= p["eccentricity"])
            add_elem_with_errors(planet, "periastron", errorminus=p['omega_error_min'], errorplus=p['omega_error_max'], value= p["omega"])
            add_elem_with_errors(planet, "inclination", errorminus=p['inclination_error_min'], errorplus=p['inclination_error_max'], value= p["inclination"])
            add_elem_with_errors(planet, "period", errorminus=p['orbital_period_error_min'], errorplus=p['orbital_period_error_max'], value= p["orbital_period"])

            description = ""

           # if len(p["pl_disc_refname"])>5:
           #     description += "This planet was discovered by " + p["pl_disc_refname"] +". "
           #     if p["pl_locale"] == "Space":
           #         if len(p["pl_telescope"])>5:
           #             description += "The discovery was made with a space based telescope ("+p["pl_telescope"]+"). "
           #         else:
           #             description += "The discovery was made with a space based telescope. "
           #     if p["pl_locale"] == "Ground":
           #             description += "This was a ground based discovery. "
           # if len(p["pl_def_refname"])>5:
            description += "The parameters listed here were imported into the Open Exoplanet Catalogue from the exoplanet.eu website. " 

            description = html.unescape(description)
           # #print(description)
            ET.SubElement(planet, "description").text = description

            # check for both kinds of masses
            if p['mass'] == "" or p['mass'] == None:
                # use msini
                add_elem_with_errors(planet, "mass", errorminus=p['mass_sini_error_min'], errorplus=p['mass_sini_error_max'], value= p["mass_sini"])
            else: 
                # use mass jupiter
                add_elem_with_errors(planet, "mass", errorminus=p['mass_error_min'], errorplus=p['mass_error_max'], value= p["mass"])
            add_elem_with_errors(planet, "radius", errorminus=p['radius_error_min'], errorplus=p['radius_error_max'], value= p["radius"])
            if p['temp_measured'] == "" or p['temp_measured'] == None:
                add_elem_with_errors(planet, "temperature", errorminus=p['temp_calculated_error_min'], errorplus=p['temp_calculated_error_max'], value= p["temp_calculated"])
            else:
                add_elem_with_errors(planet, "temperature", errorminus="", errorplus="", value= p["temp_measured"])
            if p["detection_type"]=="Radial Velocity":
                ET.SubElement(planet, "discoverymethod").text = "RV"
            elif "Transit" in p["detection_type"]:
                ET.SubElement(planet, "discoverymethod").text = "transit"
            elif p["detection_type"]=="Imaging":
                ET.SubElement(planet, "discoverymethod").text = "imaging"
            elif p["detection_type"]=="Microlensing":
                ET.SubElement(planet, "discoverymethod").text = "microlensing"
            elif "Timing" in p["detection_type"] or "TTV" in p["detection_type"]:
                ET.SubElement(planet, "discoverymethod").text = "timing"
            else:
                print("new discovery method:", p["detection_type"])
            
            if "Transit" in p["detection_type"] or "Transit" in p["mass_detection_type"] or "Transit" in p["radius_detection_type"]:
                ET.SubElement(planet, "istransiting").text = "1"
            if len(p["discovered"].strip()):
                ET.SubElement(planet, "discoveryyear").text = p["discovered"].strip()
            else:
                ET.SubElement(planet, "discoveryyear").text = "2019" # some planets don't have a discovery year??
            ET.SubElement(planet, "list").text = "Confirmed planets"
            ET.SubElement(planet, "lastupdate").text = p["updated"][2:].strip().replace("-","/")

           # # Need to check if BJD
           # add_elem_with_errors(planet, "transittime", errorminus=p['pl_tranmiderr2'], errorplus=p['pl_tranmiderr1'], value= p["pl_tranmid"])
           # 
           # # all planets new by default. 
           # ET.SubElement(planet, "new").text = "1"

            # Cleanup and write file
            xmltools.removeemptytags(system)
            xmltools.indent(system)
            ET.ElementTree(system).write(outputfilename) 
            cleanup.checkonefile(outputfilename)

    print("Reading previous planet list")
    previous_planets = {}
    if os.path.exists("exoplaneteu_previous_planets.xml"):
        with open("exoplaneteu_previous_planets.xml", 'rt') as f:
            previous_planets_root = ET.parse(f).getroot()
            for planet in previous_planets_root.findall(".//planet"):
                name = planet.findtext("./name")
                first_seen = planet.findtext("./first_seen")
                previous_planets[name] = first_seen
    else:
        previous_planets_root = ET.Element("previous_planets")



    print("Now checking if any changes occured")

    for filename in glob.glob("systems_exoplaneteu/*.xml"):
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
                markasnew = True
            if markasnew:
                ET.SubElement(planet, "new").text = "1"
                changed = True
                print("New planet found: " + name)
                
        if changed:
            ET.ElementTree(root).write(filename) 
            cleanup.checkonefile(filename)
    
    xmltools.indent(previous_planets_root)
    ET.ElementTree(previous_planets_root).write("exoplaneteu_previous_planets.xml") 


if __name__=="__main__":
    get()
    parse()
