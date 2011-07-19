"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url, app_globals
from routes.util import URLGenerator
from webtest import TestApp, TestRequest
from columns.lib import json
import urllib, cgi
from StringIO import StringIO
import pylons.test

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']]),

environ = {}

class PatchedTestApp(TestApp):
	def _gen_request(self, method, url, params='', headers=None, extra_environ=None,
					 status=None, upload_files=None, expect_errors=False,
					 content_type=None, body=None):
		"""
		Do a generic request.  
		"""
		environ = self._make_environ(extra_environ)
		# @@: Should this be all non-strings?
		if isinstance(params, (list, tuple, dict)):
			params = urllib.urlencode(params)
		if hasattr(params, 'items'):
			params = urllib.urlencode(params.items())
		if upload_files:
			params = cgi.parse_qsl(params, keep_blank_values=True)
			content_type, params = self.encode_multipart(
				params, upload_files)
			environ['CONTENT_TYPE'] = content_type
		elif params:
			environ.setdefault('CONTENT_TYPE', 'application/x-www-form-urlencoded')
		if '?' in url:
			url, environ['QUERY_STRING'] = url.split('?', 1)
		else:
			environ['QUERY_STRING'] = ''
		if content_type is not None:
			environ['CONTENT_TYPE'] = content_type
		environ['CONTENT_LENGTH'] = str(len(params))
		environ['REQUEST_METHOD'] = method
		environ['wsgi.input'] = StringIO(params)
		req = TestRequest.blank(url, environ)
		if headers:
			req.headers.update(headers)
		if body:
			req.body = body
		return self.do_request(req, status=status,
							   expect_errors=expect_errors)
	
	def post(self, url, params='', headers=None, extra_environ=None,
			 status=None, upload_files=None, expect_errors=False,
			 content_type=None, body=None):
		"""
		Do a POST request.	Very like the ``.get()`` method.
		``params`` are put in the body of the request.
		
		``upload_files`` is for file uploads.  It should be a list of
		``[(fieldname, filename, file_content)]``.	You can also use
		just ``[(fieldname, filename)]`` and the file content will be
		read from disk.
		
		Returns a ``webob.Response`` object.
		"""
		return self._gen_request('POST', url, params=params, headers=headers,
								 extra_environ=extra_environ,status=status,
								 upload_files=upload_files,
								 expect_errors=expect_errors, 
								 content_type=content_type,body=body
		)
	
	def put(self, url, params='', headers=None, extra_environ=None,
			status=None, upload_files=None, expect_errors=False,
			content_type=None, body=None):
		"""
		Do a PUT request.  Very like the ``.get()`` method.
		``params`` are put in the body of the request.
		
		``upload_files`` is for file uploads.  It should be a list of
		``[(fieldname, filename, file_content)]``.	You can also use
		just ``[(fieldname, filename)]`` and the file content will be
		read from disk.
		
		Returns a ``webob.Response`` object.
		"""
		return self._gen_request('PUT', url, params=params, headers=headers,
								 extra_environ=extra_environ,status=status,
								 upload_files=upload_files,
								 expect_errors=expect_errors,
								 content_type=content_type,body=body
		)
	

class TestController(TestCase):
	extra_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'open_id',
		'oid':u'http://tester.example.com'
	},'columns.authorize.disabled':True}
	def __init__(self, *args, **kwargs):
		wsgiapp = pylons.test.pylonsapp
		config = wsgiapp.config
		self.app = PatchedTestApp(wsgiapp)
		app_globals._push_object(config['pylons.app_globals'])
		url._push_object(URLGenerator(config['routes.map'], environ))
		TestCase.__init__(self, *args, **kwargs)
	
