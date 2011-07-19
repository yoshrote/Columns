class Message(object):
	def __init__(self,v):
		self.text = v
	
	def __repr__(self):
		return self.text
	
	def __str__(self):
		return self.text
	
	def __unicode__(self):
		return unicode(self.text)


class AdvFlash(object):
	
	def __init__(self, session_key='flash',message_type='info'):
		self.key = session_key
		self.type = message_type
	
	def __call__(self, message, message_type=None):
		from pylons import session
		message = Message(message)
		message.type = message_type or self.type
		session.setdefault(self.key, []).append(message)
		session.save()
	
	def __getattr__(self,k):
		def call(v):
			self(v,k)
		
		return call
	
	def pop_messages(self):
		from pylons import session
		messages = session.pop( self.key, [] )
		session.save()
		return messages
	

