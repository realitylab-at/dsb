import logging
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from django.db.models.signals import post_save
from django.dispatch import receiver

from apscheduler.scheduler import Scheduler

from api.models import User

logging.basicConfig()

cron = Scheduler()

@cron.interval_schedule(minutes=5)
def check_boards():
  from api.models import Building, User
  board_list = []
  for building in Building.objects.all():
    message = ''
    for board in building.board_set.all():
      if board.last_request and board.status() == False and board.last_notification and board.last_request > board.last_notification:
        message += 'Bildschirm %s ist seit %s nicht mehr online.\n' % (board.title, board.last_request)
        board.last_notification = board.last_request
        board.save()
    if len(message) > 0:
      recipients = User.objects.filter(is_staff=True, location__building=building).values_list('email', flat=True)
      if len(recipients) > 0:
        send_mail('%s | %s' % (building.title, 'Warnung!'), message, 'root@realitylab.at', recipients, fail_silently=False)

cron.start()
cron.print_jobs()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  from api.models import UserProfile
  if created:
    profile, is_new = UserProfile.objects.get_or_create(user=instance)

def validate_pdf_file(value):
  if not value.name.endswith('.pdf'):
    raise ValidationError(u'Dieses Feld erlaubt nur PDF-Dateien.')

def user_unicode(user):
  if (user.first_name and user.last_name):
    return u'%s %s' % (user.first_name, user.last_name)
  return unicode(user.username)

def get_upload_path(instance, filename):
  building = getattr(instance, 'building', instance)
  now = datetime.now()
  month = '{0:02d}'.format(now.month)
  return '%s/%s/%s/%s' % (building.title, now.year, month, filename)
