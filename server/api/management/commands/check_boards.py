from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from api.models import Board

class Command(BaseCommand):

  def handle(self, *args, **options):
    message = ''
    for board in Board.objects.all():
      if board.last_request and board.status() == False:
        message += 'Bildschirm %s ist seit %s nicht mehr online.\n' % (board.title, board.last_request)
    if len(message) > 0:
      send_mail('sunquarter_screen | %s' % 'Warnung!', message, 'root@localhost', ('root@localhost',), fail_silently=False)
      print message

