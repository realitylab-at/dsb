# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import api.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=api.utils.get_upload_path, max_length=255, verbose_name=b'Bild')),
                ('position', models.PositiveIntegerField(default=1)),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'Werbung',
                'verbose_name_plural': 'Werbungen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('last_request', models.DateTimeField(default=None, null=True, verbose_name=b'Letzte Anfrage', blank=True)),
                ('last_notification', models.DateTimeField(default=None, null=True, blank=True)),
                ('key', models.CharField(max_length=255, verbose_name='Schl\xfcssel')),
                ('description', models.TextField(verbose_name=b'Beschreibung', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Bildschirm',
                'verbose_name_plural': 'Bildschirme',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bookable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('position', models.PositiveIntegerField(default=1)),
                ('is_available', models.BooleanField(default=True, verbose_name=b'verf\xc3\xbcgbar')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'Buchbares Objekt',
                'verbose_name_plural': 'Buchbare Objekte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('start_time', models.DateTimeField(verbose_name=b'Beginn')),
                ('end_time', models.DateTimeField(verbose_name=b'Ende')),
                ('bookable', models.ForeignKey(verbose_name=b'Buchbares Objekt', to='api.Bookable')),
                ('creator', models.ForeignKey(related_name='api_booking_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='api_booking_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-start_time', '-end_time'),
                'verbose_name': 'Buchung',
                'verbose_name_plural': 'Buchungen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('address', models.CharField(max_length=255, verbose_name='Adresse')),
                ('site_url', models.URLField(max_length=255, verbose_name='Website')),
                ('max_content', models.PositiveIntegerField(default=20, verbose_name='Max. dargestellte Eintr\xe4ge')),
                ('max_content_information', models.PositiveIntegerField(default=20, verbose_name='Max. dargestellte Eintr\xe4ge vom Typ Information')),
                ('max_content_activity', models.PositiveIntegerField(default=20, verbose_name='Max. dargestellte Eintr\xe4ge vom Typ Aktivit\xe4t')),
                ('impressum_text', models.TextField(verbose_name=b'Impressum', blank=True)),
                ('emergency_pdf', models.FileField(validators=[api.utils.validate_pdf_file], upload_to=api.utils.get_upload_path, max_length=255, blank=True, null=True, verbose_name=b'PDF mit Notfallnummern')),
                ('creator', models.ForeignKey(related_name='api_building_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='api_building_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Geb\xe4ude',
                'verbose_name_plural': 'Geb\xe4ude',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('type', models.CharField(blank=True, max_length=16, verbose_name=b'Typ', choices=[(b'offer', b'Angebot'), (b'request', b'Gesuch'), (b'activity', 'Aktivit\xe4t'), (b'information', b'Information')])),
                ('text', models.TextField(blank=True)),
                ('expiry', models.DateTimeField(null=True, verbose_name='Ablaufdatum', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'aktiv')),
                ('image', models.ImageField(upload_to=api.utils.get_upload_path, max_length=255, verbose_name=b'Bild', blank=True)),
                ('pdf', models.FileField(blank=True, upload_to=api.utils.get_upload_path, max_length=255, verbose_name=b'PDF', validators=[api.utils.validate_pdf_file])),
                ('building', models.ForeignKey(verbose_name='Geb\xe4ude', to='api.Building')),
                ('creator', models.ForeignKey(related_name='api_content_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='api_content_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name': 'Eintrag',
                'verbose_name_plural': 'Eintr\xe4ge',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('apartment', models.PositiveIntegerField(null=True, verbose_name=b'Wohnung', blank=True)),
                ('building', models.ForeignKey(verbose_name='Titel', to='api.Building')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Geb\xe4ude',
                'verbose_name_plural': 'Geb\xe4ude',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255, verbose_name=b'Name')),
                ('value', models.TextField(verbose_name=b'Wert', blank=True)),
                ('content', models.ForeignKey(to='api.Content')),
            ],
            options={
                'ordering': ('key',),
                'verbose_name': 'Metadatum',
                'verbose_name_plural': 'Metadaten',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RSVP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Titel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Erstellungsdatum')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Letzte \xc4nderung')),
                ('activity', models.ForeignKey(to='api.Content')),
                ('creator', models.ForeignKey(related_name='api_rsvp_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='api_rsvp_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Teilnahme',
                'verbose_name_plural': 'Teilnahmen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'profiles/%Y/%m', verbose_name=b'Bild', blank=True)),
                ('temp_password', models.CharField(max_length=255, verbose_name='Tempor\xe4res Kennwort', blank=True)),
                ('reset_date', models.DateTimeField(help_text=b'', null=True, verbose_name='G\xfcltig bis', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user__username',),
                'verbose_name': 'Optionen',
                'verbose_name_plural': 'Optionen',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bookable',
            name='building',
            field=models.ForeignKey(verbose_name='Geb\xe4ude', to='api.Building'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookable',
            name='creator',
            field=models.ForeignKey(related_name='api_bookable_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookable',
            name='modifier',
            field=models.ForeignKey(related_name='api_bookable_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='board',
            name='building',
            field=models.ForeignKey(verbose_name='Geb\xe4ude', to='api.Building'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='board',
            name='creator',
            field=models.ForeignKey(related_name='api_board_creator', verbose_name=b'Erstellt von', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='board',
            name='modifier',
            field=models.ForeignKey(related_name='api_board_modifier', verbose_name='Zuletzt ge\xe4ndert von', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='building',
            field=models.ForeignKey(verbose_name='Geb\xe4ude', to='api.Building'),
            preserve_default=True,
        ),
    ]
