#!/usr/bin/env python

from django.contrib import admin
from app.people.models import *


admin.site.register(Person)
admin.site.register(PeopleImage)
admin.site.register(PeopleStory)
