"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
# Import helpers as desired, or define your own, ie:
# from webhelpers.html.tags import checkbox, password
from webhelpers.html.builder import literal
from columns.lib import rfc3339
from columns.lib.advflash import AdvFlash as _Flash
#from PIL import Image
from uuid import uuid4

flash = _Flash()

def user_from_session(session):
	person = {
		'id': session.get('user_id'),
		'name': session.get('user_name'),
		'uri': session.get('user_profile'),
		'email': None,
	}
	return person

def get_permissions():
	from columns.config import authorization
	return authorization.PERMISSIONS

def page_list():
	from columns.model import Page, meta
	return [(row.id,row.title) for row in meta.Session.query(Page.id,Page.title).filter(Page.can_post == True).filter(Page.slug != 'main').all()]

def menu_pages():
	from columns.model import Page, meta
	return [(row.slug,row.title) for row in meta.Session.query(Page.slug,Page.title).filter(Page.in_menu == True).all()]

def top_tags(limit=5):
	from columns.model import get_tag_frequencies
	tag_freq = get_tag_frequencies(limit=limit)
	return [(row.id,row.label) for row,freq in tag_freq]

def template_list():
	return [(u'/blog/blank',u'Blank'),(u'/blog/stream',u'Stream')]

def resource_counter(resource):
	from columns.model import RESOURCE_MAP, meta
	return meta.Session.query(RESOURCE_MAP[resource]).count()
'''
def rescale(src_img,max_side):
	img = Image.open(src_img)
	wid,hgt = img.size
	img = img.crop((x0,y0,min(x,wid),min(y1,hgt)))
	wid,hgt = img.size
	ratio = float(wid)/hgt
	if wid > max_side or hgt > max_side:
		#scale down
		if wid == hgt:
			img = img.resize((max_side,max_side))
		elif wid > hgt:
			img = img.resize((max_side,max_side*hgt//wid))
		else: #hgt > wid
			img = img.resize((max_side*wid//hgt,max_side))
	return img

'''