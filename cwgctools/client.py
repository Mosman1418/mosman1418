from bs4 import BeautifulSoup
from urllib.request import urlopen, Request, HTTPError
import urllib
import mechanize
import sys
import re

import logging

#logger = logging.getLogger("mechanize")
#logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.DEBUG)


class CWGCClient():
    '''
    Basic scraper/client for extracting structured data from the Commonwealth
    War Graves Commission database.

    USAGE:

    import client
    cwgc = client.CWGCClient()
    details = cwgc.get_details(url)

    'url' is the url of an individual entry for a person in the CWGC database.

    SAMPLE RESULTS:

    {
        'additional_information': u'Son of Edward and Alice Crisford, of 104, Glover St., Mosman, New South Wales. Born at Gordon, New South Wales.',
        'age': u'24',
        'cemetery': {
            'country': u'France',
            'locality': u'Pas de Calais',
            'name': u'QUEANT ROAD CEMETERY, BUISSY',
            'url': 'http://www.cwgc.org/find-a-cemetery/cemetery/32500/QUEANT ROAD CEMETERY, BUISSY'},
        'date_of_death': u'23/04/1917',
        'grave_reference': u'Sp. Mem. B. 3.',
        'name': u'CRISFORD, WILFRED REGINALD EDGAR',
        'rank': u'Gunner',
        'service': u'Australian Field Artillery',
        'service_no': u'9389',
        'unit': u'5th Bde.',
        'url': 'http://www.cwgc.org/find-war-dead/casualty/313405/CRISFORD,%20WILFRED%20REGINALD%20EDGAR'
    }
    '''

    FIELDS = [

                'Rank:',
                'Service No:',
                'Date of Death:',
                'Age:',
                'Grave Reference',
            ]

    FORM_FIELDS = {
        'surname': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$txtSurname',
        'forename_initials': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$ForenameInitials',
        'forename': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$txtForename',
        'war': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$ddlWar',
        'australian': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$chkAustralian',
        'service_number': 'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$txtServiceNumber'
    }

    RESULTS_FIELDS = [
        'name',
        'rank',
        'service_number',
        'date_of_death',
        'age',
        'service',
        'country',
        'grave_reference',
        'cemetery'
    ]

    CWGC_URL = 'http://www.cwgc.org'
    SEARCH_URL = 'http://www.cwgc.org/find-war-dead.aspx'

    def __init__(self):
        self.br = None

    def _get_field_value(self, soup, field):
        ''' Get the value of a field. '''
        try:
            value = soup.find('dt', text=field).find_next_sibling('dd').string.strip()
        except AttributeError:
            value = ''
        return value

    def _get_name(self, soup):
        ''' Get the person's name. '''
        return soup.h2.string.strip()

    def _get_additional_info(self, soup):
        ''' Get the additional information note. '''
        try:
            info = soup.find('h3', text='Additional Information:').find_next_sibling('p').string.strip()
        except AttributeError:
            info = ''
        return info

    def _get_service(self, soup):
        ''' Get service and unit details. '''
        service = self._get_field_value(soup, 'Regiment/Service:')
        unit = self._get_field_value(soup, '\xc2\xa0')
        return {'service': service, 'unit': unit}

    def _process_fieldname(self, field):
        ''' Slugify fieldnames '''
        return field.lower().replace(' ', '_').replace(':', '')

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
            else:
                raise
        else:
            return response

    def get_details(self, url):
        ''' Return all the extracted details for the supplied url.'''
        response = self._get_url(url)
        soup = BeautifulSoup(response.read())
        details = {}
        details['url'] = url
        details['name'] = self._get_name(soup)
        for field in self.FIELDS:
            fieldname = self._process_fieldname(field)
            details[fieldname] = self._get_field_value(soup, field)
        details['additional_information'] = self._get_additional_info(soup)
        details.update(self._get_service(soup))
        details['cemetery'] = self._get_cemetery(soup)
        return details

    def _get_cemetery(self, soup):
        ''' Get the basic cemetery details. '''
        cemetery = {}
        try:
            cemetery['name'] = soup.find('div', 'greyBox').h2.string.strip()
            cemetery['url'] = '{}{}'.format(
                self.CWGC_URL,
                soup.find('p', 'readMore').a['href']
            )
        except AttributeError:
            cemetery['name'] = None
        cemetery['country'] = self._get_field_value(soup, 'Country:')
        cemetery['locality'] = self._get_field_value(soup, 'Locality:')
        return cemetery

    def search(self, page=None, sort='name', **kwargs):
        ''' Search the db for matching results. '''
        if page and self.br:
            html = self._get_page(page)
        elif kwargs:
            self._prepare_search(**kwargs)
            html = self._do_search(sort)
            if page:
                html = self._get_page(page, sort)
        else:
            raise UsageError('No search parameters were provided.')
        results = self._process_page(html)
        total_results = self._get_total_results(html)
        return {'results': results, 'total_results': total_results}

    def _create_browser(self):
        self.br = mechanize.Browser()
        self.br.addheaders = [('User-agent',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17')]
        self.br.set_handle_robots(False)
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    def _prepare_search(self, **kwargs):
        self._create_browser()
        self.br.open(self.SEARCH_URL)
        self.br.select_form(nr=0)
        for key, value in kwargs.items():
            self.br.form[self.FORM_FIELDS[key]] = value

    def _do_search(self, sort):
        response = self.br.submit("ctl00$ctl00$ctl00$ContentPlaceHolderDefault$cpMain$ctlCasualtySearch$btnSearch")
        if sort:
            response = self.br.open('{}?sort={}&order=asc'.format(self.SEARCH_URL, sort))
        html = response.read()
        return html

    def _get_page(self, page, sort):
        response = self.br.open('{}?cpage={}&sort={}&order=asc'.format(self.SEARCH_URL, page, sort))
        html = response.read()
        return html

    def _process_page(self, html):
        soup = BeautifulSoup(html)
        results = []
        try:
            rows = soup.find(id='dataTable').tbody.find_all('tr')
        except AttributeError:
            # No results
            pass
        else:
            for row in rows:
                results.append(self._process_row(row))
        return results

    def _get_cell(self, cell):
        try:
            value = cell.string.strip()
        except AttributeError:
            value = None
        return value

    def _process_row(self, row):
        result = {}
        cells = row.find_all('td')
        result['name'] = cells[0].a.string.strip().title()
        result['id'] = self.CWGC_URL + cells[0].a['href']
        for cell, field in enumerate(self.RESULTS_FIELDS):
            if cell != 0:
                result[field] = self._get_cell(cells[cell])
        return result

    def _get_total_results(self, html):
        soup = BeautifulSoup(html)
        try:
            totals = soup.find(id='ContentPlaceHolderDefault_cpMain_ctlCasualtySearch_pnlPaginationTop').p.string
            total = re.search(r'(\d+) record', totals).group(1)
        except AttributeError:
            total = None
        return total


class ServerError(Exception):
    pass


class UsageError(Exception):
    pass
