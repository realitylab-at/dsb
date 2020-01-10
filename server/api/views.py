# -*- coding: utf-8 -*-

from api.models import *
from server import settings

from django.http import HttpResponse
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth import hashers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone

from jsonrpc import jsonrpc_method
from jsonrpc.exceptions import *

from datetime import datetime, timedelta

import time
import pytz

def has_permission(user, building):
  user_has_building = user.location_set.filter(building=building).count() > 0
  user_has_apartment = user.location_set.filter(building=building).values('apartment').count() > 0
  return user and building and user.is_active and (user.is_superuser or user.is_staff and user_has_building or user_has_building and user_has_apartment)

def pwgen(length):
  import random
  password = ()
  char_set = ('bdfghklmnnnprssstwz', u'aaaeeeiioouu',)
  for i in range(length):
    char_list = char_set[i % 2]
    char = char_list[random.randint(0, len(char_list) - 1)]
    password += (char.upper(),) if i == 0 else (char,)
  return ''.join(password)

def get_json_date(date):
  return int(time.mktime(date.timetuple()) * 1000)

class ApiError(Error):
  code = 200
  status = 200
  message = 'Unknown API error'

  def __init__(self, message=None, data=()):
    super(ApiError, self).__init__(message)
    self.message = message
    self.data = data

@jsonrpc_method('ping')
def ping(request, name=''):
  if name:
    return u'Hello, %s!' % name
  return 'pong'

@jsonrpc_method('auth_test', authenticated=True)
def auth_test(request):
  return u'Hello, %s!' % request.user.username

@jsonrpc_method('sign_in')
def sign_in(request, username, password, building_id):
  from django.contrib.auth import authenticate, login
  GenericError = ApiError(data=((None, 'Derzeit ist die Anmeldung nicht möglich. Bitte wenden Sie sich an Ihre Hausverwaltung.'), ))
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise GenericError
  if user.userprofile.reset_date:
    if datetime.now(pytz.UTC) > user.userprofile.reset_date:
      user = None
    elif password != user.userprofile.temp_password:
      user = None
  else:
    user = None
  if not user:
    user = authenticate(username=username, password=password)
    if user:
      user.userprofile.reset_date = None
      user.userprofile.temp_password = hashers.make_password(None)
      user.userprofile.save()
  if user:
    if user.is_active:
      building = Building.objects.get(id=building_id)
      if has_permission(user, building):
        if (not user.userprofile.reset_date):
          login(request, user)
          request.session.set_expiry(0)
        return user.userprofile.__json__(building)
  raise GenericError

@jsonrpc_method('sign_out')
def sign_out(request):
  from django.contrib.auth import logout
  logout(request)
  return True

@jsonrpc_method('get_impressum')
def get_impressum(request, building_id):
  building = Building.objects.get(pk=building_id)
  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)
  return building.impressum_text

@jsonrpc_method('get_content')
def get_content(request, building_id, board_key=None, timestamp=None, last_update=None):

  building = Building.objects.get(pk=building_id)
  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)

  if board_key:
    try:
      board = Board.objects.get(key=board_key)

      if board:
        board.last_request = datetime.now(pytz.UTC)
        board.save()

    except Board.DoesNotExist:
      pass

  if last_update:
    last_update = datetime.fromtimestamp(last_update / 1000, pytz.UTC)
    if building.last_update < last_update:
      return None

  result = {
    'ads': [],
    'content': []
  }

  collection = building.content_set.select_related().filter(Q(is_active=True), Q(creator__is_active=True), Q(creator__location__building=building), Q(expiry=None) | Q(expiry__gt=datetime.now(pytz.UTC))).order_by('-created')

  if timestamp is not None:
    date = datetime.fromtimestamp(timestamp / 1000)
    collection = collection.filter(created__gt=date)

  information = collection.filter(type='information')[:building.max_content_information]
  activity = collection.filter(type='activity')[:building.max_content_activity]
  classified = collection.filter(Q(type='offer') | Q(type='request'))[:building.max_content]
  collection = list(information) + list(activity) + list(classified)

  for content in collection:
    result['content'].append(content.__json__(user=request.user))

  if (request.user.is_authenticated()):
    result['session'] = request.user.userprofile.__json__(building)

  for ad in Ad.objects.select_related().filter(building=building).order_by('position'):
    result['ads'].append(ad.image.url)

  result['emergency_pdf'] = building.emergency_pdf.url if building.emergency_pdf else None
  result['title'] = unicode(building)
  return result

