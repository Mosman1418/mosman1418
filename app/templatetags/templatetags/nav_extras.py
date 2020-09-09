import string
from django import template
from django.urls import reverse, reverse_lazy

register = template.Library()


@register.inclusion_tag('_alpha_browse.html')
def alpha_browse(entity, active):
    entity_link = '{}-alpha-list'.format(entity)
    list_alpha = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')
    return {'letters': list_alpha,
            'entity_link': entity_link,
            'active': active}


@register.inclusion_tag('_pagination.html', takes_context=True)
def paginate(context, entity, number):
    letter = context['letter']
    if 'memorial' in context:
        entity_id = context['memorial'].id
    else:
        entity_id = None
    if letter:
        entity_link = '{}-alpha-list'.format(entity)
    else:
        entity_link = '{}-list'.format(entity)
    page = context['content']
    queries = context['queries']
    pages = page.paginator.page_range
    current = page.number
    number = int(number)
    last = pages[-1]
    if current + number >= last:
        pages = pages[-1 - (number * 2):]
    elif current - number <= 0:
        pages = pages[:(number * 2) + 1]
    else:
        pages = pages[current - (number + 1):current + number]
    return {'entity_link': entity_link,
            'entity_id': entity_id,
            'page': page,
            'pages': pages,
            'letter': letter,
            'queries': queries,
            'last': last}
