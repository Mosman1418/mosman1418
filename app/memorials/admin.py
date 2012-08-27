#!/usr/bin/env python

from django.contrib import admin
from mosman1418.memorials.models import *

class MemorialSourceInline(admin.TabularInline):
    model = MemorialAssociatedSource
    extra = 1
    
class MemorialAdmin(admin.ModelAdmin):   
    inlines = (MemorialSourceInline,)

admin.site.register(Memorial, MemorialAdmin)
admin.site.register(MemorialAssociation)