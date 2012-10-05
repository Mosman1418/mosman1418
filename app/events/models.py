from django.db import models

# Create your models here.


class Event(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_type = models.CharField(max_length=10, choices=(('instance', 'instance'), ('interval', 'interval')))
    start_date = models.DateField(blank=True, null=True)
    start_date_month = models.BooleanField(default=False)
    start_date_day = models.BooleanField(default=False)
    latest_start_date = models.DateField(blank=True, null=True)
    latest_start_date_month = models.BooleanField(default=False)
    latest_start_date_day = models.BooleanField(default=False)
    end_date = models.DateField(blank=True, null=True)
    end_date_month = models.BooleanField(default=False)
    end_date_day = models.BooleanField(default=False)
    earliest_end_date = models.DateField(blank=True, null=True)
    earliest_end_date_month = models.BooleanField(default=False)
    earliest_end_date_day = models.BooleanField(default=False)

