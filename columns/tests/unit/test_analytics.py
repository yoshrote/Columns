import unittest
from columns.lib.analytics.middleware import AnalyticsMiddleware

class TestAnalyticsnMiddleware(unittest.TestCase):
	def setUp(self):
		def simple_app(environ, start_response):
			"""Simplest possible application object"""
			status = '200 OK'
			response_headers = [('Content-type', 'text/plain')]
			start_response(status, response_headers)
			return ['Hello world!\n']
		
		def start_response(status, response_headers, exc_info=None):
			pass
		
		self.app = simple_app
		self.start_response = start_response
	
	def test_disabled_middleware(self):
		app = AnalyticsMiddleware(self.app, {'analytics.url':'sqlite://'}, disabled=True)
		self.assertEquals(app({'wsgiorg.routing_args':(None,{})},self.start_response),['Hello world!\n'])
	
	def test_middleware(self):
		app = AnalyticsMiddleware(self.app, {'analytics.url':'sqlite://'})
		self.assertEquals(app({'REQUEST_METHOD':'GET','PATH_INFO':'/','wsgiorg.routing_args':(None,{'controller':'blog','action':'test'})},self.start_response),['Hello world!\n'])
	

