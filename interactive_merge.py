#!/usr/bin/python 
import urllib.request
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools
import html
import math
import glob
from flask import Flask, redirect, url_for
app = Flask(__name__)

def cleanplanet(name):
    name = name.replace(" ", "")
    name = name.replace("-", "")
    name = name.replace("(", "") 
    name = name.replace(")", "") 
    name = name.replace("A", "") 
    name = name.replace("B", "") 
    name = name.replace("C", "") 
    name = name.replace("D", "") 
    return name


@app.route('/compare/<name1>/<name2>/')
def compare(name1,name2):
    h = "<frameset cols=\"50%,50%\">"
    h += "<frame src=\"/systems_exoplanetarchive/"+name1+"\"/>"
    h += "<frame src=\"/systems_open_exoplanet_catalogue/"+name2+"\"/>"
    h += "</frameset>"
    return h

@app.route('/ignore/<name>/<y>/<m>/<d>')
def ignore(name,y,m,d):
    with open("ignore/"+name, 'w') as f:
        f.write(y+"/"+m+"/"+d)
    return "ignored"

@app.route('/copy/<name>/<y>/<m>/<d>')
def copy(name,y,m,d):
    shutil.copyfile("systems_exoplanetarchive/"+name,"systems_open_exoplanet_catalogue/"+name)
    return "copied, " + ignore(name, y, m, d);

@app.route('/<directory>/<name>')
def showfile(directory,name):
    h = """
    <html>
    <head>
    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/default.min.css">
    <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js"></script>
    <script>hljs.configure({tabReplace: '    '});hljs.initHighlightingOnLoad();</script>
    </head>
    <body>
    """
    h += "<pre style='white-space: pre-wrap;'><code class='xml'>"
    with open(directory+"/"+name, 'r') as content_file:
        h += html.escape("".join(content_file.readlines()))
    h += "</pre></code>"
    h += """
    </body>
    </html>
    """
    return h

def radec(ra,dec):
    ra = ra.split(" ")
    dec = dec.split(" ")
    raf = float(ra[0])
    decf = float(dec[0])
    sign = 1.
    if decf<0.:
        sign = -1.
    raf += float(ra[1])/24.
    decf += sign*float(dec[1])/60.
    raf += float(ra[2])/24./60.
    decf += sign*float(dec[2])/60./60.
    return (raf/12.*math.pi, decf/180.*math.pi)


@app.route('/')
def index():
    ignored = {}
    for f in glob.iglob('ignore/*.xml'):
        with open(f, 'r') as content_file:
            ignored[os.path.basename(f)] = "".join(content_file.readlines())

    planets_oec = {}
    planets_oec_radec = []
    oec_files = []
    for f in glob.iglob('systems_open_exoplanet_catalogue/*.xml'):
        oec_files.append(os.path.basename(f))
        system = ET.parse(f)
        for planet in system.findall(".//planet"):
            lastupdate = planet.findtext("lastupdate")
            for name in planet.findall(".//name"):
                planets_oec[name.text] = [f, lastupdate]
        dec = system.findtext("declination")
        ra = system.findtext("rightascension")
        if dec:
            raf, decf = radec(ra, dec)
            decf += math.pi/2.
            planets_oec_radec.append([raf, decf, f])
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
            planetnames = []
            for name in planet.findall(".//name"):
                planetnames.append(name.text)
            planets.append(planetnames)
        closest_d = 1000.
        closest_name = ""
        dec_ea = system.findtext("declination")
        ra_ea = system.findtext("rightascension")
        if dec:
            raf_ea, decf_ea = radec(ra_ea, dec_ea)
            decf_ea += math.pi/2.
            sin_decf_ea = math.sin(decf_ea)
            cos_decf_ea = math.cos(decf_ea)
            for raf, decf, name in planets_oec_radec:
                d = 2.-2.*(math.sin(decf)*sin_decf_ea*math.cos(raf-raf_ea)+math.cos(decf)*cos_decf_ea)
                if d<closest_d:
                    closest_name = name
                    closest_d = d

        if len(lastupdate)>1:
            systems_ea[f] = [lastupdate, discoveryyear, planets, closest_name, closest_d]
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
    h += "<th>oec file (closest)</th>"
    h += "<th>last oec update</th>"
    h += "<th>actions</th>"
    h += "</tr>"
    i = 0
    shown = 0
    while i < len(sk) and shown < 5000:
        k = sk[i]
        i+=1
        previouslyignored = 0
        if os.path.basename(k) in ignored.keys():
            if ignored[os.path.basename(k)] == systems_ea[k][0]:
                continue
            previouslyignored = 1
        shown += 1
        h += "<tr>"
        h += "<td><a href='/" + k + "'>"+ os.path.basename(k) + "</a></td>"
        h += "<td>" + systems_ea[k][0] + "</td>"
        h += "<td>" + str(systems_ea[k][1]) + "</td>"
        oecd = ["", ""]
        pl = []
        for p in systems_ea[k][2]:
            pmain = p[0]
            c = 0
            for pmain in p:
                if pmain in planets_oec.keys():
                    c = 1
                    oecd = planets_oec[pmain]
                    break
                else:
                    cleanpmain = cleanplanet(pmain)
                    if cleanpmain in planets_oec_clean.keys():
                        c = 2
                        oecd = planets_oec_clean[cleanpmain]
                        break

            if c==0:
                pmain = p[0]
                pl.append(pmain)
            elif c==1:
                pl.append("<span style=\"background-color: #FF0000\">"+pmain+"</span>")
            elif c==2:
                pl.append("<span style=\"background-color: #FFAA00\">"+pmain+"</span>")

        h += "<td>" + ", ".join(pl) + "</td>"

        h += "<td><a href='/" + oecd[0] + "'>"+ os.path.basename(oecd[0]) +"</a>"
        if (oecd[0]!=systems_ea[k][3]):
            h += " <a style=\"background-color: #00FFFF\" href='/" + systems_ea[k][3] + "'>" + os.path.basename(systems_ea[k][3]) + "</a>"
            h += " (%.2f)"%(100.*math.sqrt(systems_ea[k][4])) 
        h += "</td>"

        try:
            h += "<td>" + oecd[1] + "</td>"
        except:
            h += "<td>unknown</td>"  # unknown last update
        h += "<td>"
        if len(oecd[0])==0:
            if len(systems_ea[k][3]):
                h += "<a href='/compare/"+os.path.basename(k) +"/" +os.path.basename(systems_ea[k][3])+"'>compare</a> "
            else:
                h += "compare "
        else:
            h += "<a href='/compare/"+os.path.basename(k) +"/" +os.path.basename(oecd[0])+"'>compare</a> "
        if os.path.basename(k) in oec_files:
            h += "<a style=\"background-color: #FF0000\" href='/copy/"+os.path.basename(k)+"/"+systems_ea[k][0]+"'>copy</a> "
        else:
            h += "<a href='/copy/"+os.path.basename(k)+"/"+systems_ea[k][0]+"'>copy</a> "
        h += "<a href='/ignore/"+os.path.basename(k)+"/"+systems_ea[k][0]+"'>ignore</a> "
        if previouslyignored==1:
            h+="*"
        h += "</td>"
        h += "</tr>"
    h += "</table>"
    h += """
    </body>
    </html>
    """
    return h




if __name__ == '__main__':
    app.run(debug=True)


