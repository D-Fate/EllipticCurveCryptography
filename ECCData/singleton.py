def singleton(cls):
	class InnerClass(cls):
		_instance = None

		def __new__(cls, *args, **kwargs):
			if InnerClass._instance is None:
					InnerClass._instance = super(InnerClass, cls).__new__(cls, *args, **kwargs)
					InnerClass._instance._initialized = False
			return InnerClass._instance

		def __init__(self, *args, **kwargs):
			if self._initialized:
				return
			super(InnerClass, self).__init__(*args, **kwargs)
			self._initialized = True

	InnerClass.__name__ = cls.__name__
	return InnerClass
