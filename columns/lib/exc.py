from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound as SQLA_MultipleResultsFound
from jinja2.exceptions import TemplateNotFound
from formencode import Invalid
from columns.lib.authorization import AuthorizationException
from mongokit import MultipleResultsFound

class AtomException(Exception):
	pass

class EntryNotFound(AtomException):
	pass

class UnknownOperatorError(Exception):
	def __init__(self, value):
		self.value = "Operator %s is unknown" % value
	
	def __str__(self):
		return self.value
	

class UnacceptedFormat(Exception):
	def __init__(self, value):
		self.value = "%s is not an acceptable format for this resource" % value
	
	def __str__(self):
		return self.value
	

class InvalidForm(Exception):
	"InvalidForm is raised if a form schema raises an Invalid exception"
	def __init__(self, response, error_dict):
		self.value = response
		self.message = str(error_dict)
	

class NoParentException(Exception):
	pass

class FileExistsError(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return self.value
	

class InvalidFormatError(Exception):
	def __init__(self, value='Unknown'):
		self.value = value
	
	def __str__(self):
		return "%s is not an acceptable format"%self.value
	

class NoChangesMade(Exception):
	pass


