from django.contrib import admin

# Register your models here.
from .models import Store_labels
from .models import Review_tokens

admin.site.register(Store_labels)
admin.site.register(Review_tokens)