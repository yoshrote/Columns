from formencode import validators, NoDefault, Invalid, Schema, NestedVariables, ForEach, All, Any
from columns.lib import rfc3339

__all__ = [
	'Invalid',
	'CreateArticle', 'UpdateArticle', 
	'CreatePage', 'UpdatePage', 
	'CreateUser', 'UpdateUser', 
	'CreateAccount', 'UpdateAccount', 
	'CreateComment', 'UpdateComment',
	'CreateUpload', 'UpdateUpload',
	'CreateTag',
]

class DateTimeValidator(validators.FancyValidator):
	format = ""
	tzinfo = None
	messages = {'bad_format': 'Date/Time stamp must be in the format %(format)s',}
	
	def to_python(self, value, state):
		import datetime
		import pytz
		UTC = pytz.timezone('UTC')
		EST = pytz.timezone('US/Eastern')
		try:
			if isinstance(value, basestring):
				value = datetime.datetime.strptime(value,self.format)
			dt = EST.localize(value).astimezone(UTC).replace(tzinfo=None)
		except ValueError:
			raise Invalid(self.message("bad_format", state, format=self.format), value, state)
		return dt
	
	def from_python(self, value, state):
		return value.strftime(self.format)
	

class UniqueUserName(validators.FancyValidator):
	messages = {'user_name_taken': 'The name %(name)s is unavailable',}
	def to_python(self, value, state):
		from columns.model import User, meta
		if meta.Session.query(User).filter(User.name == value).count() > 0:
			raise validators.Invalid(self.message("user_name_taken",state,name=value),value,state)
		return value

class StringListValidator(validators.FancyValidator):
	messages = {'bad_string': 'Value %(value)s is not a valid string',}
	
	def to_python(self, value, state):
		try:
			return [unicode(x.strip()) for x in value.split(",") if x.strip() != ""]
		except (TypeError, ValueError, AttributeError):
			raise Invalid(self.message("bad_string", state, value=str(value)), value, state)
	
	def from_python(self, value, state):
		return unicode(", ".join(value))
	

class HTMLValidator(validators.UnicodeString):
	def to_python(self, value, state):
		try:
			from lxml import etree
			soup = etree.fromstring("<div>%s</div>"%value)
			return etree.tostring(soup, encoding=unicode)[5:-6]
		except:
			from BeautifulSoup import BeautifulSoup
			soup = BeautifulSoup(value)
			return unicode(soup)
	


class CreateArticle(Schema):
	allow_extra_fields = True
	
	title = validators.UnicodeString(max=255, strip=True, not_empty=True)
	page_id = validators.Int(if_empty=None)
	can_comment = validators.StringBool(if_missing=False)
	sticky = validators.StringBool(if_missing=False)
	published = DateTimeValidator(format=rfc3339.RFC3339_wo_Timezone, if_empty=None)
	content = HTMLValidator()
	tags = StringListValidator()

class UpdateArticle(CreateArticle):
	allow_extra_fields = True
	filter_extra_fields = True


class CreatePage(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	title = validators.UnicodeString(max=255, strip=True, not_empty=True)
	can_post = validators.StringBool(if_missing=False)
	content = HTMLValidator(if_empty=u'')
	template = validators.UnicodeString(if_empty=u'/blog/blank')
	visible = validators.StringBool(if_missing=False)
	in_main = validators.StringBool(if_missing=False)
	in_menu = validators.StringBool(if_missing=False)
	stream_comment_style = validators.UnicodeString(max=20, strip=True)
	story_comment_style = validators.UnicodeString(max=20, strip=True)

class UpdatePage(CreatePage):
	allow_extra_fields = True
	filter_extra_fields = True


class CreateUser(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	name = validators.UnicodeString(max=255, strip=True, not_empty=True)
	open_id = validators.UnicodeString(max=255, if_empty=None, strip=True)
	fb_id = validators.UnicodeString(max=255, if_empty=None, strip=True)
	twitter_id = validators.UnicodeString(max=255, if_empty=None, strip=True)
	profile = validators.URL(add_http=True, max=255, strip=True, if_empty=None)
	type = validators.Int()

class UpdateUser(CreateUser):
	allow_extra_fields = True
	filter_extra_fields = True


class CreateAccount(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	name = validators.UnicodeString(max=255, strip=True, not_empty=True)
	profile = validators.URL(add_http=True, max=255, strip=True, if_empty=None)

class UpdateAccount(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	profile = validators.URL(add_http=True, max=255, strip=True, if_empty=None)


class CreateTag(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	label = validators.UnicodeString(max=255, strip=True)

class UpdateTag(CreateTag):
	allow_extra_fields = True
	filter_extra_fields = True


class CreateComment(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	parent = validators.Int(if_missing=None, if_empty=None)
	title = validators.UnicodeString(max=255, if_empty='No Subject', strip=True)
	content = validators.UnicodeString()

class UpdateComment(CreateComment):
	allow_extra_fields = True
	filter_extra_fields = True


class CreateUpload(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	upload = validators.FieldStorageUploadConverter()
	title = validators.UnicodeString(max=255, strip=True)
	content = validators.UnicodeString(if_empty=None, if_missing=u'', strip=True)
	tags = StringListValidator(if_missing=[])

class UpdateUpload(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	title = validators.UnicodeString(max=255, strip=True)
	content = validators.UnicodeString(if_empty=None, if_missing=u'', strip=True)
	tags = StringListValidator(if_missing=[])


class CreateSetting(Schema):
	pre_validators = [NestedVariables()]
	allow_extra_fields = True
	filter_extra_fields = True
	
	module = validators.UnicodeString(max=255, strip=True)
	values = NestedVariables()

class UpdateSetting(CreateSetting):
	pre_validators = [NestedVariables()]
	allow_extra_fields = True
	filter_extra_fields = True
	
	values = NestedVariables()


class LoginForm(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	auth_type = validators.UnicodeString(max=255)
	auth_id = validators.UnicodeString(max=255, if_empty=None, if_missing=None)

class UpdateProfile(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	profile = validators.URL(add_http=True, max=255, strip=True, if_empty=None)

class SaveQuickUser(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	name = All(validators.UnicodeString(max=255,min=3,strip=True),UniqueUserName())
	profile = validators.URL(add_http=True, max=255, strip=True, if_empty=None)

class Delete(Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	obj_type = validators.UnicodeString(max=255)
	id = validators.Int(max=255)


