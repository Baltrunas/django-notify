from django.db import models
from django.contrib import admin
from django.forms import Textarea

from .models import Notify, NotifyProperty


class NotifyPropertyInline(admin.TabularInline):
	model = NotifyProperty
	extra = 0
	fields = ['name', 'key', 'value']
	formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 80})},
    }

class NotifyAdmin(admin.ModelAdmin):
	list_display = ['name', 'backend', 'on_create', 'on_change', 'public']
	search_fields = ['name', 'backend', 'on_create', 'on_change', 'public']
	list_filter = ['public', 'on_create', 'on_change', 'backend']
	list_editable = ['public', 'on_create', 'on_change', 'backend']
	inlines = [NotifyPropertyInline]
	save_as = True

admin.site.register(Notify, NotifyAdmin)


class NotifyPropertyAdmin(admin.ModelAdmin):
	list_display = ['notify', 'name', 'key', 'value']
	search_fields = ['notify', 'name', 'key', 'value']
	list_filter = ['notify', 'key']

admin.site.register(NotifyProperty, NotifyPropertyAdmin)
