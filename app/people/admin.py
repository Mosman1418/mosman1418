#!/usr/bin/env python

from django.contrib import admin
from app.people.models import *


admin.site.register(Person)
admin.site.register(Organisation)
admin.site.register(PersonAssociation)
admin.site.register(Rank)
admin.site.register(ServiceNumber)
admin.site.register(Birth)
admin.site.register(Death)
admin.site.register(LifeEvent)

