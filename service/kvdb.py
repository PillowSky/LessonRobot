try:
	from sae.kvdb import KVClient
except ImportError as e:
	class KVClient(object):
		cache = {}
		def get(self, key):
			return self.cache.get(key)
		def set(self, key, value):
			self.cache[key] = value
finally:
	kvdb = KVClient()
