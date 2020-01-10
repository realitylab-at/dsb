from django import forms
from django.contrib import admin

from adminsortable.admin import SortableTabularInline

from api.models import *
from api.admin_forms import *

class GenericInline(admin.TabularInline):
  readonly_fields = ('creator', 'modifier', 'created', 'modified')

class UserProfileInline(admin.StackedInline):
  model = UserProfile
  exclude = ('image',)
  fields = (('temp_password', 'reset_date'),)
  readonly_fields = ('temp_password', 'reset_date',)
  can_delete = False
  max_num = 1

class LocationInline(admin.TabularInline):
  model = Location
  formset = LocationInlineFormset
  fk_name = 'user'
  fields = ('building', 'apartment')
  extra = 0

  def get_formset(self, request, obj=None, **kwargs):
    formset = super(LocationInline, self).get_formset(request, obj, **kwargs)
    if not request.user.is_superuser:
      fields = formset.form.base_fields
      ids = request.user.location_set.values_list('building__id');
      buildings = Building.objects.filter(id__in=ids)
      fields['building'] = forms.ModelChoiceField(queryset=buildings)
    return formset

class BoardInline(GenericInline):
  model = Board
  fields = ('title',)
  readonly_fields = ('title',)
  can_delete = False
  extra = 0

class BuildingInline(GenericInline):
  model = Building
  exclude = ('title',)
  can_delete = False
  extra = 0

class ContentInline(admin.StackedInline):
  model = Content
  readonly_fields = GenericInline.readonly_fields
  can_delete = True
  extra = 0

class BookingInline(GenericInline):
  model = Booking
  exclude = ('title', 'modifier',)
  readonly_fields = ('start_time', 'end_time', 'creator', 'created')
  can_delete = False
  extra = 0

class BookableInline(SortableTabularInline):
  model = Bookable
  extra = 0
  exclude = ('creator', 'modifier')

class RsvpInline(GenericInline):
  model = RSVP
  fields = ('title', 'creator', 'modifier', 'modified')
  readonly_fields = ('creator', 'modifier', 'modified')
  extra = 0

  def get_formset(self, *args, **kwargs):
    formset = super(RsvpInline, self).get_formset(*args, **kwargs)
    fields = formset.form.base_fields
    widget = forms.Select(choices=RSVP.CHOICES)
    fields['title'] = forms.CharField(label='Titel', widget=widget)
    return formset

class MetadataInline(admin.TabularInline):
  model = Metadata
  extra = 0

class AdInline(SortableTabularInline):
  model = Ad
  readonly_fields = ('thumbnail',)
  extra = 0

  def thumbnail(self, ad):
    return '<img src="%s" height="100">' % ad.image.url
  thumbnail.allow_tags = True
  thumbnail.short_description = 'Vorschau'

