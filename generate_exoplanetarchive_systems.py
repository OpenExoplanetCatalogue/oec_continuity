#!/usr/bin/python 
import urllib.request
import os
import shutil
import datetime
import glob
import xml.etree.ElementTree as ET 
import xmltools
import html
import hashlib
import re
import csv
import cleanup

#####################
# Exoplanet Archive
#####################
url_exoplanetarchive = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+pscomppars&format=csv"
now = datetime.datetime.now()
        

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text).strip()

def get():
    answer = input("download new version?").lower()
    if answer=="y":
        shutil.copyfile("exoplanetarchive.csv","exoplanetarchive_backup.csv")
        urllib.request.urlretrieve (url_exoplanetarchive, "exoplanetarchive.csv")
        with open("dates_exoplanetarchive.txt","a+") as w:
            w.write(now.strftime("%y/%m/%d\n"))


def add_elem_with_errors(node, name, errorminus="", errorplus="", value=""):
    if len(errorminus)==0 or len(errorplus)==0:
        ET.SubElement(node, name).text = value
        return
    if float(errorminus)==0. or float(errorplus)==0.:
        ET.SubElement(node, name).text = value
        return

    ET.SubElement(node, name, errorminus=errorminus.replace("-",""), errorplus=errorplus).text = value

def getHash(f):
    system = ET.parse(f).getroot()
    planets = system.findall(".//planet")
    for planet in planets:
        es = planet.findall("./lastupdate")
        for e in es:
            planet.remove(e)
        es = planet.findall("./new")
        for e in es:
            planet.remove(e)
    s = ET.tostring(system, encoding='utf8', method='text')
    md5 = hashlib.md5()
    md5.update(s)
    return md5.hexdigest()

