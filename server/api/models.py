# -*- coding: utf-8 -*-

import hashlib, pytz
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models

from adminsortable.models import SortableMixin

from utils import *

class GenericModel(models.Model):
  title = models.CharField('Titel', max_length=255)
  created = models.DateTimeField('Erstellungsdatum', auto_now_add=True)
  modified = models.DateTimeField(u'Letzte Änderung', auto_now=True)
  creator = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_creator', verbose_name='Erstellt von')
  modifier = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_modifier', verbose_name=u'Zuletzt geändert von')

  class Meta:
    abstract = True

  def __unicode__(self):
    return unicode(self.title)

  def __json__(self, building):
    return {
      'id': self.id,
      'title': self.title,
      'created': self.created,
      'modified': self.modified,
      'creator': self.creator.userprofile.__json__(building),
      'modifier': self.modifier.userprofile.__json__(building)
    }

class UserProfile(models.Model):
  user = models.OneToOneField(User, primary_key=True)
  image = models.ImageField(upload_to='profiles/%Y/%m', blank=True, verbose_name='Bild')
  temp_password = models.CharField(u'Temporäres Kennwort', max_length=255, blank=True)
  reset_date = models.DateTimeField(u'Gültig bis', blank=True, null=True, help_text='')

  class Meta:
    verbose_name = 'Optionen'
    verbose_name_plural = 'Optionen'
    ordering = ('user__username',)

  def __unicode__(self):
    return user_unicode(self.user)

  def get_group(self, building, apartment=None):
    if self.user.is_superuser:
      return 'Administration'
    elif self.user.is_staff:
      return 'Hausverwaltung'
    else:
      if not apartment:
        apartment = self.get_apartment(building)
      if apartment:
        return 'Top %s' % apartment
    return None

  def get_location(self, building):
    locations = self.user.location_set.select_related().filter(building=building)
    if locations.count() > 0:
      locations_with_apartment = locations.exclude(apartment=None)
      if locations_with_apartment.count() > 0:
        location = locations_with_apartment[0]
        return 'Top %s, %s' % (location.apartment, location.building)
      location = locations[0]
      return location.building
    return None

  def get_apartment(self, building=None):
    if building:
      locations = list(self.user.location_set.select_related().filter(building=building).exclude(apartment=None)[:1])
      if len(locations) > 0:
        return unicode(locations[0].apartment)
    return None

  def __json__(self, building):
    apartment = self.get_apartment(building)
    group = self.get_group(building, apartment)
    json = {
      'id': self.user_id,
      'username': self.user.username,
      'name': self.user.username,
      'reset_date': self.reset_date,
      'group': group,
      'building': getattr(building, 'title', None),
      'apartment': apartment or group,
      'image': {}
    }
    if (self.image):
      json['image'] = {
        'url': unicode(self.image.url),
        'width': self.image.width,
        'height': self.image.height
      }
    return json

class Building(GenericModel):
  address = models.CharField(u'Adresse', max_length=255)
  site_url = models.URLField(u'Website', max_length=255)
  max_content = models.PositiveIntegerField(u'Max. dargestellte Einträge vom Typ Suche & Biete', default=20)
  max_content_information = models.PositiveIntegerField(u'Max. dargestellte Einträge vom Typ Information', default=20)
  max_content_activity = models.PositiveIntegerField(u'Max. dargestellte Einträge vom Typ Aktivität', default=20)
  impressum_text = models.TextField('Impressum', blank=True)
  emergency_pdf = models.FileField('PDF mit Notfallnummern', upload_to=get_upload_path, max_length=255, blank=True, null=True, validators=[validate_pdf_file])
  booking_unit = models.PositiveIntegerField(u'Buchungseinheit', default=1)
  max_booking_days = models.PositiveIntegerField(u'Buchungszeitraum', default=60)
  last_update = models.DateTimeField('Letzte Aktualisierung')

  class Meta:
    verbose_name = u'Gebäude'
    verbose_name_plural = u'Gebäude'
    ordering = ('title',)

  def __unicode__(self):
    return '%s - %s' % (self.title, self.address)

  def save(self, *args, **kwargs):
    self.last_update = datetime.now(pytz.UTC)
    return super(Building, self).save(*args, **kwargs)

class Location(models.Model):
  user = models.ForeignKey(User)
  building = models.ForeignKey(Building, verbose_name=u'Titel')
  apartment = models.CharField('Wohnung', max_length=10, null=True, blank=True)

  class Meta:
    verbose_name = u'Gebäude'
    verbose_name_plural = u'Gebäude'

  def __unicode__(self):
    if self.apartment:
      return u'Top %s, %s' % (self.apartment, self.building)
    return unicode(self.building)

class Board(GenericModel):
  building = models.ForeignKey(Building, verbose_name=u'Gebäude')
  last_request = models.DateTimeField('Letzte Anfrage', null=True, blank=True, default=None)
  last_notification = models.DateTimeField(null=True, blank=True, default=None)
  key = models.CharField(u'Schlüssel', max_length=255)
  description = models.TextField('Beschreibung', blank=True)

  class Meta:
    verbose_name = 'Bildschirm'
    verbose_name_plural = 'Bildschirme'
    ordering = ('title',)

  def save(self, *args, **kwargs):
    if not self.key:
      self.key = hashlib.sha256(str(datetime.now())).hexdigest()
    super(Board, self).save(*args, **kwargs)

  def status(board):
    if not board.last_request:
      return False
    return datetime.now(pytz.UTC) - board.last_request < timedelta(minutes=1)
  status.boolean = True

  def __unicode__(self):
    return u'%s, %s' % (self.building, self.title)

