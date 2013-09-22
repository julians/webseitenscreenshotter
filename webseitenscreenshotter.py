#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import locale
import time
import re
import os
from datetime import datetime
import yaml
import unidecode
from selenium import webdriver

locale.setlocale(locale.LC_ALL, 'de_DE')

def get_filename(country, site):
    return "%s-%s.png" % (
        unidecode.unidecode(unicode(country.lower())),
        re.sub(r"\s", "_", unidecode.unidecode(unicode(site)))
    )

def log(file, str):
    file.write("%s\n" % str)
    file.flush()

def main():
    now = datetime.now()
    startdate = datetime(2013, 9, 22, 6)
    enddate = datetime(2013, 9, 23, 20)

    logfile = open("log.txt", "a")
    log(logfile, "-----------")
    log(logfile, "starting up at %s" % now.isoformat())

    if now < startdate:
        log(logfile, "too early for screenshots, will start on %s" % startdate.isoformat())
        sys.exit()
    if now > enddate:
        log(logfile, "too late for screenshots, stopped on %s" % enddate.isoformat())
        sys.exit()
    
    log(logfile, "reading config.yml")
    config = yaml.load(open("config.yml"))
    log(logfile, "reading urls.yml")
    urls = yaml.load(open("urls.yml"))
    
    folder = os.path.join(config["save_path"], datetime.now().strftime("%Y-%m-%dT%H-%M-%S%z"))
    log(logfile, "save folder: %s" % folder)

    jobs = []
    for country, sites in urls.items():
        for site_name, site_url in sites.items():
            jobs.append({
                "filename": get_filename(country, site_name),
                "url": site_url,
                "site_name": site_name
            })
    
    log(logfile, "starting to download")
    #for job in jobs:
    #    print "* %s - %s" % (job["site_name"], job["url"])
    
    if not os.path.exists(folder):
        log(logfile, "save folder doesn't exist")
        os.makedirs(folder)
        log(logfile, "created save folder")

    # use Firefox as driver because screenshots capture the whole page, not just the viewport
    driver = webdriver.Firefox()
    driver.set_window_size(1280, 960) # optional

    # load all sites before we start taking screenshots
    # because of cookie warnings, subscription offers etc.
    for job in jobs:
        log(logfile, "preloading %s" % job["url"])
        driver.get(job["url"])
    
    # take screenshots
    for job in jobs:
        #print job["site_name"]
        
        try:
            driver.get(job["url"])
            if job["site_name"] == "Haaretz":
                try:
                    driver.execute_script("closePopUpSubscriptionReminder()")
                except Exception, e:
                    print e
            time.sleep(5)
            driver.save_screenshot(os.path.join(folder, job["filename"]))
            log(logfile, "saved %s" % job["filename"])
        except Exception, e:
            print "could not download %s" % job["filename"]
            log(logfile, "could not download %s" % job["filename"])
            
    driver.quit()
    log(logfile, "finished")
    logfile.close()

if __name__ == "__main__":
    main()
