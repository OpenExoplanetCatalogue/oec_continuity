#!/usr/bin/python 
import urllib.request
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools
import html
import glob
from flask import Flask
app = Flask(__name__)

def cleanplanet(name):
    name = name.replace(" ", "")
    name = name.replace("-", "")
    name = name.replace("(", "") 
    name = name.replace(")", "") 
    name = name.replace("A", "") 
    name = name.replace("B", "") 
    name = name.replace("C", "") 
    return name


@app.route('/systems_open_exoplanet_catalogue/<name>')
def soec(name,d="/systems_open_exoplanet_catalogue/"):
    h = "<xmp>"
    with open("."+d+name, 'r') as content_file:
        h += "".join(content_file.readlines())
    h += "</xmp>"
    return h

@app.route('/systems_exoplanetarchive/<name>')
def sea(name):
    return soec(name,"/systems_exoplanetarchive/")

@app.route('/')
def hello():
    planets_oec = {}
    for f in glob.iglob('systems_open_exoplanet_catalogue/*.xml'):
        system = ET.parse(f)
        for planet in system.findall(".//planet"):
            lastupdate = planet.findtext("lastupdate")
            for name in planet.findall(".//name"):
                planets_oec[name.text] = [f, lastupdate]
    planets_oec_clean = {}          
    for p in planets_oec.keys():
        p_clean = cleanplanet(p)
        planets_oec_clean[p_clean] = planets_oec[p]

    systems_ea = {}
    for f in glob.iglob('systems_exoplanetarchive/*.xml'):
        system = ET.parse(f)
        lastupdate = ""
        discoveryyear = 0
        planets = []
        for planet in system.findall(".//planet"):
            lastupdate = planet.findtext("lastupdate")
            discoveryyear = max(int(planet.findtext("discoveryyear")), discoveryyear)
            for name in planet.findall(".//name"):
                planets.append(name.text)
        if len(lastupdate)>1:
            systems_ea[f] = [lastupdate, discoveryyear, planets]
    def lu(elem):
        return systems_ea.get(elem)[0]
    sk = sorted(systems_ea, key=lu, reverse=True)
    # newest systems
    h = """
    <html>
    <head>
    </head>
    <body>
    """
    h += "<table border=1>"
    h += "<tr>"
    h += "<th>file</th>"
    h += "<th>last-update</th>"
    h += "<th>discovery year</th>"
    h += "<th>planets found</th>"
    h += "<th>planet already in oec?</th>"
    h += "<th>oec file</th>"
    h += "<th>last oec update</th>"
    h += "<th>actions</th>"
    h += "</tr>"
    for i in range(10):
        h += "<tr>"
        k = sk[i]
        h += "<td><a href='/" + k + "'>"+ os.path.basename(k) + "</a></td>"
        h += "<td>" + systems_ea[k][0] + "</td>"
        h += "<td>" + str(systems_ea[k][1]) + "</td>"
        h += "<td>" + str(", ".join(systems_ea[k][2])) + "</td>"
        c = 0
        cc = 0
        oecd = ["", ""]
        for p in systems_ea[k][2]:
            if p in planets_oec.keys():
                c += 1
                oecd = planets_oec[p]
            else:
                if p in planets_oec_clean.keys():
                    cc += 1
                    oecd = planets_oec_clean[p]

        h += "<td>" + "%d/%d/%d" %(c, cc, len(systems_ea[k][2])) + "</td>"
        h += "<td><a href='/" + oecd[0] + "'>"+ os.path.basename(oecd[0]) + "</a></td>"
        h += "<td>" + oecd[1] + "</td>"
        h += "<td>  <a href=''>add</a>  <a href=''>ignore</a> </td>"
        h += "</tr>"
    h += "</table>"
    h += """
    </body>
    </html>
    """
    return h




if __name__ == '__main__':
    app.run(debug=True)


