"""Yes this is dumb, but I'm going to do it anyway."""

import unittest
from columns.lib.exc import *

class TestExceptions(unittest.TestCase):
	def test_UnknownOperatorError(self):
		ex = UnknownOperatorError('#')
		str(ex)
	
	def test_UnacceptedFormat(self):
		ex = UnacceptedFormat('#')
		str(ex)
	
	def test_InvalidForm(self):
		ex = InvalidForm(None,{})
		str(ex)
	
	def test_FileExistsError(self):
		ex = FileExistsError('blah')
		str(ex)
	
	def test_InvalidFormatError(self):
		ex = InvalidFormatError('blah')
		str(ex)
	
	def test_AuthorizationException(self):
		ex = AuthorizationException()
		str(ex)
	