@jsonrpc_method('add_content', authenticated=True)
def add_content(request, building_id, type, title, text, date=None, location=None, image=None, id=None):
  user = request.user
  if user.is_active == False:
    raise InvalidCredentialsError()
  building = Building.objects.get(pk=building_id)
  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)
  if not has_permission(user, building):
    raise InvalidCredentialsError()
  if (id is not None):
    content = Content.objects.get(pk=id)
    content.type = type
    content.title = title
    content.text = text
    content.modifier = user
  else:
    content = Content(type=type, title=title, text=text, building=building, creator=user, modifier=user)
  if type == 'activity':
    if not date or not location:
      raise InvalidParamsError('Date or location missing.')
    content.save()
    content.metadata_set.all().delete()
    Metadata.objects.create(content=content, key='date', value=date).save()
    Metadata.objects.create(content=content, key='location', value=location).save()
  else:
    content.save()
  if image is not None:
    import base64, hashlib
    from django.core.files.base import ContentFile
    info, b64data = image.split(',')
    # "data:image/jpeg;base64"
    _, type = info.split(':')[1].split(';')[0].split('/')
    filename = '%s.%s' % (hashlib.sha1(image).hexdigest(), type)
    file = ContentFile(base64.b64decode(b64data))
    content.image.save(filename, file)
    #from PIL import Image
    #content.thumbnail.save('thumbnail-' + filename, file)
    #filename = content.thumbnail.file.name
    #image = Image.open(filename)
    #image.thumbnail((200, 200), Image.ANTIALIAS)
    #image.save(filename)
  return content.__json__(user=user)

@jsonrpc_method('delete_content', authenticated=True)
def delete_content(request, id):
  user = request.user
  if user.is_active == False:
    raise InvalidCredentialsError()
  content = Content.objects.get(pk=id)
  if user.is_superuser or user.is_staff or content.creator == user:
    content.is_active = False
    content.save()
  return content.__json__(user=user)

@jsonrpc_method('send_message', authenticated=True)
def send_message(request, building_id, type, id=None, title=None, text=None, rsvp=None):
  user = request.user
  if user.is_active == False:
    raise InvalidCredentialsError()
  building = Building.objects.get(pk=building_id)
  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)
  if not has_permission(user, building):
    raise InvalidCredentialsError('No permission to write to this board.')
  if id:
    content = building.content_set.get(pk=id)
    if not content:
      raise InvalidParamsError('Content with id %s does not exist.' % id)
    recipients = [content.creator.email, request.user.email]
    rsvp_summary = {}
    if rsvp:
      obj, created = RSVP.objects.get_or_create(activity=content, creator=user, modifier=user)
      if (obj.title != rsvp):
        obj.title = rsvp
      obj.save()
      content.save()
      rsvp_summary = content.__json__()['rsvp']
      rsvp_summary['sender'] = filter(lambda x: x[0] == obj.title, RSVP.CHOICES)[0][1]
    type = type if type == 'activity' else 'classified'
    text = render_to_string('mail/%s.txt' % type, {
      'location': content.creator.userprofile.get_location(building),
      'title': content.title,
      'sender': {
        'apartment': user.userprofile.get_apartment(building) or user.userprofile.get_group(building),
        'email': user.email
      },
      'body': text,
      'rsvp': rsvp_summary,
      'url': building.site_url
    })
  else:
    recipients = User.objects.filter(location__building=building, groups__name='Hausverwaltung').values_list('email', flat=True)
    text = render_to_string('mail/%s.txt' % type, {
      'building': building,
      'apartment': user.userprofile.get_apartment(building) or user.userprofile.get_group(building),
      'body': text,
      'sender': user.email,
      'url': building.site_url
    })
  #print 'Send e-mail from %s to %s' % (user.email, recipients)
  return send_mail('%s | %s' % (building.title, title), text, user.email, recipients, fail_silently=False)

