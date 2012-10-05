#!/usr/bin/env python

from django.contrib import admin
from app.linkeddata.models import *


class RDFPropertyInline(admin.TabularInline):
    model = RDFProperty
    extra = 1


class RDFClassInline(admin.TabularInline):
    model = RDFClass
    extra = 1


class RDFSchemaAdmin(admin.ModelAdmin):
    inlines = (RDFPropertyInline, RDFClassInline,)


admin.site.register(RDFSchema, RDFSchemaAdmin)
admin.site.register(RDFProperty)
admin.site.register(RDFClass)
