import datetime, pytz
from pytz import reference

__all__ = ['UTFDateTime','now','as_string','from_string','LocalizedDateTime']

UTC = reference.UTC
LOCAL = reference.Local

RFC3339_w_Timezone = '%Y-%m-%dT%H:%M:%S%z'
RFC3339_wo_Timezone = '%Y-%m-%dT%H:%M:%SZ'

def UTFDateTime(dt):
	if dt.tzinfo:
		return dt.astimezone(UTC)	
	else:
		return UTC.localize(dt)

def now():
	return UTC.localize(datetime.datetime.utcnow())

def as_string(date):
	if date is None:
		return None
	elif date.tzinfo:
		return date.strftime(RFC3339_w_Timezone)
	else:
		return date.strftime(RFC3339_wo_Timezone)

def from_string(dtstring):
	dt = datetime.datetime.strptime(dtstring,RFC3339_wo_Timezone)
	return UTC.localize(dt)

def localized(dt, timezone=None):
	localization = pytz.timezone(timezone) if timezone is not None else LOCAL
	if not dt.tzinfo:
		dt = UTC.localize(dt)
	return dt.astimezone(localization)
