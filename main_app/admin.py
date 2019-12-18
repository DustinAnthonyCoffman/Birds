from django.contrib import admin
from .models import Bird, Photo, Feeding

# Register your models here.
admin.site.register(Bird)
admin.site.register(Photo)
admin.site.register(Feeding)