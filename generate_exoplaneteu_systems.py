#!/usr/bin/python 
import urllib.request
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools
import math
import csv
import html
import cleanup

#####################
# Exoplanet EU
#####################
url_exoplaneteu = "http://exoplanet.eu/catalog/csv/"

def get():
    answer = input("download new version?").lower()
    if answer=="y":
        urllib.request.urlretrieve (url_exoplaneteu, "exoplaneteu.csv")

def add_elem_with_errors(node, name, errorminus="", errorplus="", value=""):
    if "nan" in errorminus or "inf" in errorminus:
        errorminus = ""
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
                pname = p["# name"]
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
                
                ra = float(p["ra"])/360.*24.
                if ra!=0.:
                    rah = math.floor(ra)
                    ra -= rah
                    ram = math.floor(ra*60.)
                    ra -= ram/60.
                    ras = ra*60*60
                    ET.SubElement(system, "rightascension").text = "%02.0f %02.0f %02.2f"% (rah, ram, ras)
                
                dec = float(p["dec"])
                if dec>0.:
                    decd = math.floor(dec)
                    dec -= decd
                    decm = math.floor(dec*60.)
                    dec -= decm/60.
                    decs = dec*60*60
                    ET.SubElement(system, "declination").text = "+%02.0f %02.0f %02.2f"% (decd, decm, decs)
                if dec<0.:
                    dec *= -1
                    decd = math.floor(dec)
                    dec -= decd
                    decm = math.floor(dec*60.)
                    dec -= decm/60.
                    decs = dec*60*60
                    ET.SubElement(system, "declination").text = "-%02.0f %02.0f %02.2f"% (decd, decm, decs)


                if len(p["star_distance"])>1:
                    add_elem_with_errors(system, "distance", errorminus=p['star_distance_error_min'], errorplus=p['star_distance_error_max'], value=p["star_distance"])

           #     star = ET.SubElement(system,"star")
           #     for sn in systemnames:
           #         ET.SubElement(star, "name").text = sn
           #     add_elem_with_errors(star,"radius",p['st_raderr2'], p['st_raderr1'],p["st_rad"])

           #     add_elem_with_errors(star, "magV", errorminus=p['st_vjerr'], errorplus=p['st_vjerr'],value= p["st_vj"])
           #     add_elem_with_errors(star, "magI", errorminus=p['st_icerr'], errorplus=p['st_icerr'],value= p["st_ic"])
           #     add_elem_with_errors(star, "magJ", errorminus=p['st_jerr'], errorplus=p['st_jerr'],value= p["st_j"])
           #     add_elem_with_errors(star, "magH", errorminus=p['st_herr'], errorplus=p['st_herr'],value= p["st_h"])
           #     add_elem_with_errors(star, "magK", errorminus=p['st_kerr'], errorplus=p['st_kerr'],value= p["st_k"])
           #     add_elem_with_errors(star, "mass", errorminus=p['st_masserr2'], errorplus=p['st_masserr1'],value= p["st_mass"])
           #     add_elem_with_errors(star, "temperature", errorminus=p['st_tefferr2'], errorplus=p['st_tefferr1'],value= p["st_teff"])
           #     add_elem_with_errors(star, "metallicity", errorminus=p['st_metfeerr2'], errorplus=p['st_metfeerr1'],value= p["st_metfe"])
           #     ET.SubElement(star, "spectraltype").text = p["st_spstr"].replace(" ","")

           # planet = ET.SubElement(star,"planet")
           # for sn in systemnames:
           #     ET.SubElement(planet, "name").text = sn+" "+p["pl_letter"]
           # add_elem_with_errors(planet, "semimajoraxis", errorminus=p["pl_orbsmaxerr2"], errorplus=p["pl_orbsmaxerr1"], value= p["pl_orbsmax"])
           # add_elem_with_errors(planet, "eccentricity", errorminus=p['pl_orbeccenerr2'], errorplus=p['pl_orbeccenerr1'], value= p["pl_orbeccen"])
           # add_elem_with_errors(planet, "periastron", errorminus=p['pl_orblpererr2'], errorplus=p['pl_orblpererr1'], value= p["pl_orblper"])
           # add_elem_with_errors(planet, "inclination", errorminus=p['pl_orbinclerr2'], errorplus=p['pl_orbinclerr1'], value= p["pl_orbincl"])
           # add_elem_with_errors(planet, "period", errorminus=p['pl_orbpererr2'], errorplus=p['pl_orbpererr1'], value= p["pl_orbper"])

           # description = ""

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
           #     description += "The parameters listed here are those reported by " + p["pl_def_refname"] + " and were imported into the Open Exoplanet Catalogue from the NASA Exoplanet Archive. " 

           # description = html.unescape(description)
           # #print(description)
           # ET.SubElement(planet, "description").text = description

           # # check for both kinds of masses
           # if p['pl_massj'] == "" or p['pl_massj'] == None:
           #     # use msini
           #     add_elem_with_errors(planet, "mass", errorminus=p['pl_msinijerr2'], errorplus=p['pl_msinijerr1'], value= p["pl_msinij"])
           # else: 
           #     # use mass jupiter
           #     add_elem_with_errors(planet, "mass", errorminus=p['pl_massjerr2'], errorplus=p['pl_massjerr1'], value= p["pl_massj"])
           # add_elem_with_errors(planet, "radius", errorminus=p['pl_radjerr2'], errorplus=p['pl_radjerr1'], value= p["pl_radj"])
           # add_elem_with_errors(planet, "temperature", errorminus=p['pl_eqterr2'], errorplus=p['pl_eqterr1'], value= p["pl_eqt"])
           # if p["pl_discmethod"]=="Radial Velocity":
           #     ET.SubElement(planet, "discoverymethod").text = "RV"
           # elif p["pl_discmethod"]=="Transit":
           #     ET.SubElement(planet, "discoverymethod").text = "transit"
           #     ET.SubElement(planet, "istransiting").text = "1"
           # elif p["pl_discmethod"]=="Imaging":
           #     ET.SubElement(planet, "discoverymethod").text = "imaging"
           # elif p["pl_discmethod"]=="Microlensing":
           #     ET.SubElement(planet, "discoverymethod").text = "microlensing"
           # elif p["pl_discmethod"]=="Eclipse Timing Variations":
           #     ET.SubElement(planet, "discoverymethod").text = "timing"
           # elif p["pl_discmethod"]=="Pulsation Timing Variations":
           #     ET.SubElement(planet, "discoverymethod").text = "timing"
           # elif p["pl_discmethod"]=="Pulsar Timing":
           #     ET.SubElement(planet, "discoverymethod").text = "timing"
           # elif p["pl_discmethod"]=="Transit Timing Variations":
           #     ET.SubElement(planet, "discoverymethod").text = "timing"
           # else:
           #     print("new discovery method:"+ p["pl_discmethod"])
           # ET.SubElement(planet, "discoveryyear").text = p["pl_disc"]
           # ET.SubElement(planet, "list").text = "Confirmed planets"
           # ET.SubElement(planet, "lastupdate").text = p["rowupdate"][2:].replace("-","/")

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



if __name__=="__main__":
    get()
    parse()
