#!/usr/bin/env python

from django.contrib import admin
from app.memorials.models import *


class MemorialSourceInline(admin.TabularInline):
    model = MemorialAssociatedSource
    extra = 1


class MemorialPlaceInline(admin.TabularInline):
    model = MemorialAssociatedPlace
    extra = 1


class MemorialPartInline(admin.TabularInline):
    model = MemorialPart
    extra = 1


class MemorialAdmin(admin.ModelAdmin):
    inlines = (MemorialSourceInline, MemorialPartInline, MemorialPlaceInline)


class MemorialNameAdmin(admin.ModelAdmin):
	list_display = ('name', 'memorial', 'memorial_part')
	list_filter = ('memorial', 'memorial_part')
	search_fields = ['name']
	ordering = ('name',)

admin.site.register(Memorial, MemorialAdmin)
admin.site.register(MemorialAssociation)
admin.site.register(MemorialPart)
admin.site.register(MemorialSourceAssociation)
admin.site.register(MemorialPlaceAssociation)
admin.site.register(MemorialName, MemorialNameAdmin)
