#!/usr/bin/env python

#!/usr/bin/env python

from django.contrib import admin
from app.sources.models import *

admin.site.register(Source)
admin.site.register(SourceType)
admin.site.register(SourceImage)
admin.site.register(Story)
admin.site.register(SourcePerson)
