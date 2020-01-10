# -*- coding: utf-8 -*-

from django.contrib.admin import SimpleListFilter

from api.models import *

class BuildingFilter(SimpleListFilter):
  title = u'Gebäude'
  parameter_name = 'building'

  def lookups(self, request, model_admin):
    buildings = Building.objects.values_list('id', 'title')
    if request.user.is_superuser:
      return buildings
    return buildings.filter(id__in=request.user.location_set.values('building'))

  def queryset(self, request, queryset):
    if self.value():
      model = queryset[0].__class__
      if model in (Board, Bookable, Content):
        return queryset.filter(building__in=self.value())
      elif model == Booking:
        return queryset.filter(bookable__building__in=self.value())
      elif model == Building:
        return queryset.filter(id__in=self.value())
      elif model == User:
        return queryset.filter(location__building__in=self.value())
    return queryset

class BookableFilter(SimpleListFilter):
  title = u'Titel'
  parameter_name = 'bookable'

  def lookups(self, request, model_admin):
    bookables = Bookable.objects.order_by('title')
    if 'building' in request.GET:
      bookables = bookables.filter(building__id=request.GET['building'])
    if not request.user.is_superuser:
      bookables = bookables.filter(building__in=request.user.location_set.values('building'))
    return bookables.values_list('id', 'title')

  def queryset(self, request, queryset):
    if self.value():
      return queryset.filter(bookable__id=self.value())
    return queryset

class CreatorFilter(SimpleListFilter):
  title = 'Erstellt von'
  parameter_name = 'creator'

  def lookups(self, request, model_admin):
    return User.objects.filter(is_staff=True).order_by('username').values_list('id', 'username')

  def queryset(self, request, queryset):
    creator_id = self.value()
    if creator_id:
      return queryset.filter(creator=self.value())
    return queryset
