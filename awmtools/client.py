from bs4 import BeautifulSoup
from urllib.request import urlopen, Request, HTTPError
import urllib
import re

try:
    from utilities import retry
except ImportError:
    from awmtools.utilities import retry

'''
A basic scraper/client library for WWI resources held by
the Australian War Memorial.

AVAILABLE CLIENTS:

RollClient() - Roll of Honour database
(http://www.awm.gov.au/research/people/roll_of_honour/)

EmbarkationClient() - WWI Embarkation Roll
(http://www.awm.gov.au/research/people/nominal_rolls/first_world_war_embarkation/)

RedCrossClient() - RedCross Wounded and Missing Files
(http://www.awm.gov.au/research/people/wounded_and_missing/)

HonoursClient() - Honours and Awards database
(http://www.awm.gov.au/research/people/honours_and_awards/)

CollectionClient() - Collection database
(http://www.awm.gov.au/search/collections/)

USAGE:

import client
c = client.RollClient()
c.get_details(url=[url])

Subsequent calls to the same entry don't need to provide a url. For example:

import client
c = client.CollectionClient()
c.get_licence(url='http://cas.awm.gov.au/item/P07922.001')

> 'Copyright expired - public domain'

c.get_img_url()

> 'http://www.awm.gov.au/collection/images/screen/P07922.001.jpg'

SAMPLE RESULTS (from get_details()):

Roll of Honour

{'also_known_as': [u'Frederick Neville Smith'],
 'cause_of_death': u'Killed in action',
 'cemetery_or_memorial_details': None,
 'date_of_death': u'11 April 1917',
 'name': u'Walter John Neville Newbold',
 'pdf_link': None,
 'place_of_death': u'France',
 'rank': u'Private',
 'service': u'Australian Army',
 'service_number': u'6806',
 'title': u'Roll of Honour - Walter John Neville Newbold',
 'unit': u'13th Battalion (Infantry)'}

 Embarkation Roll

 {'date_of_embarkation': u'23 November 1916',
 'name': u'Walter Abbott',
 'pdf_link': '/collection/records/awm8/23/39/awm8-23-39-4-0126.pdf',
 'place_of_embarkation': u'Melbourne',
 'rank': u'Private',
 'roll_title': u'22 Infantry Battalion - 13 to 18 Reinforcements (July-November 1916)',
 'service_number': u'6274',
 'ship_embarked_on': u'HMAT Hororata',
 'ship_number': u'A20',
 'title': u'First World War Embarkation Roll - Walter Abbott'}

 Red Cross Files

 {'name': u'Smith Edward Briggs',
 'pdf_link': 'http://www.awm.gov.au/collection/records/1drl0428/2/53/5/1drl-0428-2-53-5-5.pdf',
 'rank': u'Private',
 'service_number': u'10693',
 'title': u'Red Cross Wounded and Missing - Smith Edward Briggs',
 'unit': u'3rd Division Signal Company Engineers'}

 Honours and Awards

 {'award': u'Mention in Despatches',
 'date_of_commonwealth_of_australia_gazette': u'11 October 1917',
 'date_of_london_gazette': u'6 July 1917',
 'date_of_recommendation': None,
 'location_in_commonwealth_of_australia_gazette': u'Page 2664, position 103',
 'location_in_london_gazette': u'Page 6773, position 99',
 'name': u'Robert Smith Gibson',
 'pdf_link': None,
 'rank': u'Acting Company Sergeant Major',
 'recommendation': None,
 'service': u'Army',
 'service_number': u'1028',
 'title': u'Honours and Awards - Robert Smith Gibson',
 'unit': u'6th Co AASC'}

 Collection

 {'access': None,
 'artist': None,
 'collection': u'Photograph',
 'copying_provision': None,
 'date_made': u'c 1918',
 'description': u'Portrait of Private (Pte) Smith and Nurse Bertha Smith (nee Newcombe) on their wedding day. Pte Smith served with the AIF, as denoted by the rising sun badges on his collar. Nurse Smith served with the British Red Cross (see P03149.001).',
 'id_number': u'P03149.002',
 'img_url': '/collection/images/screen/P03149.002.jpg',
 'licence': u'Copyright expired - public domain',
 'maker': None,
 'measurement': None,
 'medium': None,
 'object_type': None,
 'permalink': u'http://www.awm.gov.au/collection/P03149.002',
 'photographer': None,
 'physical_description': u'Black & white',
 'place_made': None,
 'places_made': None,
 'summary': None,
 'title': None}

'''