@jsonrpc_method('get_bookings')
def get_bookings(request, building_id, offset=0, limit=10):

  local_timezone = pytz.timezone(settings.TIME_ZONE)
  building = Building.objects.get(pk=building_id)

  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)

  user = request.user
  timestamp = local_timezone.normalize(timezone.now())
  hour = timestamp.hour

  while hour % building.booking_unit != 0:
    hour -= 1
  date = timestamp.replace(hour=hour, minute=0, second=0, microsecond=0)

  result = {
    'timestamp': date,
    'dates': [],
    'bookables': [],
    'unit': building.booking_unit
  }

  dates = []
  page_size = building.booking_unit * limit
  start_hours = offset * page_size
  end_hours = (offset + 1) * page_size
  start_time = date + timedelta(hours=start_hours)
  end_time = date + timedelta(hours=end_hours)

  for hours in range(start_hours, end_hours, building.booking_unit):
    dates.append(get_json_date(date + timedelta(hours=hours)))

  result['dates'] = dates
  bookables = building.bookable_set.filter(is_available=True).order_by('position')

  for bookable in bookables:
    bookable_data = {
      'id': bookable.id,
      'title': bookable.title,
      'status': []
    }

    bookings = {}

    for booking in bookable.booking_set.filter(start_time__gte=start_time, end_time__lte=end_time):
      date = get_json_date(local_timezone.normalize(booking.start_time))

      if user == booking.creator:
        bookings[date] = 1
      else:
        apartment = booking.creator.userprofile.get_apartment(building)
        if apartment:
          bookings[date] = str(apartment)
        else:
          bookings[date] = ''

    for date in dates:
      bookable_data['status'].append(bookings[date] if date in bookings else 0)

    result['bookables'].append(bookable_data)
    result['max_booking_days'] = building.max_booking_days
    result['next'] = offset + 1 if offset < building.max_booking_days else -1
    result['prev'] = offset - 1 if offset > 0 else -1

  return result

@jsonrpc_method('update_bookings', authenticated=True)
def update_bookings(request, building_id, bookings):
  user = request.user

  if user.is_active == False:
    raise InvalidCredentialsError()

  building = Building.objects.get(pk=building_id)

  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)

  if not has_permission(user, building):
    raise InvalidCredentialsError('No permission to write to this board.')

  local_timezone = pytz.timezone(settings.TIME_ZONE)

  for date_index, date in enumerate(bookings['dates']):

    for bookable_data in bookings['bookables']:
      # status is either
      #    1 (user added booking)
      #    0 (no change)
      #   -1 (user removed booking)
      # or a string containing the apartment ID of another user (empty if not assigned)
      status = bookable_data['status'][date_index]

      # do nothing if booking was neither added nor removed
      if status != 1 and status != -1:
        continue

      bookable = Bookable.objects.get(id=bookable_data['id'])
      start_time = local_timezone.localize(datetime.fromtimestamp(date / 1000))
      end_time = start_time + timedelta(hours=building.booking_unit)

      try:
        existing_booking = bookable.booking_set.get(start_time=start_time)

        # user tries to overwrite booking by other user
        if existing_booking.creator != user:
          raise ApiError(data=((None, 'Zur gewünschten Zeit wurde inzwischen bereits eine Reservierung vorgenommen.'),))

        # user has removed booking
        if status == -1:
          existing_booking.delete()

      except Booking.DoesNotExist:
        # user has added booking
        if status == 1:
          booking = Booking(start_time=start_time, end_time=end_time, bookable=bookable, creator=user, modifier=user)
          booking.save()

  return True

@jsonrpc_method('password_reset')
def password_reset(request, username, building_id, temp_password=None, new_password=None):
  building = Building.objects.get(pk=building_id)
  if building == None:
    raise InvalidParamsError('Building with id %s does not exist.' % building_id)
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise ApiError(data=((None, 'Derzeit ist die Änderung Ihres Kennworts nicht möglich. Bitte wenden Sie sich an Ihre Hausverwaltung.'), ))
  if (user and user.is_active):
    if not has_permission(user, building):
      raise InvalidCredentialsError('No permission to write to this board.')
    elif user.userprofile.reset_date and temp_password and new_password and temp_password == user.userprofile.temp_password:
      user.password = hashers.make_password(new_password)
      user.save()
      user.userprofile.temp_password = hashers.make_password(None)
      user.userprofile.reset_date = None
      user.userprofile.save()
      return sign_in(request, username, new_password, building_id)
    else:
      password = pwgen(10)
      user.userprofile.temp_password = password
      user.userprofile.reset_date = datetime.now(pytz.UTC) + timedelta(hours=settings.TEMP_PASSWORD_EXPIRY)
      user.userprofile.save()
      title = u'%s | Zurücksetzung Ihres Kennworts' % building.title
      from django.utils import translation
      translation.activate('de-at')
      text = render_to_string('mail/password_reset.txt', {
        'location': user.userprofile.get_location(building),
        'password': password,
        'expiry': user.userprofile.reset_date,
        'url': building.site_url
      })
      translation.deactivate()
      return send_mail(title, text, user.email, (user.email,), fail_silently=False)
  raise InvalidParamsError('FIXME')
