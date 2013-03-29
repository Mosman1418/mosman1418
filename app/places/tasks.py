from app.places.models import *
from django.contrib.auth.models import User
from urllib2 import urlopen
import json
from urllib import quote_plus


NOM_URL = 'http://nominatim.openstreetmap.org/search?q={},+{}&format=json&polygon=1'


def load_streets():
    streets_file = '/Users/tim/mycode/mosman1418/mosman1418/data/streets.txt'
    user = User.objects.get(username='system')
    with open(streets_file, 'rb') as streets:
        for street in streets:
            MosmanStreet.objects.create(
                    street_name=street,
                    added_by=user
                )


def get_osm_data():
    for street in MosmanStreet.objects.all():
        url = NOM_URL.format(quote_plus(street.street_name), 'Mosman')
        response = urlopen(url)
        data = json.load(response)
        print data
