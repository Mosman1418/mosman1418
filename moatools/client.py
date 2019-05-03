from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, HTTPError
import re

try:
    from utilities import retry
except ImportError:
    from moatools.utilities import retry


class MOAClient():
    '''
    Simple scraper/client for extracting structured data from
    entries in Mapping Our Anzacs (http://mappingouranzacs.naa.gov.au/).

    USAGE:

    import client
    moa = client.MOAClient()
    details = moa.get_details(id)

    PARAMETERS:

    'id' can either be a barcode number or a MoA permalink.

    SAMPLE RESULTS:
    {
        'also_known_as': None,
        'family_name': 'Hutchings',
        'next_of_kin': u'Hutchings, Emily (mother)',
        'other_names': 'Frank Albert',
        'place_of_birth': u'Goulburn, NSW, Australia',
        'place_of_enlistment': u'Liverpool, NSW, Australia',
        'service_number': u'Lieutenant',
        'ww1_file': {
            'barcode': '6928234',
            'control_symbol': 'HUTCHINGS F A LIEUTENANT',
            'series': 'B2455'
            },
        'ww2_file': {
            'barcode': '5652072',
            'control_symbol': u'NX111970',
            'series': u'B883'}
        }
        'tumblr_ids': [],
        'see_also': {'barcode': None, 'name': None, 'url': None}
    }

    '''

    MOA_URL = 'http://mappingouranzacs.naa.gov.au/details-permalink.aspx?barcode_no={}'
    FIELDS = {
        'service_number': 'ContentPlaceHolder1_Repeater\d_Label3_0',
        'place_of_birth': 'ContentPlaceHolder1_Repeater\d_Label4_0',
        'place_of_enlistment': 'ContentPlaceHolder1_Repeater\d_Label5_0',
        'next_of_kin': 'ContentPlaceHolder1_Repeater\d_Label6_0',
        'also_known_as': 'ContentPlaceHolder1_Repeater\d_Label2_0'
    }
    FORM_FIELDS = {
        'other_names': 'ContentPlaceHolder1_Repeater1_hiddentxtOthernames_0',
        'family_name': 'ContentPlaceHolder1_Repeater1_hiddentxtSurname_0'
    }
    WW1_FILE_FIELDS = {
        'series': 'ContentPlaceHolder1_Repeater1_hiddentxtSeries_0',
        'control_symbol': 'ContentPlaceHolder1_Repeater1_hiddentxtControlSymbol_0'
    }
    WW2_FILE_FIELDS = {
        'series': 'ContentPlaceHolder1_Repeater\d_Label9_0',
        'control_symbol': 'ContentPlaceHolder1_Repeater\d_Label10_0'
    }
    WW2_LINK = 'ContentPlaceHolder1_Repeater\d_ww2link_0'
    SEE_ALSO_LINK = 'ContentPlaceHolder1_Repeater\d_seelink_0'
    SEE_ALSO_NAME = 'ContentPlaceHolder1_Repeater\d_Label11_0'

    # Uncomment the next line to retry in the case of a timeout error.
    #@retry(ServerError, tries=10, delay=1)
    def _get_url(self, url):
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

    def _get_field_value(self, soup, field):
        ''' Get the text of the element with the supplied id.'''
        try:
            value = soup.find(id=re.compile(field)).string.strip()
        except AttributeError:
            value = None
        return value

    def _get_form_field_value(self, soup, field):
        ''' Get the value of the form element with the supplied id.'''
        try:
            value = soup.find(id=re.compile(field))['value'].strip()
        except (TypeError, AttributeError):
            value = None
        return value

    def _parse_id(self, id):
        '''
        Check to see if the supplied id is a barcode or MoA permalink.
        Extract and return barcode.
        '''
        if id.isdigit():
            barcode = id
        else:
            try:
                barcode = re.search(r'barcode_no=(\d+)', id).group(1)
            except AttributeError:
                raise UsageError('Please provide a valid barcode or url')
        return barcode

    def get_details(self, id):
        '''
        Get all the extracted details from an entry with the supplied id.
        'id' is either an NAA Recordsearch barcode or a MoA permalink.
        '''
        details = {}
        barcode = self._parse_id(id)
        response = self._get_url(self.MOA_URL.format(barcode))
        soup = BeautifulSoup(response.read())
        for field, id in self.FIELDS.items():
            details[field] = self._get_field_value(soup, id)
        for field, id in self.FORM_FIELDS.items():
            details[field] = self._get_form_field_value(soup, id)
        details['ww1_file'] = self._get_ww1_file(soup, barcode)
        details['ww2_file'] = self._get_ww2_file(soup)
        details['see_also'] = self._get_see_also(soup)
        details['tumblr_ids'] = self.get_tumblr_ids(soup)
        return details

    def _get_ww1_file(self, soup, barcode):
        ''' Get the details of the associated WW1 service record. '''
        ww1_file = {}
        for field, id in self.WW1_FILE_FIELDS.items():
            ww1_file[field] = self._get_form_field_value(soup, id)
        ww1_file['barcode'] = barcode
        return ww1_file

    def _get_ww2_file(self, soup):
        ''' Get details of a linked WW2 service record (if one exists). '''
        ww2_file = {}
        try:
            ww2_link = soup.find(id=re.compile(self.WW2_LINK))['href']
        except TypeError:
            ww2_file['barcode'] = None
        else:
            try:
                barcode = re.search(r'&Number=(\d+)', ww2_link).group(1)
                if barcode != '0':
                    ww2_file['barcode'] = barcode
                else:
                    ww2_file['barcode'] = None
            except AttributeError:
                ww2_file['barcode'] = None
        for field, id in self.WW2_FILE_FIELDS.items():
            ww2_file[field] = self._get_field_value(soup, id)
        return ww2_file

    def _get_see_also(self, soup):
        ''' Get details of links between MoA entries. '''
        see_also = {}
        try:
            href = soup.find(id=self.SEE_ALSO_LINK)['href']
            barcode = self._parse_id(href)
            if barcode != '0':
                see_also['url'] = 'http://mappingouranzacs.naa.gov.au/{}'.format(href)
                see_also['barcode'] = barcode
            else:
                see_also['url'] = None
                see_also['barcode'] = None
        except TypeError:
            see_also['url'] = None
            see_also['barcode'] = None
        see_also['name'] = self._get_field_value(soup, self.SEE_ALSO_NAME)
        return see_also

    def get_tumblr_ids(self, soup=None, id=None):
        ''' Get id numbers of Tumblr posts in the MoA scrapbook. '''
        if not soup and not id:
            raise UsageError('Please provide a valid barcode or url')
        elif id and not soup:
            barcode = self._parse_id(id)
            response = self._get_url(self.MOA_URL.format(barcode))
            soup = BeautifulSoup(response.read())
        tumblr_ids = []
        for tumblr_ref in soup.find_all('div', 'tumblrRefs'):
            tumblr_ids.append(tumblr_ref.string.split(',')[0].strip())
        return tumblr_ids


class UsageError(Exception):
    pass


class ServerError(Exception):
    pass
