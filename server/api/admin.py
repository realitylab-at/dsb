# -*- coding: utf-8 -*-

import time, pytz
from datetime import datetime

from django.core import urlresolvers
from django.db.models import Q

from django.contrib import admin
#from django.contrib.contenttypes import generic
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session

from reversion.admin import VersionAdmin
from reversion.helpers import patch_admin

from import_export import resources, fields
from import_export.admin import ImportMixin, ImportExportMixin

from adminsortable.admin import NonSortableParentAdmin

from api.models import *
from api.admin_filters import *
from api.admin_forms import *
from api.admin_inlines import *

USERINFO_FIELDSET = (
  'User Info', {
    'classes': ('collapse', 'wide'),
    'fields': ('creator', 'created', 'modifier', 'modified')
  }
)

User.__unicode__ = user_unicode

class GenericAdmin(VersionAdmin):
  readonly_fields = ('creator', 'modifier', 'created', 'modified')

  def save_model(self, request, object, form, change):
    if hasattr(object, 'creator') == False:
      object.creator = request.user
    object.modifier = request.user
    object.save()

  def save_formset(self, request, form, formset, change):
    print(123);
    instances = formset.save(commit=False)
    for object in formset.deleted_objects:
      object.delete()
    for object in instances:
      if hasattr(object, 'creator') == False:
        object.creator = request.user
      object.modifier = request.user
      object.save()
    formset.save_m2m()

  def creator_name(self, obj):
    return unicode(obj.creator.userprofile)

class UserProfileResource(resources.ModelResource):

  def before_import(self, dataset, dry_run, *args, **kwargs):
    user_ids = []

    for data in dataset.dict:
      username = data['username']
      email = data['email']
      building = Building.objects.get(pk=data['building'])
      apartment = data['apartment']

      try:
        user = User.objects.get(username=username, email=email)
      except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()

      query = {'user': user, 'building': building, 'apartment': apartment}

      try:
        location = Location.objects.get(**query)
      except Location.DoesNotExist:
        location = Location(**query)
        location.save()

      user_ids.append(user.id)

    dataset.insert_col(0, user_ids, 'user')
    return super(UserProfileResource, self).before_import(dataset, dry_run, *args, **kwargs)

  # def init_instance(self, data, *args, **kwargs):
  #   profile = super(UserProfileResource, self).init_instance(data, *args, **kwargs)
  #   return profile

  # def before_save_instance(self, instance, dry_run, *args, **kwargs):
  #   return super(UserProfileResource, self).before_save_instance(instance, dry_run, *args, **kwargs)

  class Meta:
    model = UserProfile
    #use_transactions = True
    #skip_unchanged = True
    #report_skipped = True
    fields = ('user', 'username', 'first_name', 'last_name', 'email', 'building', 'apartment')
    import_id_fields = ('user',)

