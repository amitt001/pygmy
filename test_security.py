"""Security regressions using an isolated database and synthetic credentials."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
TEMP = tempfile.TemporaryDirectory()
os.environ['PYGMY_SECRET_KEY'] = 'test-only-api-secret-never-use-in-production'
os.environ['DJANGO_SECRET_KEY'] = 'test-only-ui-secret-never-use-in-production'
os.environ['PYGMY_ALLOWED_HOSTS'] = 'testserver'
os.environ['DJANGO_SETTINGS_MODULE'] = 'pygmyui.settings'

from pygmy.core.initialize import initialize_test
initialize_test(db_url='sqlite:///' + TEMP.name + '/test.db')
from pygmy.database.base import Model
from pygmy.config import config
from pygmy.model.link import Link
from pygmy.model.user import User
from pygmy.model.clickmeta import ClickMeta
Model.metadata.create_all(config.db.engine)
from pygmy.rest.manage import app
# The UI and API both use a pygmy package; run UI tests in a separate process.
import django
sys.path.insert(0, str(ROOT / 'pygmyui'))
# Let the UI URL module coexist with the already imported API package.
import pygmy
pygmy.__path__.append(str(ROOT / 'pygmyui' / 'pygmy'))
django.setup()
from django.test import Client, override_settings


class SecurityTests(unittest.TestCase):
    def test_demo_blocks_all_account_api_paths(self):
        with patch.dict(os.environ, PYGMY_DEMO_MODE='1'):
            client = app.test_client()
            for path in ['/api/user', '/api/user/1', '/api/user/links', '/api/login', '/token/refresh']:
                for method in ['get', 'post']:
                    response = getattr(client, method)(path)
                    self.assertEqual(response.status_code, 403, (path, method))
            self.assertEqual(client.get('/favicon.ico').status_code, 204)
            response = client.post('/api/shorten', json={'long_url': 'https://example.com/demo', 'owner': '999999'})
            self.assertEqual(response.status_code, 201, response.json)
            self.assertIsNone(response.json['owner'])

    def test_self_hosted_accounts_work_and_password_is_hashed(self):
        with patch.dict(os.environ, PYGMY_DEMO_MODE='0'):
            client = app.test_client()
            user = {'email': 'synthetic@example.com', 'password': 'Synthetic-pass-123', 'f_name': 'Test', 'l_name': 'User'}
            response = client.post('/api/user', json=user)
            self.assertEqual(response.status_code, 201, response.json)
            response = client.post('/api/login', json=user)
            self.assertEqual(response.status_code, 200, response.json)
            self.assertIn('access_token', response.json)
            uid = config.db.store.query(User).filter_by(email=user['email']).one().id
            self.assertEqual(client.get('/api/user/' + str(uid)).status_code, 401)
            headers = {'JWT_Authorization': 'Bearer ' + response.json['access_token']}
            self.assertEqual(client.get('/api/user/' + str(uid), headers=headers).status_code, 200)
            self.assertNotEqual(config.db.store.query(User).filter_by(email=user['email']).one().password, user['password'])

    @override_settings(PYGMY_DEMO_MODE=True)
    def test_demo_ui_has_notice_no_forms_and_blocks_direct_requests(self):
        client = Client()
        client.cookies['refresh_token'] = 'stale-demo-token'
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'signup and login are unavailable')
        self.assertNotContains(response, 'ajax-register-form')
        self.assertNotContains(response, 'ajax-login-form')
        for path in ['/signup', '/login', '/logout', '/dashboard']:
            self.assertEqual(client.get(path).status_code, 403)
            self.assertEqual(client.post(path).status_code, 403)

    @override_settings(PYGMY_DEMO_MODE=False)
    def test_self_hosted_ui_keeps_forms_and_secures_auth_cookies(self):
        client = Client()
        self.assertContains(client.get('/'), 'ajax-register-form')
        with patch('user_auth.views.pygmy_client_object') as api:
            api.return_value.login.return_value = {'email': 'synthetic@example.com', 'f_name': 'Test', 'refresh_token': 'synthetic-refresh', 'access_token': 'synthetic-access'}
            response = client.post('/login', {'email': 'synthetic@example.com', 'password': 'Synthetic-pass-123'})
            self.assertEqual(response.status_code, 302)
            for name in ['access_token', 'refresh_token']:
                self.assertTrue(response.cookies[name]['secure'])
                self.assertTrue(response.cookies[name]['httponly'])
                self.assertEqual(response.cookies[name]['samesite'], 'Lax')

    @override_settings(PYGMY_DEMO_MODE=True)
    def test_demo_preserves_csrf_cookie_for_shortening(self):
        client = Client(enforce_csrf_checks=True)
        client.get('/')
        token = client.cookies['csrftoken'].value
        with patch('pygmy.views.pygmy_client_object') as api:
            api.return_value.shorten.return_value = {'short_code': 'test'}
            response = client.post('/shorten', {'long_url': 'https://example.com', 'custom_url': '', 'secret_key': ''}, HTTP_X_CSRFTOKEN=token)
            self.assertEqual(response.status_code, 302)
            api.return_value.shorten.assert_called_once()

    @override_settings(PYGMY_DEMO_MODE=True)
    def test_demo_ui_and_api_shortening_contract(self):
        import requests
        from urllib.parse import urlsplit
        def send(session, method, url, **kwargs):
            target = urlsplit(url)
            path = target.path + ('?' + target.query if target.query else '')
            headers = {k: v for k, v in kwargs.get('headers', {}).items() if v is not None}
            result = app.test_client().open(path, method=method, json=kwargs.get('json'), headers=headers)
            response = requests.Response()
            response.status_code = result.status_code
            response._content = result.data
            response.headers.update(result.headers)
            response.url = url
            return response
        with patch.dict(os.environ, PYGMY_DEMO_MODE='1'), patch('requests.sessions.Session.request', new=send):
            response = Client().post('/shorten', {'long_url': 'https://example.com/full-demo-contract', 'custom_url': '', 'secret_key': ''}, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Copy To Clipboard')

    def test_demo_preview_and_normal_redirect(self):
        with patch('pygmy.views.pygmy_client_object') as api:
            api.return_value.unshorten.return_value = {'long_url': 'https://example.com'}
            with override_settings(PYGMY_DEMO_MODE=True):
                response = Client().get('/abc')
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Automatic redirects are disabled')
            with override_settings(PYGMY_DEMO_MODE=False):
                response = Client().get('/abc')
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response['Location'], 'https://example.com')

    def test_database_url_does_not_depend_on_logging(self):
        from pygmy.database.base import BaseDatabase
        database = {'engine': 'postgresql', 'url': '{engine}://{user}:{password}@{host}:{port}/{db_name}', 'user': 'synthetic', 'password': 'test-only', 'host': 'localhost', 'port': '5432', 'db_name': 'synthetic'}
        with patch.dict(os.environ, {}, clear=True), patch.object(config, 'database', database):
            self.assertEqual(BaseDatabase().db_url, 'postgresql://synthetic:test-only@localhost:5432/synthetic')

    def test_unknown_hosts_are_rejected(self):
        self.assertEqual(Client().get('/', HTTP_HOST='untrusted.example').status_code, 400)

    def assertContains(self, response, text):
        self.assertIn(text, response.content.decode())

    def assertNotContains(self, response, text):
        self.assertNotIn(text, response.content.decode())


if __name__ == '__main__':
    unittest.main()
