from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Advocate)
admin.site.register(UserRegistration)
admin.site.register(Login)
admin.site.register(Case_request)
admin.site.register(Case_details)
admin.site.register(Feedback)

