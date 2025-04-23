from django.contrib import admin
from .models import *

# Register models.
admin.site.register(Complaint)
admin.site.register(Location)
admin.site.register(ComplaintHistory)
admin.site.register(ComplaintType)
