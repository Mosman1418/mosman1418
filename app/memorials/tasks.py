#!/usr/bin/env python
from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import csv
from django.contrib.auth.models import User
from app.memorials.models import *
from app.people.models import *
from app.places.models import *
from app.sources.models import *


def scrape_memorial(url):
    '''Scrape memorial data from the War Memorials in Australia site.'''
    page = BeautifulSoup(get_url(url))
    memorial = Memorial.objects.get(associated_sources__url=url)
    user = User.objects.get(username='tim')
    face = 1
    for table in page('table'):
        memorial_part, created = MemorialPart.objects.get_or_create(memorial=memorial, label='Face %s' % face, added_by=user)
        row_num = 1
        for row in table('tr'):
            cell_num = 1
            for cell in row('td'):
                name = cell.get_text(strip=True)
                if name:
                    print 'Row: %s Cell: %s -- %s' % (row_num, cell_num, name)
                    memorial_name, created = MemorialName.objects.get_or_create(memorial=memorial, memorial_part=memorial_part, name=name, row=row_num, column=cell_num, added_by=user)
                    family_name = name[:name.find(' ')].strip().title()
                    other_names = name[name.find(' ')+1:].strip()
                    if '(NSE)' in other_names:
                        other_names = other_names.replace('(NSE)', '')
                        rank = 'Nurse'
                    else:
                        rank = None
                    display_name = '{} {}'.format(other_names.replace('.', ''), family_name)
                    person, created = Person.objects.get_or_create(display_name=display_name, family_name=family_name, other_names=other_names, status='confirmed', public=True, added_by=user)
                    memorial_name.person = person
                    memorial_name.save()
                    if rank:
                        new_rank = Rank.objects.create(person=person, rank=rank, added_by=user)
                        new_rank.memorials.add(memorial)
                        new_rank.save()
                    if face == 1:
                        death = Death.objects.create(person=person, label="Died on service", cause_of_death="Died on service", added_by=user)
                        death.memorials.add(memorial)
                        death.save()
                    cell_num += 1
            row_num += 1
        face += 1


def load_memorials_csv():
    csv_path = '/Users/tim/mycode/mosman1418/mosman1418/data/memorials_names.csv'
    csv_file = open(csv_path, 'rb')
    csv_reader = csv.DictReader(csv_file)
    user = User.objects.get(username='tim')
    for row in csv_reader:
        if row['display']:
            if ['Memorial id'] != '1':
                print row['display']
                if not row['Memorial id'].isdigit():
                    source, created = Source.objects.get_or_create(title=row['Memorial id'], added_by=user)
                    memorial = None
                else:
                    memorial = Memorial.objects.get(id=row['Memorial id'])
                    source = None
                person, created = Person.objects.get_or_create(
                    display_name=row['display'],
                    added_by=user,
                    defaults={
                        'gender': row['Gender'],
                        'status': 'confirmed',
                        'public': True
                    }
                )
                if created:
                    person.family_name = row['Last Name']
                    person.other_names = row['Initials']
                    person.save()
                if memorial:
                    MemorialName.objects.get_or_create(
                        memorial=memorial,
                        person=person,
                        name='{}, {}'.format(row['Last Name'], row['Initials']),
                        notes=row['Notes'],
                        added_by=user
                    )
                if row['Rank']:
                    rank, created = Rank.objects.get_or_create(
                        rank=row['Rank'],
                        person=person,
                        added_by=user
                    )
                    if memorial:
                        rank.memorials.add(memorial)
                    if source:
                        rank.sources.add(source)
                    rank.save()
                if row['Status']:
                    death, created = Death.objects.get_or_create(
                        person=person,
                        cause_of_death=row['Status'],
                        added_by=user
                    )
                    if row['Campaign']:
                        death_place, created = Place.objects.get_or_create(
                            display_name=row['Campaign'],
                            added_by=user
                        )
                        death.location = death_place
                    if memorial:
                        death.memorials.add(memorial)
                    if source:
                        death.sources.add(source)
                    death.save()
                if row['Unit']:
                    org, created = Organisation.objects.get_or_create(
                        name=row['Unit'],
                        added_by=user
                    )
                    association = PersonOrgAssociation.objects.get(label='member of')
                    membership, created = PersonAssociatedOrganisation.objects.get_or_create(
                        person=person,
                        organisation=org,
                        association=association,
                        added_by=user
                    )
                    if memorial:
                        membership.memorials.add(memorial)
                    if source:
                        membership.sources.add(source)
                    membership.save()
                if row['Decorations']:
                    event_type = LifeEventType.objects.get(label='award')
                    lifeevent, created = LifeEvent.objects.get_or_create(
                        person=person,
                        label='{}'.format(
                            'Awarded {}'.format(row['Decorations']) if row['Decorations'] != 'Decorated' else 'Decorated'),
                        type_of_event=event_type,
                        added_by=user
                    )
                    if memorial:
                        lifeevent.memorials.add(memorial)
                    if source:
                        lifeevent.sources.add(source)
                    lifeevent.save()


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