class BaseClient():
    '''
    Base class providing common methods, don't use this directly.
    '''

    AWM_URL = 'http://www.awm.gov.au'

    def __init__(self):
        self.soup = None

    # Uncomment the next line to retry in the case of a timeout error.
    #@retry(ServerError, tries=10, delay=1)
    def _get_url(self, url):
        ''' Try to retrieve the supplied url.'''
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            if e.code == 503 or e.code == 504:
                raise ServerError("The server didn't respond")
            elif e.code == 404:
                raise UsageError('Please provide a valid URL.')
            else:
                raise
        else:
            return response

    def _get_soup(self, soup, url):
        '''
        Check to see if there's any soup. If not use the supplied url
        to make some.
        '''
        if not soup and not url:
            if self.soup is not None:
                soup = self.soup
            else:
                raise UsageError('Please supply a valid URL.')
        elif not soup:
            response = self._get_url(url)
            soup = BeautifulSoup(response.read())
        self.soup = soup
        return soup


class WWIBiogClient(BaseClient):
    '''
    Base class providing common methods for all the biographical
    databases of the Australian War Memorial. Don't use this directly.
    '''

    def get_title(self, soup=None, url=None):
        ''' Get the title of this entry. '''
        soup = self._get_soup(soup, url)
        return soup.find('h1', 'pagetitle').string.strip()

    def get_name(self, soup=None, url=None):
        ''' Get the name of the person described by this entry. '''
        soup = self._get_soup(soup, url)
        title = self.get_title(soup)
        return title.split(' - ')[1].strip()

    def _get_field_value(self, soup, field):
        ''' Get the text value of the requested field. '''
        try:
            value = ''
            for sibling in soup.find('strong', text=field).next_siblings:
                print (sibling.string)
                value += sibling.string
        except AttributeError:
            value = ''
        return value

    def _get_field_values(self, soup, field):
        ''' Get a list of values from the requested field. '''
        try:
            value_list = soup.find('strong', text=field).parent.parent.find_all('li')
            values = [name.string.strip() for name in value_list]
        except AttributeError:
            values = []
        return values

    def get_pdf_link(self, soup=None, url=None):
        ''' Get a url to an attached pdf. '''
        soup = self._get_soup(soup, url)
        try:
            pdf_link = '{}{}'.format(
                                self.AWM_URL,
                                soup.find('div', 'pdf').find('a')['href']
                                )
        except AttributeError:
            pdf_link = None
        return pdf_link

    def _process_fieldname(self, field):
        ''' Slugify a fieldname. '''
        return field.lower().replace(' ', '_').replace(':', '')

    def get_details(self, soup=None, url=None):
        ''' Return all the extracted details from this entry. '''
        soup = self._get_soup(soup, url)
        details = {}
        details['title'] = self.get_title(soup)
        details['name'] = self.get_name(soup)
        for field in self.FIELDS['single_value']:
            fieldname = self._process_fieldname(field)
            details[fieldname] = self._get_field_value(soup, field)
        for field in self.FIELDS['multiple_value']:
            fieldname = self._process_fieldname(field)
            details[fieldname] = self._get_field_values(soup, field)
        details['pdf_link'] = self.get_pdf_link(soup)
        return details


class RollClient(WWIBiogClient):
    '''
    Basic scraper/client for extracting structured data from a WWI entry in
    the Australian War Memorial's Roll of Honour database.
    '''

    FIELDS = {
                'single_value':
                [
                    'Service Number:',
                    'Rank:',
                    'Unit:',
                    'Service:',
                    'Date of death:',
                    'Place of death:',
                    'Cause of death:',
                    'Cemetery or memorial details:'
                ],
                'multiple_value':
                [
                    'Also known as:'
                ]
            }


class EmbarkationClient(WWIBiogClient):
    '''
    Basic scraper/client for extracting structured data from an entry in
    the Australian War Memorial's WWI Embarkation Roll database.
    '''

    FIELDS = {
                'single_value':
                [
                    'Service Number:',
                    'Rank:',
                    'Roll title:',
                    'Date of embarkation:',
                    'Place of embarkation:',
                    'Ship embarked on:',
                    'Ship number:'
                ],
                'multiple_value':
                []
            }


class RedCrossClient(WWIBiogClient):
    '''
    Basic scraper/client for extracting structured data from an entry in
    the Australian War Memorial's WWI Red Cross Missing and Wounded database.
    '''

    FIELDS = {
                'single_value':
                [
                    'Service Number:',
                    'Rank:',
                    'Unit:',
                ],
                'multiple_value':
                []
            }


class HonoursClient(WWIBiogClient):
    '''
    Basic scraper/client for extracting structured data from a WWI entry in
    the Australian War Memorial's Honours and Awards database.
    '''
    FIELDS = {
                'single_value':
                [
                    'Service Number:',
                    'Rank:',
                    'Unit:',
                    'Service:',
                    'Award:',
                    'Date of London Gazette:',
                    'Location in London Gazette:',
                    'Date of Commonwealth of Australia Gazette:',
                    'Location in Commonwealth of Australia Gazette:',
                    'Recommendation:',
                    'Date of recommendation:'
                ],
                'multiple_value':
                []
            }


