from selenium import webdriver
import re
from bs4 import BeautifulSoup
import webbrowser, sys, requests

def getExemptStateRules(state):
    pathToPhantom = '/Users/datinkm1/Desktop/phantomjs-2.1.1-macosx/bin'
    browser = webdriver.PhantomJS(executable_path = '/Users/datinkm1/Desktop/phantomjs-2.1.1-macosx/bin/phantomjs')
    url = 'https://revenue.alabama.gov/incometax/2016_forms/16f40ablk.pdf'
    browser.get(url)
    
    browser.switch_to_default_content()
    frameset = browser.find_elements_by_tag_name('frame')
    for a in frameset:
        print a.get_attribute('h3')
    browser.switch_to_frame("left")
    table = browser.find_element_by_tag_name('table')
    tbody = table.find_element_by_tag_name('tbody')
    
    body_rows = tbody.find_elements_by_tag_name('tr')
    for row in body_rows:
        data = row.find_elements_by_tag_name('td')
        for data1 in data:
            link = data1.find_elements_by_tag_name('a')
            file_row = []
            for datum in link:
                datumText = datum.text.encode('utf8')
                regex = re.compile('pers*', re.IGNORECASE)
                match = regex.search(datumText)
                if 'Personal Exemption' in datumText:
                    link =  datum.get_attribute('href')
                    browser.get(link)
                    browser.switch_to_default_content()
    
    resp = requests.get('http://www.alabamatax.net/leftborder.htm')

    soup = BeautifulSoup(resp.content, 'html.parser')
    
    webText = soup.get_text()