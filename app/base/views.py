# Create your views here.

from django.views.generic import TemplateView
from app.sources.models import Story


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['stories'] = Story.objects.all().order_by('-date_created')[:5]
        return context