class Content(GenericModel):
  CONTENT_TYPES = (
    ('offer', 'Angebot'),
    ('request', 'Gesuch'),
    ('activity', u'Aktivität'),
    ('information', 'Information')
  )
  building = models.ForeignKey(Building, verbose_name=u'Gebäude')
  type = models.CharField('Typ', max_length=16, choices=CONTENT_TYPES, blank=True)
  text = models.TextField(blank=True)
  expiry = models.DateTimeField(u'Ablaufdatum', blank=True, null=True)
  is_active = models.BooleanField('aktiv', default=True)
  image = models.ImageField(upload_to=get_upload_path, max_length=255, blank=True, verbose_name='Bild')
  #thumbnail = models.ImageField(upload_to=get_upload_path, max_length=255, blank=True, verbose_name='Vorschaubild')
  pdf = models.FileField(upload_to=get_upload_path, max_length=255, blank=True, verbose_name='PDF', validators=[validate_pdf_file])

  class Meta:
    verbose_name = 'Eintrag'
    verbose_name_plural = u'Einträge'
    ordering = ('-created',)

  def get_metadata(self, key=None):
    if key:
      metadata = self.metadata_set.filter(key=key)
      if metadata.count() > 0:
        return metadata[0].value
    else:
      return dict(self.metadata_set.values_list('key', 'value'))
    return None

  def save(self, *args, **kwargs):
    self.building.last_update = datetime.now(pytz.UTC)
    self.building.save()
    return super(Content, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    print(111111)
    return super(Content, self).save(*args, **kwargs)

  def __unicode__(self):
    return u'%s: %s' % (self.get_type_display(), self.title)

  def __json__(self, user=None):
    json = super(Content, self).__json__(self.building)
    json['type'] = self.type
    json['text'] = self.text
    json['image'] = {}
    json['pdf'] = {}
    json['location'] = self.get_metadata(key='location')
    json['date'] = self.get_metadata(key='date')
    if (self.image):
      json['image'] = {
        'url': unicode(self.image.url),
        'width': self.image.width,
        'height': self.image.height
      }
    rsvp = {
      'yes': 0,
      'no': 0,
      'maybe': 0,
      'unknown': 0,
      'selected': None
    }
    if user:
      try:
        rsvp['selected'] = RSVP.objects.get(creator=user, activity_id=self).title
      except:
        pass
    groups = self.rsvp_set.values('title').annotate(count=models.Count('title'))
    for group in groups:
      if 'count' in group:
        rsvp[group['title']] = group['count']
    json['rsvp'] = rsvp
    json['pdf'] = unicode(self.pdf.url) if self.pdf else None
    return json

from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Content)
def delete_current_image(sender, instance, *args, **kwargs):
  try:
    if instance.pk:
      content = Content.objects.get(pk=instance.pk)
      if instance.image and instance.image != content.image:
        content.image.delete(False)
  except:
    pass

class Metadata(models.Model):
  content = models.ForeignKey(Content)
  key = models.CharField('Name', max_length=255)
  value = models.TextField('Wert', blank=True)

  class Meta:
    verbose_name = 'Metadatum'
    verbose_name_plural = 'Metadaten'
    ordering = ('key',)

  def __unicode__(self):
    return u'%s (%s)' % (self.value, self.key,)

class Bookable(GenericModel, SortableMixin):
  MAX_BOOKINGS_PERIOD_CHOICES = (
    ('day', 'Tag'),
    ('week', 'Woche'),
    ('month', 'Monat')
  )
  building = models.ForeignKey(Building, verbose_name=u'Gebäude')
  position = models.PositiveIntegerField(default=1, editable=False, db_index=True)
  is_available = models.BooleanField('verfügbar', default=True)
  #min_booking_period = models.PositiveIntegerField(u'Mindestbuchungslänge')
  #max_bookings = models.PositiveIntegerField('Max. Buchungsanzahl')
  #max_bookings_period = models.CharField('Buchungszeitraum', max_length=20, choices=MAX_BOOKINGS_PERIOD_CHOICES)

  class Meta:
    verbose_name = 'Buchbares Objekt'
    verbose_name_plural = 'Buchbare Objekte'
    ordering = ('position',)

class Booking(GenericModel):
  start_time = models.DateTimeField('Beginn')
  end_time = models.DateTimeField('Ende')
  bookable = models.ForeignKey(Bookable, verbose_name='Buchbares Objekt')

  class Meta:
    verbose_name = 'Buchung'
    verbose_name_plural = 'Buchungen'
    ordering = ('-start_time', '-end_time')

  def save(self, *args, **kwargs):
    self.title = self.bookable.title
    return super(Booking, self).save(*args, **kwargs)

class RSVP(GenericModel):
  activity = models.ForeignKey(Content)

  CHOICES = (
    ('unknown', u'Weiß noch nicht'),
    ('yes', 'Ja'),
    ('maybe', 'Vielleicht'),
    ('no', 'Nein')
  )

  class Meta:
    verbose_name = 'Teilnahme'
    verbose_name_plural = 'Teilnahmen'

class Ad(SortableMixin):
  building = models.ForeignKey(Building, verbose_name=u'Gebäude')
  image = models.ImageField(upload_to=get_upload_path, max_length=255, verbose_name='Bild')
  position = models.PositiveIntegerField(default=1, editable=False, db_index=True)

  class Meta:
    verbose_name = 'Werbung'
    verbose_name_plural = 'Werbungen'
    ordering = ('position',)

  def __unicode__(self):
    return unicode(self.image)
