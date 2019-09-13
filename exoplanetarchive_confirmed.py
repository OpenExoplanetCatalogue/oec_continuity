#!/usr/bin/python 
import urllib
import os
import shutil
import xml.etree.ElementTree as ET 
import xmltools

#####################
# Exoplanet Archive
#####################
url_exoplanetarchive = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets&select=ra,st_raerr,st_rah,st_raherr,ra_str,dec,st_decerr,dec_str,st_glon,st_glonerr,st_glat,st_glaterr,st_elon,st_elonerr,st_elat,st_elaterr,st_posn,st_plx,st_plxerr1,st_plxerr2,st_plxlim,st_plxn,st_dist,st_disterr1,st_disterr2,st_distlim,st_distn,st_pmra,st_pmraerr,st_pmralim,st_pmdec,st_pmdecerr,st_pmdeclim,st_pm,st_pmerr,st_pmlim,st_pmn,st_radv,st_radverr1,st_radverr2,st_radvlim,st_radvn,st_uj,st_ujerr,st_ujlim,st_bj,st_bjerr,st_bjlim,st_vj,st_vjerr,st_vjlim,st_rc,st_rcerr,st_rclim,st_ic,st_icerr,st_iclim,st_j,st_jerr,st_jlim,st_h,st_herr,st_hlim,st_k,st_kerr,st_klim,st_wise1,st_wise1err,st_wise1lim,st_wise2,st_wise2err,st_wise2lim,st_wise3,st_wise3err,st_wise3lim,st_wise4,st_wise4err,st_wise4lim,st_irac1,st_irac1err,st_irac1lim,st_irac2,st_irac2err,st_irac2lim,st_irac3,st_irac3err,st_irac3lim,st_irac4,st_irac4err,st_irac4lim,st_mips1,st_mips1err,st_mips1lim,st_mips2,st_mips2err,st_mips2lim,st_mips3,st_mips3err,st_mips3lim,st_iras1,st_iras1err,st_iras1lim,st_iras2,st_iras2err,st_iras2lim,st_iras3,st_iras3err,st_iras3lim,st_iras4,st_iras4err,st_iras4lim,st_optmag,st_optmagerr,st_optmaglim,st_optband,st_photn,st_umbj,st_umbjerr,st_umbjlim,st_bmvj,st_bmvjerr,st_bmvjlim,st_vjmic,st_vjmicerr,st_vjmiclim,st_vjmrc,st_vjmrcerr,st_vjmrclim,st_jmh2,st_jmh2err,st_jmh2lim,st_hmk2,st_hmk2err,st_hmk2lim,st_jmk2,st_jmk2err,st_jmk2lim,st_bmy,st_bmyerr,st_bmylim,st_m1,st_m1err,st_m1lim,st_c1,st_c1err,st_c1lim,st_colorn,st_spstr,st_ssperr,st_splim,st_spn,st_teff,st_tefferr1,st_tefferr2,st_tefflim,st_teffn,st_logg,st_loggerr1,st_loggerr2,st_logglim,st_loggn,st_metfe,st_metfeerr1,st_metfeerr2,st_metfelim,st_metfen,st_metratio,st_lum,st_lumerr1,st_lumerr2,st_lumlim,st_lumn,st_rad,st_raderr1,st_raderr2,st_radlim,st_radn,st_mass,st_masserr1,st_masserr2,st_masslim,st_massn,st_dens,st_denserr1,st_denserr2,st_denslim,st_densn,st_age,st_ageerr1,st_ageerr2,st_agelim,st_agen,st_vsini,st_vsinierr1,st_vsinierr2,st_vsinilim,st_vsinin,st_acts,st_actserr,st_actslim,st_actsn,st_actr,st_actrerr,st_actrlim,st_actrn,st_actlx,st_actlxerr,st_actlxlim,st_actlxn,st_nts,st_nplc,st_nglc,st_nrvc,st_naxa,st_nimg,st_nspec,hd_name,hip_name,swasp_id,pl_name,pl_hostname,pl_letter,pl_pnum,pl_snum,pl_mnum,pl_status,pl_discmethod,pl_disc,pl_disc_refname,pl_publ_date,pl_facility,pl_telescope,pl_instrument,pl_locale,pl_def_refname,pl_rvflag,pl_imgflag,pl_astflag,pl_tranflag,pl_ttvflag,pl_kepflag,pl_k2flag,pl_nnotes,pl_cbflag,pl_omflag,pl_pelink,pl_edelink,pl_orbper,pl_orbpererr1,pl_orbpererr2,pl_orbperlim,pl_orbpern,pl_orbsmax,pl_orbsmaxerr1,pl_orbsmaxerr2,pl_orbsmaxlim,pl_orbsmaxn,pl_orbincl,pl_orbinclerr1,pl_orbinclerr2,pl_orbincllim,pl_orbincln,pl_orbtper,pl_orbtpererr1,pl_orbtpererr2,pl_orbtperlim,pl_orbtpern,pl_orbeccen,pl_orbeccenerr1,pl_orbeccenerr2,pl_orbeccenlim,pl_orbeccenn,pl_orblper,pl_orblpererr1,pl_orblpererr2,pl_orblperlim,pl_orblpern,pl_rvamp,pl_rvamperr1,pl_rvamperr2,pl_rvamplim,pl_rvampn,pl_conrat,pl_conraterr1,pl_conraterr2,pl_conratlim,pl_conratband,pl_conratn,pl_msinij,pl_msinijerr1,pl_msinijerr2,pl_msinijlim,pl_msinie,pl_msinieerr1,pl_msinieerr2,pl_msinielim,pl_msinin,pl_massj,pl_massjerr1,pl_massjerr2,pl_massjlim,pl_masse,pl_masseerr1,pl_masseerr2,pl_masselim,pl_massn,pl_bmassj,pl_bmassjerr1,pl_bmassjerr2,pl_bmassjlim,pl_bmasse,pl_bmasseerr1,pl_bmasseerr2,pl_bmasselim,pl_bmassn,pl_bmassprov,pl_radj,pl_radjerr1,pl_radjerr2,pl_radjlim,pl_rade,pl_radeerr1,pl_radeerr2,pl_radelim,pl_rads,pl_radserr1,pl_radserr2,pl_radslim,pl_radn,pl_dens,pl_denserr1,pl_denserr2,pl_denslim,pl_densn,pl_eqt,pl_eqterr1,pl_eqterr2,pl_eqtlim,pl_eqtn,pl_insol,pl_insolerr1,pl_insolerr2,pl_insollim,pl_insoln,pl_trandep,pl_trandeperr1,pl_trandeperr2,pl_trandeplim,pl_trandepn,pl_trandur,pl_trandurerr1,pl_trandurerr2,pl_trandurlim,pl_trandurn,pl_tranmid,pl_tranmiderr1,pl_tranmiderr2,pl_tranmidlim,pl_tranmidn,pl_tsystemref,pl_imppar,pl_impparerr1,pl_impparerr2,pl_impparlim,pl_impparn,pl_occdep,pl_occdeperr1,pl_occdeperr2,pl_occdeplim,pl_occdepn,pl_ratdor,pl_ratdorerr1,pl_ratdorerr2,pl_ratdorlim,pl_ratdorn,pl_ratror,pl_ratrorerr1,pl_ratrorerr2,pl_ratrorlim,pl_ratrorn,pl_mrtranmid,pl_mrtranmiderr1,pl_mrtranmiderr2,pl_mrtranmidlim,pl_mrtmrefid,pl_mrtmreflink,pl_mrtsystemref,pl_st_npar,pl_st_nref,rowupdate,gaia_plx,gaia_plxerr1,gaia_plxerr2,gaia_plxlim,gaia_dist,gaia_disterr1,gaia_disterr2,gaia_distlim,gaia_pmra,gaia_pmraerr,gaia_pmralim,gaia_pmdec,gaia_pmdecerr,gaia_pmdeclim,gaia_pm,gaia_pmerr,gaia_pmlim,gaia_gmag,gaia_gmagerr,gaia_gmaglim,pl_angsep,pl_angseperr1,pl_angseperr2,pl_controvflag"

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
