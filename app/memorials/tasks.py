#!/usr/bin/env python
from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import csv
from mosman1418.memorials.models import *
from mosman1418.people.models import Person

def scrape_memorial(url):
    '''Scrape memorial data from the War Memorials in Australia site.'''
    page = BeautifulSoup(get_url(url))
    memorial = Memorial.objects.get(associated_sources__url=url)
    face = 1
    for table in page('table'):
        memorial_part, created = MemorialPart.objects.get_or_create(memorial=memorial, label='Face %s' % face)
        row_num = 1
        for row in table('tr'):
            cell_num = 1
            for cell in row('td'):
                name = cell.get_text(strip=True)
                if name: 
                    print 'Row: %s Cell: %s -- %s' % (row_num, cell_num, name)
                    memorial_name, created = MemorialName.objects.get_or_create(memorial=memorial, memorial_part=memorial_part, name=name, row=row_num, column=cell_num)
                    family_name = name[:name.find(' ')].strip().title()
                    other_names = name[name.find(' ')+1:].strip()
                    person = Person.objects.create(family_name=family_name, other_names=other_names)
                    memorial_name.person = person
                    memorial_name.save()
                    cell_num += 1
            row_num += 1
        face += 1
                
def make_csv():
    people_killed = Person.objects.filter(memorialname__memorial_part=2)
    killed_csv = csv.writer(open('memorial_killed.csv', 'wb'), dialect='excel')
    for killed in people_killed:
        killed_csv.writerow([killed.id, killed.memorialname_set.all()[0], killed.family_name, killed.other_names])
    people_survived = Person.objects.exclude(memorialname__memorial_part=2)
    survived_csv = csv.writer(open('memorial_survived.csv', 'wb'), dialect='excel')
    for survived in people_survived:
        survived_csv.writerow([survived.id, survived.memorialname_set.all()[0], survived.family_name, survived.other_names])

def get_url(url):
    '''
    Retrieve page.
    '''
    user_agent = 'Mozilla/5.0 (X11; Linux i686; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
    headers = { 'User-Agent' : user_agent }
    req = Request(url, None, headers)
    try:
        response = urlopen(req)
    except HTTPError, URLError:
        raise
    return response
    