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

def main():
    now = datetime.now()
    startdate = datetime(2013, 9, 22, 6)
    enddate = datetime(2013, 9, 23, 20)

    log = open("log.txt", "a")
    log.write("-----------\n")
    log.write("starting up at %s\n" % now.isoformat())

    if now < startdate:
        log.write("too early for screenshots, will start on %s\n" % startdate.isoformat())
        sys.exit()
    if now > enddate:
        log.write("too late for screenshots, stopped on %s\n" % enddate.isoformat())
        sys.exit()
    
    log.write("reading config.yml\n")    
    config = yaml.load(open("config.yml"))
    log.write("reading urls.yml\n")
    urls = yaml.load(open("urls.yml"))
    
    folder = os.path.join(config["save_path"], datetime.now().strftime("%Y-%m-%dT%H-%M-%S%z"))
    log.write("save folder: %s\n" % folder)

    jobs = []
    for country, sites in urls.items():
        for site_name, site_url in sites.items():
            jobs.append({
                "filename": get_filename(country, site_name),
                "url": site_url,
                "site_name": site_name
            })
    
    log.write("starting to download\n")
    #for job in jobs:
    #    print "* %s - %s" % (job["site_name"], job["url"])
    
    if not os.path.exists(folder):
        log.write("save folder doesn't exist\n")
        os.makedirs(folder)
        log.write("created save folder\n")

    # use Firefox as driver because screenshots capture the whole page, not just the viewport
    driver = webdriver.Firefox()
    driver.set_window_size(1280, 960) # optional

    # load all sites before we start taking screenshots
    # because of cookie warnings, subscription offers etc.
    for job in jobs:
        log.write("preloading %s\n" % job["url"])
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
            log.write("saved %s\n" % job["filename"])
        except Exception, e:
            print "could not download %s" % job["filename"]
            log.write("could not download %s\n" % job["filename"])
            
    driver.quit()
    log.write("finished\n")
    log.close()

if __name__ == "__main__":
    main()