class UserProfileAdmin(ImportMixin, UserAdmin):
  resource_class = UserProfileResource
  form = UserProfileAdminForm
  list_display = ('username', 'full_name', 'email_link', 'buildings', 'apartments', 'MA', 'Admin', 'is_active')
  list_display_links = ('username',)
  list_editable = ('is_active',)
  list_filter = (BuildingFilter, 'is_staff', 'is_superuser', 'is_active')
  inlines = (LocationInline, UserProfileInline)
  readonly_fields = ('password', 'last_login', 'date_joined')
  view_on_site = False

  def get_queryset(self, request):
    queryset = super(UserProfileAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    queryset = queryset.exclude(is_superuser=True)
    self_filter = Q(pk=request.user.id)
    return queryset.filter(self_filter | Q(location__building__in=request.user.location_set.values('building'))).distinct()

  def change_view(self, request, *args, **kwargs):
    if request.user.is_superuser:
      return super(UserProfileAdmin, self).change_view(request, *args, **kwargs)
    try:
      self.fieldsets = (
        (None, {
          'fields': ('username', 'password', 'first_name', 'last_name', 'email', 'is_active', 'last_login', 'date_joined')
        }),
      )
      response = super(UserProfileAdmin, self).change_view(request, *args, **kwargs)
    finally:
      self.fieldsets = UserProfileAdmin.fieldsets
    return response

  def full_name(self, user):
    if len(user.last_name) > 0 and len(user.first_name) > 0:
      return ', '.join((user.last_name, user.first_name))
    elif len(user.last_name) > 0:
      return user.last_name
    elif len(user.first_name) > 0:
      return user.first_name
  full_name.short_description = 'Vollständiger Name'
  full_name.admin_order_field = 'last_name'

  def email_link(self, user):
    return '<a href="mailto:%s">%s</a>' % (user.email, user.email)
  email_link.short_description = 'E-Mail-Adresse'
  email_link.admin_order_field = 'email'
  email_link.allow_tags = True

  def buildings(self, user):
    return '<br>'.join(user.location_set.values_list('building__title', flat=True).order_by('building__title'))
  buildings.short_description = u'Gebäude'
  buildings.allow_tags = True
  buildings.admin_order_field = 'location__building__title'

  def apartments(self, user):
    apartments = []
    for location in user.location_set.exclude(building=None).order_by('building__title'):
      apartment = user.userprofile.get_apartment(location.building)
      apartments.append(apartment or '')
    return '<br>'.join(apartments)
  apartments.short_description = 'Wohnung'
  apartments.admin_order_field = 'location__apartment'
  apartments.allow_tags = True

  def Admin(self, user):
    return user.is_superuser
  Admin.boolean = True
  Admin.admin_order_field = 'is_superuser'

  def MA(self, user):
    return user.is_staff
  MA.boolean = True
  MA.admin_order_field = 'is_staff'

  def group_list(self, user):
    result = []
    if user.is_superuser:
      result.append('Administration')
    if user.is_staff:
      result.append('Hausverwaltung')
    return ', '.join(result)
  group_list.short_description = 'Gruppen'
  group_list.admin_order_field = 'is_superuser'
  group_list.allow_tags = True

@admin.register(Building)
class BuildingAdmin(GenericAdmin, NonSortableParentAdmin):
  list_display = ('title', 'address', 'board_list', 'apartment_count', 'site_link')
  list_filter = (BuildingFilter,)
  fieldsets = (
    (None, {
      'fields': ('title', 'address', 'site_url', 'impressum_text', 'emergency_pdf'),
      'classes': ('wide',)
    }), USERINFO_FIELDSET,
    (u'Einträge', {
      'fields': (('max_content_information', 'max_content_activity', 'max_content'),),
      'classes': ('wide',)
    }),
    ('Buchungen', {
      'fields': (('max_booking_days', 'booking_unit'),),
      'classes': ('wide',)
    })
  )
  inlines = (BookableInline, AdInline)

  def get_queryset(self, request):
    queryset = super(BuildingAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    return queryset.filter(id__in=request.user.location_set.values('building'))

  def board_list(self, building):
    return '<br>'.join(board.title for board in building.board_set.order_by('title'))
  board_list.short_description = 'Bildschirme'
  board_list.allow_tags = True

  def apartment_count(self, building):
    return Location.objects.filter(building=building).exclude(apartment=None).count()
  apartment_count.short_description = 'Anzahl Wohnungen'

  def site_link(self, building):
    return '<a href="{0}">{0}</a>'.format(building.site_url)
  site_link.allow_tags = True
  site_link.short_description = 'Website'

@admin.register(Board)
class BoardAdmin(GenericAdmin):
  list_display = ('title', 'building', 'last_request', 'status')
  list_filter = (BuildingFilter,)
  fieldsets = (
    (None, {
      'fields': ('title', 'building', 'description', 'key', 'last_request')
    }), USERINFO_FIELDSET
  )
  readonly_fields = GenericAdmin.readonly_fields + ('last_request', 'key')

  def changelist_view(self, request, *args, **kwargs):
    if request.user.is_superuser:
      return super(BoardAdmin, self).changelist_view(request, *args, **kwargs)
    try:
      current_actions = self.actions
      self.actions = None
      response = super(BoardAdmin, self).changelist_view(request, *args, **kwargs)
    finally:
      self.actions = current_actions
    return response

  def get_queryset(self, request):
    queryset = super(BoardAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    return queryset.filter(building__id__in=request.user.location_set.values('building'))

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == 'building' and not request.user.is_superuser:
      kwargs['queryset'] = Building.objects.filter(id__in=request.user.location_set.values('building'))
    return super(BoardAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

  def content_count(self, board):
    return board.content_set.count()
  content_count.short_description = u'Anzahl Einträge'

@admin.register(Content)
class ContentAdmin(GenericAdmin):
  list_display = ('title', 'type', 'text', 'rsvp_count', 'building', 'created', 'creator', 'is_active', 'is_online')
  list_filter = (BuildingFilter, 'type')
  search_fields = ('title', 'text')
  list_editable = ('is_active',)
  fieldsets = (
    (None, {
      'fields': (('type', 'is_active'), 'title', 'text', 'building', 'image', 'pdf', 'expiry')
    }), USERINFO_FIELDSET
  )
  inlines = (RsvpInline, MetadataInline)

  def get_queryset(self, request):
    queryset = super(ContentAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    return queryset.filter(building__in=request.user.location_set.values('building'))

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == 'building' and not request.user.is_superuser:
      kwargs['queryset'] = Building.objects.filter(id__in=request.user.location_set.values('building'))
    return super(ContentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

  def rsvp_count(self, obj):
    return obj.rsvp_set.count() if obj.type == 'activity' else '';
  rsvp_count.short_description = 'RSVP'

  def is_online(self, obj):
    return obj.is_active and (obj.expiry == None or obj.expiry > datetime.now(pytz.UTC))
  is_online.boolean = True
  is_online.short_description = 'Online'

@admin.register(Bookable)
class BookableAdmin(GenericAdmin):
  list_display = ('title', 'building', 'bookings_count', 'is_available')
  list_filter = (BuildingFilter, 'is_available')
  fieldsets = (
    (None, {
      'fields': (('title', 'is_available'), 'building'),
      'classes': ('wide',)
    }), USERINFO_FIELDSET
  )
  inlines = (BookingInline,)
  ordering = ('title',)

  def get_queryset(self, request):
    queryset = super(BookableAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    return queryset.filter(building__in=request.user.location_set.values('building'))

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == 'building' and not request.user.is_superuser:
      kwargs['queryset'] = Building.objects.filter(id__in=request.user.location_set.values('building'))
    return super(BookableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

  def bookings_count(self, obj):
    return obj.booking_set.count()
  bookings_count.short_description = 'Buchungen'

@admin.register(Booking)
class BookingAdmin(GenericAdmin):
  #actions = None
  #form = BookingAdminForm
  list_display = ('title', 'building', 'start_time', 'end_time', 'creator')
  list_filter = (BuildingFilter, BookableFilter)
  search_fields = ('creator__first_name', 'creator__last_name')
  readonly_fields = GenericAdmin.readonly_fields + ('title', 'building', 'bookable', 'start_time', 'end_time')
  fieldsets = (
    (None, {
      'fields': ('title', 'start_time', 'end_time'),
      'classes': ('wide',)
    }), USERINFO_FIELDSET
  )

  def has_add_permission(self, request):
    return False

  def has_delete_permission(self, request, obj=None):
    return True

  def get_queryset(self, request):
    queryset = super(BookingAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return queryset
    return queryset.filter(bookable__building__in=request.user.location_set.values('building'))

  def building(self, obj):
    return obj.bookable.building
  building.short_description = 'Gebäude'

class SessionAdmin(admin.ModelAdmin):
  list_display = ('session_key', 'user', '_session_data', 'expire_date')
  readonly_fields = ('session_key', '_session_data')
  fieldsets = (
    (None, {
      'fields': ('session_key', '_session_data', 'expire_date')
    }),
  )

  def user(self, obj):
    data = self._session_data(obj)
    user_id = data.get('_auth_user_id', None)
    try:
      user = User.objects.get(id=user_id)
      url = urlresolvers.reverse('admin:%s_%s_change' % (user._meta.app_label, user._meta.module_name), args=(user.id,))
      return '<a href="%s">%s</a>' % (url, user)
    except:
      return ''
  user.short_description = u'Benutzerin'
  user.allow_tags = True

  def _session_data(self, obj):
    return obj.get_decoded()
  _session_data.short_description = u'Sitzungs-Daten'
  _session_data.is_readonly = True

  def has_add_permission(self, request):
    return False

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
#patch_admin(User)

admin.site.register(Session, SessionAdmin)
