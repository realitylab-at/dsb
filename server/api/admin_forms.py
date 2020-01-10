# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet

from api.models import *

class BookingAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(BookingAdminForm, self).__init__(*args, **kwargs)
    self.fields['bookable'].choices = self.get_bookables(*args, **kwargs)

  def get_bookables(*args, **kwargs):
    bookables = Bookable.objects.order_by('title')
    if 'instance' in kwargs:
      booking = kwargs['instance']
      bookables = bookables.filter(building=booking.bookable.building)
    return bookables.values_list('id', 'title')

class UserProfileAdminForm(forms.ModelForm):
  class Meta:
    model = User
    fields = '__all__'

  def clean(self):
    data = super(UserProfileAdminForm, self).clean()
    if data.get('is_staff', False) and not data.get('is_superuser', False):
      # Show an error if a staff account is not assigned at least one group
      if len(data.get('groups', [])) < 1:
        message = u'Bitte weisen Sie dem Profil mind. eine Gruppe zu.'
        self._errors['groups'] = self.error_class([message])
        del data['groups']
    return data

class LocationInlineFormset(forms.models.BaseInlineFormSet):
  def clean(self):
    super(LocationInlineFormset, self).clean()
    if self.instance.is_superuser:
      return

    valid = False
    assigned_buildings = []
    for form in self.forms:
      is_delete = form.cleaned_data.get('DELETE', False)
      building = form.cleaned_data.get('building', False)
      if building in assigned_buildings:
        raise forms.ValidationError(u'Bitte weisen Sie dem Profil nicht zweimal dasselbe Gebäude zu.')
      elif building and not is_delete:
        assigned_buildings.append(building)
      if form.cleaned_data and not is_delete:
        valid = True
    # Show an error if a staff account is not assigned at least one location
    if not valid:
      raise forms.ValidationError(u'Bitte weisen Sie dem Profil mind. ein Gebäude zu.')
