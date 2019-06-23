#!/usr/bin/python 
import urllib
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools

#####################
# Exoplanet Archive
#####################
url_exoplanetarchive = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets"

debug = True

def get():
    xmltools.ensure_empty_dir("tmp_data")
    if debug:
        shutil.copy2("confirmed.csv","tmp_data/exoplanetarchive.csv")
        return
    urllib.urlretrieve (url_exoplanetarchive, "tmp_data/exoplanetarchive.csv")

def parse():
    # delete old data
    xmltools.ensure_empty_dir("systems_exoplanetarchive")

    # parse data into default xml format
    f = open("tmp_data/exoplanetarchive.csv")
    header = [x.strip() for x in f.readline().split(",")]
    for line in f:
        p = dict(zip(header, [x.strip() for x in line.split(",")]))
        outputfilename = "systems_exoplanetarchive/"+p["pl_hostname"]+".xml"
        if os.path.exists(outputfilename):
            system = ET.parse(outputfilename).getroot()
            star = system.find(".//star")
        else:
            system = ET.Element("system")
            ET.SubElement(system, "name").text = p["pl_hostname"]
            
            tempra = ""
            tempra += p["ra_str"].split("h")[0] # hours
            tempra += " " + p["ra_str"].split("h")[1].split("m")[0] # minutes
            tempra += " %.2i" % (round(float(p["ra_str"].split("h")[1].split("m")[1].split("s")[0]))) # seconds
            ET.SubElement(system, "rightascension").text = tempra

            tempdec = ""
            tempdec += p["dec_str"].split("d")[0] # hours
            tempdec += " " + p["dec_str"].split("d")[1].split("m")[0] # minutes
            tempdec += " %.2i" % (round(float(p["dec_str"].split("d")[1].split("m")[1].split("s")[0]))) # seconds
            ET.SubElement(system, "declination").text = tempdec

            star = ET.SubElement(system,"star")
            ET.SubElement(star, "name").text = p["pl_hostname"]
            ET.SubElement(star, "radius", errorminus=p['st_raderr2'], errorplus=p['st_raderr1']).text = p["st_rad"]
            ET.SubElement(star, "magV", errorminus=p['st_vjerr'], errorplus=p['st_vjerr']).text = p["st_vj"]
            ET.SubElement(star, "magI", errorminus=p['st_icerr'], errorplus=p['st_icerr']).text = p["st_ic"]
            ET.SubElement(star, "magJ", errorminus=p['st_jerr'], errorplus=p['st_jerr']).text = p["st_j"]
            ET.SubElement(star, "magH", errorminus=p['st_herr'], errorplus=p['st_herr']).text = p["st_h"]
            ET.SubElement(star, "magK", errorminus=p['st_kerr'], errorplus=p['st_kerr']).text = p["st_k"]
            ET.SubElement(star, "mass", errorminus=p['st_masserr2'], errorplus=p['st_masserr1']).text = p["st_mass"]
            ET.SubElement(star, "temperature", errorminus=p['st_tefferr2'], errorplus=p['st_tefferr1']).text = p["st_teff"]
            ET.SubElement(star, "metallicity", errorminus=p['st_metfeerr2'], errorplus=p['st_metfeerr1']).text = p["st_metfe"]

        planet = ET.SubElement(star,"planet")
        ET.SubElement(planet, "name").text = p["pl_hostname"]+" "+p["pl_letter"]
        ET.SubElement(planet, "semimajoraxis", errorminus=p["pl_orbsmaxerr2"], errorplus=p["pl_orbsmaxerr1"]).text = p["pl_orbsmax"]
        ET.SubElement(planet, "eccentricity", errorminus=p['pl_orbeccenerr2'], errorplus=p['pl_orbeccenerr1']).text = p["pl_orbeccen"]
        ET.SubElement(planet, "periastron", errorminus=p['pl_orblpererr2'], errorplus=p['pl_orblpererr1']).text = p["pl_orblper"]
        ET.SubElement(planet, "inclination", errorminus=p['pl_orbinclerr2'], errorplus=p['pl_orbinclerr1']).text = p["pl_orbincl"]
        ET.SubElement(planet, "period", errorminus=p['pl_orbpererr2'], errorplus=p['pl_orbpererr1']).text = p["pl_orbper"]
        # check for both kinds of masses
        if p['pl_massj'] == "" or p['pl_massj'] == None:
            # use msini
            ET.SubElement(planet, "mass", errorminus=p['pl_msinijerr2'], errorplus=p['pl_msinijerr1']).text = p["pl_msinij"]
        else: 
            # use mass jupiter
            ET.SubElement(planet, "mass", errorminus=p['pl_massjerr2'], errorplus=p['pl_massjerr1']).text = p["pl_massj"]
        ET.SubElement(planet, "radius", errorminus=p['pl_radjerr2'], errorplus=p['pl_radjerr1']).text = p["pl_radj"]
        ET.SubElement(planet, "temperature", errorminus=p['pl_eqterr2'], errorplus=p['pl_eqterr1']).text = p["pl_eqt"]
        if p["pl_discmethod"]=="Radial Velocity":
            ET.SubElement(planet, "discoverymethod").text = "RV"
        elif p["pl_discmethod"]=="Transit":
            ET.SubElement(planet, "discoverymethod").text = "transit"
        elif p["pl_discmethod"]=="Imaging":
            ET.SubElement(planet, "discoverymethod").text = "imaging"
        elif p["pl_discmethod"]=="Microlensing":
            ET.SubElement(planet, "discoverymethod").text = "microlensing"
        elif p["pl_discmethod"]=="Eclipse Timing Variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif p["pl_discmethod"]=="Pulsation Timing Variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif p["pl_discmethod"]=="Pulsar Timing":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        elif p["pl_discmethod"]=="Transit Timing Variations":
            ET.SubElement(planet, "discoverymethod").text = "timing"
        else:
            print("new discovery method:"+ p["pl_discmethod"])
        ET.SubElement(planet, "discoveryyear").text = p["pl_disc"]
        ET.SubElement(planet, "list").text = "Confirmed planets"
        ET.SubElement(planet, "lastupdate").text = p["rowupdate"][2:].replace("-","/")

        # Need to check if BJD
        ET.SubElement(planet, "transittime", errorminus=p['pl_tranmiderr2'], errorplus=p['pl_tranmiderr1']).text = p["pl_tranmid"]

        # Cleanup and write file
        xmltools.removeemptytags(system)
        xmltools.indent(system)
        ET.ElementTree(system).write(outputfilename) 



if __name__=="__main__":
    get()
    parse()