class CollectionClient(BaseClient):
    '''
    Basic scraper/client for extracting structured data from an entry in
    the Australian War Memorial's collection database.
    '''

    FIELDS = {
                'single_value':
                [
                    'ID number',
                    'Title',
                    'Photographer',
                    'Object type',
                    'Date made',
                    'Description',
                    'Place made',
                    'Summary',
                    'Object_type',
                    'Maker',
                    'Physical description',
                    'Access',
                    'Copying provision',
                    'Measurement',
                    'Artist',
                    'Medium'
                ],
                'multiple_value':
                [
                    'Places made'
                ]
            }

    def get_licence(self, soup=None, url=None):
        ''' Get the licence applied to this item. '''
        soup = self._get_soup(soup, url)
        try:
            licence = soup.find('a', rel='license').string.strip()
        except AttributeError:
            licence = None
        return licence

    def get_permalink(self, soup=None, url=None):
        ''' Get the item permalink. '''
        soup = self._get_soup(soup, url)
        try:
            permalink = soup.find(id='collection_permalink').contents[1].string.strip()
        except AttributeError:
            permalink = None
        return permalink

    def get_img_url(self, soup=None, url=None):
        ''' Get the url of a collection image. '''
        soup = self._get_soup(soup, url)
        try:
            img_url = '{}{}'.format(
                                self.AWM_URL,
                                soup.find('span', rel='contentURL').find('img')['src']
                                )
        except AttributeError:
            img_url = None
        return img_url

    def _get_field_value(self, soup, field):
        ''' Get the text value of the requested field. '''
        try:
            value = soup.find('dt', text=field).find_next_sibling('dd').string.strip()
        except AttributeError:
            value = None
        return value

    def _get_field_values(self, soup, field):
        ''' Get a list of values from the requested field. '''
        try:
            value_list = soup.find('dt', text=field).find_next_sibling('dd').find_all('li')
            values = [value.get_text().strip() for value in value_list]
        except AttributeError:
            values = None
        return values

    def get_collection(self, soup=None, url=None):
        ''' Get the collection of which this item is part. '''
        soup = self._get_soup(soup, url)
        try:
            collection = soup.find('dt', text='Collection').find_next_sibling('dd').string.strip()
        except AttributeError:
            collection = None
        return collection

    def _process_fieldname(self, field):
        ''' Slugify field.'''
        return field.lower().replace(' ', '_').replace(':', '')

    def get_details(self, soup=None, url=None):
        ''' Return all the extracted details for this item. '''
        soup = self._get_soup(soup, url)
        details = {}
        details['licence'] = self.get_licence(soup)
        details['img_url'] = self.get_img_url(soup)
        details['collection'] = self.get_collection(soup)
        details['permalink'] = self.get_permalink(soup)
        for field in self.FIELDS['single_value']:
            fieldname = self._process_fieldname(field)
            details[fieldname] = self._get_field_value(soup, field)
        for field in self.FIELDS['multiple_value']:
            fieldname = self._process_fieldname(field)
            details[fieldname] = self._get_field_values(soup, field)
        return details


class AWMBioSearchClient(BaseClient):

    FIELDS = ['name', 'service_number', 'unit', 'conflict', 'award']

    def search(self, db, **kwargs):
        params = urllib.urlencode(kwargs)
        url = '{}/research/people/{}/?{}&op=Search'.format(self.AWM_URL, db, params)
        print (url)
        response = self._get_url(url)
        soup = BeautifulSoup(response.read())
        #print soup
        total_results = self._get_total_results(soup)
        results = self._process_page(soup)
        return {
                'total_results': total_results,
                'results': results
            }

    def _process_page(self, soup):
        results = []
        try:
            rows = soup.table.tbody.find_all('tr')
        except AttributeError:
            pass
        else:
            for row in rows:
                results.append(self._process_row(row))
        return results

    def _process_row(self, row):
        cells = row.find_all('td')
        result = {}
        result['name'] = cells[0].a.string.strip()
        result['url'] = self.AWM_URL + cells[0].a['href']
        for cell, field in enumerate(self.FIELDS):
            if cell != 0:
                try:
                    result[field] = self._get_cell(cells[cell])
                except IndexError:
                    pass
        return result

    def _get_cell(self, cell):
        try:
            value = cell.get_text(strip=True)
        except AttributeError:
            value = None
        return value

    def _get_total_results(self, soup):
        try:
            page_count = soup.find(class_='pg_pagecount').get_text()
            total_results = re.search(r'Displaying \d+ to \d+ of (\d{1,3}(?:\,\d{3})*)', page_count).group(1)
        except AttributeError:
            total_results = 0
        else:
            total_results = total_results.replace(',', '')
        return int(total_results)


class UsageError(Exception):
    pass


class ServerError(Exception):
    pass
