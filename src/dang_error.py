class DangError(Exception):
	def __init__(self, *args):
		self.args = [a for a in args]