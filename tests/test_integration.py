import pytest
import sqlite3
import unittest
import requests

from pygmy.config import config


@pytest.mark.usefixtures('run_test_server')
class PygmyIntegrationTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.url = 'http://127.0.0.1:8001'

    @classmethod
    def teardown_class(cls):
        pass

    def teardown_method(self, _):
        return
        self.conn = sqlite3.connect(config.database['url'])
        self.cur = self.conn.cursor()
        tables = ['clickmeta', 'link', 'user']
        for table in tables:
            self.cur.execute('DELETE FROM {}'.format(table))
        self.conn.commit()
        self.conn.close()

    def setup_method(self, _):
        self._token = None
        self.cookies = None

    @property
    def token(self):
        if self._token is None:
            text = requests.get(self.url).text
            self._token = text[2906:2878 + 92]
        return self._token

    @property
    def headers(self):
        _headers = {'Cookie': 'csrftoken={}'.format(self.token), 'Content-Type': 'application/x-www-form-urlencoded'}
        # Cook the cookie
        if self.cookies is not None:
            co_di = requests.utils.dict_from_cookiejar(self.cookies)
            _headers['Cookie'] += '; ' + '; '.join(['{}= {}'.format(k, v) for k, v in co_di.items()])
        return _headers


    @property
    def data(self):
        return {
            'csrfmiddlewaretoken': self.token,
            'long_url': 'http://example.com',
            'custom_url': '',
            'secret_key': '',
            'remember_time': ''
        }

    @property
    def user_data(self):
        return {
            'csrfmiddlewaretoken': self.token,
            'f_name': 'Test',
            'l_name': 'Example',
            'email': 'test@example.com',
            'password': 'test@example',
            'confirm_password': 'test@example',
            'register-submit': 'Register Now'
        }

    @property
    def login_data(self):
        return {
            'csrfmiddlewaretoken': self.token,
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'login-submit': 'Log In'
        }

    def get_short_url_from_response(self, response):
        """
        :param response: requests.response object
        :return: str
        """
        resp_text = response.text
        idx = resp_text.find(self.url)
        return resp_text[idx:idx + 23]

    def test_shorten(self):
        data = self.data
        response = requests.post(self.url + '/shorten', data=data, headers=self.headers)
        short_url = self.get_short_url_from_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('value="{}"'.format(short_url) in response.text)
        self.assertTrue('Copy To Clipboard' in response.text)
        self.assertTrue('Shorten Another Link' in response.text)
        self.assertTrue('{}+'.format(short_url) in response.text)

        # Repeat shorten should return the same result
        response = requests.post(self.url + '/shorten', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('value="{}"'.format(short_url) in response.text)

        # Test a different url
        data['long_url'] = 'https://www.python.org/'
        response = requests.post(self.url + '/shorten', data=data, headers=self.headers)
        short_url = self.get_short_url_from_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('value="{}"'.format(short_url) in response.text)

    def test_already_shortened_url_error(self):
        err_msg = 'URL is already a pygmy shortened link'
        data = self.data
        data['long_url'] = 'https://pygy.co'
        response = requests.post(self.url + '/shorten', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(err_msg in response.text)

    def test_unshorten(self):
        data = self.data
        data['long_url'] = 'http://httpbin.com/'
        response = requests.post(self.url + '/shorten', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        short_url = self.get_short_url_from_response(response)

        response = requests.get(short_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.url, data['long_url'])

    # User access

    def test_signup(self):
        data = self.user_data
        data['email'] = 'ninja@example.com'
        response = requests.post(self.url + '/signup', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Welcome Test' in response.text)
        self.assertIsNotNone(response.cookies.get('access_token'))

        response = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('User exists' in response.text)

    def test_invalid_email_login(self):
        response = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        login_data = self.login_data.copy()
        login_data['email'] = 'wrong@email.com'
        response = requests.post(self.url + '/login', data=login_data, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertTrue('DASHBOARD' not in response.text)
        self.assertTrue('LOGIN' in response.text)
        self.assertTrue('No user found with email: {}'.format(login_data['email']) in response.text)

    def test_invalid_password_login(self):
        response = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        login_data = self.login_data.copy()
        login_data['password'] = 'i know it'
        response = requests.post(self.url + '/login', data=login_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('LOGIN' in response.text)
        self.assertTrue('Invalid username or password.' in response.text)

    def test_login(self):
        response = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        response = requests.get(self.url)
        self.assertTrue('LOGIN' in response.text)
        self.assertTrue('DASHBOARD' not in response.text)

        """Test redirection, hidden login, visible dashboard section, Welcome <username> section
        and dashboard table"""
        response = requests.post(self.url + '/login', data=self.login_data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.url == self.url + '/dashboard')
        self.assertTrue('DASHBOARD' in response.text)
        self.assertTrue('LOGIN' not in response.text)
        self.assertTrue('Welcome Test' in response.text)
        self.assertTrue('<table class="table table-bordered">' in response.text)

    def test_logout(self):
        _ = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        with requests.Session() as sess:
            _ = sess.post(self.url + '/login', data=self.login_data, headers=self.headers)
            self.cookies = sess.cookies
            response = sess.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('Welcome Test' in response.text)
            # logout
            response = sess.get(self.url + '/logout', headers=self.headers)
            self.assertEqual(response.url.strip('/'), self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('Welcome Test' not in response.text)

    def test_login_shorten(self):
        response = requests.post(self.url + '/signup', data=self.user_data, headers=self.headers)
        with requests.Session() as sess:
            response = sess.post(self.url + '/login', data=self.login_data, headers=self.headers)
            self.cookies = sess.cookies
            self.assertTrue('Welcome Test' in response.text)

            # Shorten the URL
            data = self.data
            data['long_url'] = 'https://example.com/1'
            response = sess.post(self.url + '/shorten', data=data, headers=self.headers)
            short_url = self.get_short_url_from_response(response)

            self.assertEqual(response.status_code, 200)
            self.assertTrue('value="{}"'.format(short_url) in response.text)
            self.assertTrue('Welcome Test' in response.text)
            self.assertTrue('Copy To Clipboard' in response.text)
            self.assertTrue('Shorten Another Link' in response.text)

            # verify its on dashboard
            response = sess.get(self.url + '/dashboard')
            short_code = short_url.split('/')[-1]
            self.assertEqual(response.status_code, 200)
            self.assertTrue('{}+'.format(short_code) in response.text)
            self.assertTrue('https://example.com/1' in response.text)

    def test_non_loggedin_dashboard(self):
        response = requests.get(self.url + '/dashboard')
        self.assertTrue(response.status_code == 400)
        self.assertTrue('Please log in again to continue.</h3>' in response.text)
    #
    # ###############
    # # Link Options
    # ###############
    #
    # def test_custom_links(self):
    #     pass
    #
    # def test_secret_links(self):
    #     pass
    #
    # def test_expiry_links(self):
    #     pass
    #
    # def test_custom_secret_links(self):
    #     pass
    #
    # def test_custom_expiry_links(self):
    #     pass
    #
    # def test_secret_expiry_links(self):
    #     pass
    #
    # def test_custom_secret_expiry_links(self):
    #     pass
    #
    # ############
    # # Link stats
    # ############
    #
    # def test_link_hit(self):
    #     pass
    #
    # def test_link_stats(self):
    #     pass
    #
    # def test_secret_link_stats(self):
    #     pass
    #
    # def test_expired_link_stats(self):
    #     pass
    #
    # def test_custom_link_stats(self):
    #     pass
    #
    # # Test static resources
    #
    # def test_logo(self):
    #     pass
    #
    # def test_logo_svg(self):
    #     pass
    #
    # def test_favicon(self):
    #     pass
