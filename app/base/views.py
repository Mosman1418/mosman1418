# Create your views here.

from django.views.generic import TemplateView
from app.sources.models import *


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['stories'] = Story.objects.all().order_by('-date_created')[:5]
        context['image'] = Source.objects.filter(source_type__label='photograph').filter(personassociatedsource__association__label='primary topic of').order_by('?')[0]
        return context