def parse():
    oldhashes = {}
    for f  in glob.glob("systems_exoplanetarchive_backup_may20/*.xml"):
        systemname = f.split("/")[1].split(".")[0]
        oldhashes[systemname] = getHash(f)
    
    # delete old data
    xmltools.ensure_empty_dir("systems_exoplanetarchive")

    # parse data into default xml format
    with open('exoplanetarchive.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pl_name = row["pl_name"]
            systemname, system =  parserow(row)
            outputfilename = "systems_exoplanetarchive/"+systemname+".xml"

            ET.ElementTree(system).write(outputfilename) 
            cleanup.checkonefile(outputfilename)

    print("Now checking if any changes occured")

    for filename in glob.glob("systems_exoplanetarchive/*.xml"):
        f = open(filename, 'rt')
        newhash = getHash(f)
        f = open(filename, 'rt')
        root = ET.parse(f).getroot()
        systemname = root.findtext("./name")
        try:
            oldhash = oldhashes[systemname]
        except:
            oldhash = "n/a"
        if oldhash != newhash:
            for lastupdate in root.findall(".//planet/lastupdate"):
                lastupdate.text = now.strftime("%y/%m/%d")
            ET.ElementTree(root).write(filename) 
            cleanup.checkonefile(filename)
            print("new  hash ", systemname)

def parserow(p):
        _systemnames = [p["hostname"]]
        if len(p["hd_name"])>4:
            _systemnames.append(p["hd_name"])
        if len(p["hip_name"])>4:
            _systemnames.append(p["hip_name"])
        systemnames = []
        for _sn in _systemnames:
            if _sn not in systemnames:
                systemnames.append(_sn)
        
        outputfilename = "systems_exoplanetarchive/"+systemnames[0]+".xml"
        if os.path.exists(outputfilename):
            system = ET.parse(outputfilename).getroot()
            star = system.find(".//star")
        else:
            system = ET.Element("system")
            for sn in systemnames:
                ET.SubElement(system, "name").text = sn
            
            if len(p["rastr"]):
                tempra = ""
                tempra += p["rastr"].split("h")[0] # hours
                tempra += " " + p["rastr"].split("h")[1].split("m")[0] # minutes
                tempra += " %.2i" % (round(float(p["rastr"].split("h")[1].split("m")[1].split("s")[0]))) # seconds
                ET.SubElement(system, "rightascension").text = tempra

                try:
                    tempdec = ""
                    tempdec += p["decstr"].split("d")[0] # hours
                    tempdec += " " + p["decstr"].split("d")[1].split("m")[0] # minutes
                    tempdec += " %.2i" % (round(float(p["decstr"].split("d")[1].split("m")[1].split("s")[0]))) # seconds
                    ET.SubElement(system, "declination").text = tempdec
                except:
                    print("Declination parsing error for "+outputfilename)
            else:
                print("Warning: no coordinates for "+outputfilename)

            if len(p["sy_dist"])>1:
                add_elem_with_errors(system, "distance", errorminus=p['sy_disterr2'], errorplus=p['sy_disterr1'], value=p["sy_dist"])

            star = ET.SubElement(system,"star")
            for sn in systemnames:
                ET.SubElement(star, "name").text = sn
            add_elem_with_errors(star,"radius",p['st_raderr2'], p['st_raderr1'],p["st_rad"])

            add_elem_with_errors(star, "magV", errorminus=p['sy_vmagerr2'], errorplus=p['sy_vmagerr1'],value= p["sy_vmag"])
            add_elem_with_errors(star, "magJ", errorminus=p['sy_jmagerr2'], errorplus=p['sy_jmagerr1'],value= p["sy_jmag"])
            add_elem_with_errors(star, "magH", errorminus=p['sy_hmagerr2'], errorplus=p['sy_hmagerr1'],value= p["sy_hmag"])
            add_elem_with_errors(star, "magK", errorminus=p['sy_kmagerr2'], errorplus=p['sy_kmagerr1'],value= p["sy_kmag"])
            add_elem_with_errors(star, "magI", errorminus=p['sy_imagerr2'], errorplus=p['sy_imagerr1'],value= p["sy_imag"])
            add_elem_with_errors(star, "mass", errorminus=p['st_masserr2'], errorplus=p['st_masserr1'],value= p["st_mass"])
            add_elem_with_errors(star, "temperature", errorminus=p['st_tefferr2'], errorplus=p['st_tefferr1'],value= p["st_teff"])
            add_elem_with_errors(star, "metallicity", errorminus=p['st_meterr2'], errorplus=p['st_meterr1'],value= p["st_met"])
            ET.SubElement(star, "spectraltype").text = p["st_spectype"].replace(" ","")

        planet = ET.SubElement(star,"planet")
        for sn in systemnames:
            ET.SubElement(planet, "name").text = sn+" "+p["pl_letter"]
        add_elem_with_errors(planet, "semimajoraxis", errorminus=p["pl_orbsmaxerr2"], errorplus=p["pl_orbsmaxerr1"], value= p["pl_orbsmax"])
        add_elem_with_errors(planet, "eccentricity", errorminus=p['pl_orbeccenerr2'], errorplus=p['pl_orbeccenerr1'], value= p["pl_orbeccen"])
        add_elem_with_errors(planet, "periastron", errorminus=p['pl_orblpererr2'], errorplus=p['pl_orblpererr1'], value= p["pl_orblper"])
        add_elem_with_errors(planet, "inclination", errorminus=p['pl_orbinclerr2'], errorplus=p['pl_orbinclerr1'], value= p["pl_orbincl"])
        add_elem_with_errors(planet, "period", errorminus=p['pl_orbpererr2'], errorplus=p['pl_orbpererr1'], value= p["pl_orbper"])

        description = ""

        if len(p["disc_refname"])>5:
            description += "This planet was discovered by " + remove_tags(p["disc_refname"]) +". "
            if p["disc_locale"] == "Space":
                if len(p["disc_telescope"])>5:
                    description += "The discovery was made with a space based telescope ("+p["disc_telescope"]+"). "
                else:
                    description += "The discovery was made with a space based telescope. "
            if p["disc_locale"] == "Ground":
                    description += "This was a ground based discovery. "
            description += "The parameters listed here have been imported into the Open Exoplanet Catalogue from the NASA Exoplanet Archive. " 

        description = html.unescape(description)
        #print(description)
        ET.SubElement(planet, "description").text = description

        # check for both kinds of masses
        # use mass jupiter
        add_elem_with_errors(planet, "mass", errorminus=p['pl_bmassjerr2'], errorplus=p['pl_bmassjerr1'], value= p["pl_bmassj"])
        add_elem_with_errors(planet, "radius", errorminus=p['pl_radjerr2'], errorplus=p['pl_radjerr1'], value= p["pl_radj"])
        add_elem_with_errors(planet, "temperature", errorminus=p['pl_eqterr2'], errorplus=p['pl_eqterr1'], value= p["pl_eqt"])
        discoverymethod = p["discoverymethod"].lower()
        if discoverymethod=="radial velocity":
            ET.SubElement(planet, "discoverymethod").text = "RV"
        elif discoverymethod=="transit":
            ET.SubElement(planet, "discoverymethod").text = "transit"
            ET.SubElement(planet, "istransiting").text = "1"
        elif discoverymethod=="imaging":
            ET.SubElement(planet, "discoverymethod").text = "imaging"
        elif discoverymethod=="microlensing":
            ET.SubElement(planet, "discoverymethod").text = "microlensing"
        elif discoverymethod=="eclipse timing variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif discoverymethod=="pulsation timing variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif discoverymethod=="pulsar timing":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif discoverymethod=="transit timing variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        else:
            print("new discovery method:"+ discoverymethod)
        ET.SubElement(planet, "discoveryyear").text = p["disc_year"]
        ET.SubElement(planet, "list").text = "Confirmed planets"
        ET.SubElement(planet, "lastupdate").text = (p["disc_pubdate"][2:]+"-01").replace("-","/")

        # Need to check if BJD
        add_elem_with_errors(planet, "transittime", errorminus=p['pl_tranmiderr2'], errorplus=p['pl_tranmiderr1'], value= p["pl_tranmid"])
        
        # all planets new by default. 
        ET.SubElement(planet, "new").text = "1"

        # Cleanup and write file
        xmltools.removeemptytags(system)
        xmltools.indent(system)
        return systemnames[0], system


#        ET.ElementTree(system).write(outputfilename) 
#        cleanup.checkonefile(outputfilename)


if __name__=="__main__":
    get()
    parse()
