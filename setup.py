import os
import platform
import sys

try:
	from setuptools import setup, find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README')).read()
except IOError:
    README = ''

dependency_links = [
	"http://oauth-python-twitter2.googlecode.com/svn/trunk/oauthtwitter.py#egg=oauthtwitter-0.2",
	"https://github.com/mitsuhiko/jinja2/zipball/master#egg=Jinja2-2.6dev",
]
install_requires=[
	"Pylons==1.0",
	"SQLAlchemy>=0.6,<0.7",
	"BeautifulSoup",
	"pytz",
	"python-memcached",
	"oauth",
	"python-openid",
	"postmarkup",
	"lxml",
	"simplejson>=2.1",
	"oauthtwitter",
	"Jinja2>=2.6dev",
	#"PIL",#==1.1.7",
]

tests_require = install_requires + ['WebTest']

setup(
	name='columns',
	version='1.0',
	description='This is a pylons based publishing platform.  It\'s simple and kicks ass',
	long_description=README,
	author='Joshua Forman',
	author_email='josh@yoshrote.com',
	url='http://www.nerdblerp.com',
	license="BSD",
	classifiers=[
		"Intended Audience :: Developers",
		"Programming Language :: Python",
		"Framework :: Pylons",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Internet :: WWW/HTTP :: WSGI",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Internet :: WWW/HTTP :: Site Management",
		"Operating System :: OS Independent",
		"Natural Language :: English",
		"License :: OSI Approved :: BSD License",
	],
	keywords='wsgi web pylons publishing',
	dependency_links=dependency_links,
	install_requires=install_requires,
	setup_requires=["PasteScript>=1.6.3"],
	packages=find_packages(exclude=['ez_setup']),
	include_package_data=True,
	tests_require = tests_require,
	test_suite='nose.collector',
	package_data={'columns': ['i18n/*/LC_MESSAGES/*.mo']},
	#message_extractors={'columns': [
	#		('**.py', 'python', None),
	#		('templates/**.jinja', 'jinja2', {'input_encoding': 'utf-8'}),
	#		('public/**', 'ignore', None)]},
	zip_safe=False,
	paster_plugins=['PasteScript', 'Pylons'],
	entry_points="""
	[paste.app_factory]
	main = columns.config.middleware:make_app
	
	[paste.app_install]
	main = pylons.util:PylonsInstaller
	""",
)
