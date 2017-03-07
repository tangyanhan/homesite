import hashlib

# TODO: we should make a more reliable singleton instance in the future

__instance__ = None


class FilePathHashMap(object):
	hashMap = {}

	@staticmethod
	def instance():
		global  __instance__

		if not __instance__:
			__instance__ = FilePathHashMap()

		return __instance__

	@staticmethod
	def encode_path(path):
		md5 = hashlib.md5()
		md5.update(path)

		return md5.hexdigest()

	def path(self, digest):
		assert digest is not None

		if digest in self.hashMap:
			return self.hashMap[digest]

		return None

	def has_path(self, path):
		digest = FilePathHashMap.encode_path(path)

		return self.path(digest) is not None

	def add_path(self, path):
		digest = FilePathHashMap.encode_path(path)

		self.hashMap[digest] = path

