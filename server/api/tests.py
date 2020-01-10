import json

from django.contrib.auth.models import User
from django.core.handlers.base import BaseHandler
from django.test import TestCase
from django.test.client import RequestFactory

from api import views
from api.models import Building, Location

class SignInTestCase(TestCase):

  def setUp(self):
    factory = RequestFactory()
    self.request = factory.post('/api/')

    # Adding middleware and session to the request object.
    # Source: https://gist.github.com/tschellenbach/925270
    handler = BaseHandler()
    handler.load_middleware()
    for middleware_method in handler._request_middleware:
      if middleware_method(self.request):
        raise Exception('Could not create request object; request middleware returned a response')

    self.password = '1234'
    self.admin = User.objects.create_superuser('admin', 'admin@local', self.password)
    self.account = User.objects.create_user('test', 'test@local', self.password)
    self.building = Building.objects.create(title='test', creator=self.admin, modifier=self.admin)
    self.other_building = Building.objects.create(title='test2', creator=self.admin, modifier=self.admin)
    self.location = Location.objects.create(building=self.building, user=self.account)
    self.location_with_apartment = Location.objects.create(building=self.building, apartment=1, user=self.account)
    self.update_account()

  def update_account(self, is_active=0, is_staff=0, is_superuser=0, location=None):
    self.account.is_active = is_active
    self.account.is_staff = is_staff
    self.account.is_superuser = is_superuser
    self.account.location_set.all().delete()
    if location:
      self.account.location_set.add(location)
    self.account.save()

  # Testing prerequisites

  def test_setup(self):
    account = User.objects.get(username=self.account.username)
    self.assertFalse(account.is_active)
    self.assertFalse(account.is_staff)
    self.assertFalse(account.is_superuser)
    from django.contrib.auth import authenticate

  def test_rpc_ping(self):
    result = views.ping(self.request, 'Board')
    self.assertEqual(result, 'Hello, Board!', 'Result must be the string "Hello, Board!"')

  # Testing inactive account

  def test_account(self):
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)

  def test_superuser_account(self):
    self.update_account(0, 0, 1)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_staff_account(self):
    self.update_account(0, 1, 0)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_staff_and_superuser_account(self):
    self.update_account(0, 1, 1)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  # Testing active account

  def test_active_account(self):
    self.update_account(1, 0, 0)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_active_superuser_account(self):
    self.update_account(1, 0, 1)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    result = views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(result['id'])
    self.update_account()

  # FIXME: Test fails
  def test_active_staff_account(self):
    self.update_account(1, 1, 0)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_active_staff_and_superuser_account(self):
    self.update_account(1, 1, 1)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    result = views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(result['id'])
    self.update_account()

  # Testing account with location

  def test_account_with_location(self):
    self.update_account(location=self.location)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)

  def test_superuser_account_with_location(self):
    self.update_account(0, 0, 1, location=self.location)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_staff_account_with_location(self):
    self.update_account(0, 1, 0, location=self.location)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_staff_and_superuser_account_with_location(self):
    self.update_account(0, 1, 1, location=self.location)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_active_account_with_location(self):
    self.update_account(1, 0, 0, location=self.location)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(context.exception.data)
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_active_superuser_account_with_location(self):
    self.update_account(1, 0, 1, location=self.location)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    result = views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(result['id'])
    self.update_account()

  def test_active_staff_account_with_location(self):
    self.update_account(1, 1, 0, location=self.location)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()

  def test_active_staff_and_superuser_account_with_location(self):
    self.update_account(1, 1, 1, location=self.location)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    result = views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(result['id'])
    self.update_account()

  # Testing account with location and apartment

  def test_active_account_with_location_and_apartment(self):
    self.update_account(1, 0, 0, location=self.location_with_apartment)
    result = views.sign_in(self.request, self.account.username, self.password, self.building.id)
    self.assertIsNotNone(result['id'])
    with self.assertRaises(views.ApiError) as context:
      views.sign_in(self.request, self.account.username, self.password, self.other_building.id)
    self.assertIsNotNone(context.exception.data)
    self.update_account()
