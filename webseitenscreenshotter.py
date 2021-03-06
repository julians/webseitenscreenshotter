#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import locale
import time
import re
import os
import logging
import signal
from datetime import datetime
import yaml
import unidecode
from selenium import webdriver

locale.setlocale(locale.LC_ALL, 'de_DE')

def signal_handler(signal, frame):
    logging.warning("process killed")
    sys.exit(0)

def get_filename(country, site):
    return "%s-%s-%s.png" % (
        unidecode.unidecode(unicode(country.lower())),
        re.sub(r"\s", "_", unidecode.unidecode(unicode(site))),
        datetime.now().strftime("%Y-%m-%dT%H-%M-%S%z")
    )

def main():
    now = datetime.now()
    startdate = datetime(2013, 9, 22, 6)
    enddate = datetime(2013, 9, 23, 20)
    
    running = open("%s.run" % now.strftime("%Y-%m-%dT%H-%M-%S%z"), "w")
    running.write("ran on %s\n" % now.isoformat())
    running.close()
    
    logging.basicConfig(filename='webseitenscreenshotter.log', level=logging.INFO, format="%(levelname)s:%(message)s")
    
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("-----------")
    logging.info("starting up at %s" % now.isoformat())

    if now < startdate:
        logging.info("too early for screenshots, will start on %s" % startdate.isoformat())
        sys.exit()
    if now > enddate:
        logging.info("too late for screenshots, stopped on %s" % enddate.isoformat())
        sys.exit()
    
    logging.info("reading config.yml")
    config = yaml.load(open("config.yml"))
    logging.info("reading urls.yml")
    urls = yaml.load(open("urls.yml"))
    
    folder = os.path.join(config["save_path"], now.strftime("%Y-%m-%dT%H-%M-%S%z"))
    logging.info("save folder: %s" % folder)

    jobs = []
    for country, sites in urls.items():
        for site_name, site_url in sites.items():
            jobs.append({
                "country": country,
                "url": site_url,
                "site_name": site_name
            })
    
    logging.info("starting to download")

    if not os.path.exists(folder):
        logging.info("save folder doesn't exist")
        os.makedirs(folder)
        logging.info("created save folder")

    # use Firefox as driver because screenshots capture the whole page, not just the viewport
    driver = webdriver.Firefox()
    driver.set_window_size(1280, 960) # optional

    # load all sites before we start taking screenshots
    # because of cookie warnings, subscription offers etc.
    for job in jobs:
        logging.info("preloading %s" % job["url"])
        driver.get(job["url"])
        time.sleep(1)
        for x in range(1, 35):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/35*%d);" % x)
            time.sleep(0.035)
        time.sleep(1)
    
    # take screenshots
    for job in jobs:
        filename = get_filename(job["country"], job["site_name"])
        
        try:
            driver.get(job["url"])
            if job["site_name"] == "Haaretz":
                try:
                    driver.execute_script("closePopUpSubscriptionReminder()")
                except Exception, e:
                    logging.warning("Error executing Haaretz script hack")
                    print e
            time.sleep(1)
            for x in range(1, 35):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/35*%d);" % x)
                time.sleep(0.035)
            time.sleep(2)
            driver.save_screenshot(os.path.join(folder, filename))
            logging.info("saved %s" % filename)
        except Exception, e:
            print "could not download %s" % job["filename"]
            logging.warning("could not download %s" % filename)
            
    driver.quit()
    logging.info("finished")

if __name__ == "__main__":
    main()
