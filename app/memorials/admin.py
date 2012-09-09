#!/usr/bin/env python

from django.contrib import admin
from app.memorials.models import *


class MemorialSourceInline(admin.TabularInline):
    model = MemorialAssociatedSource
    extra = 1


class MemorialPartInline(admin.TabularInline):
    model = MemorialPart
    extra = 1


class MemorialAdmin(admin.ModelAdmin):
    inlines = (MemorialSourceInline, MemorialPartInline,)

admin.site.register(Memorial, MemorialAdmin)
admin.site.register(MemorialAssociation)
admin.site.register(MemorialPart)
