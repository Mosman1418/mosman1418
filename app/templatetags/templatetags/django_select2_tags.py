from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag(name='import_django_select2_js')
def import_js():
    return (u'<script src="http://mosman1914-1918.net/static/js/select2.js"></script>')


@register.simple_tag(name='import_django_select2_css')
def import_css():
    return (u'<style type="text/css" href="http://mosman1914-1918.net/static/css/select2.css">')