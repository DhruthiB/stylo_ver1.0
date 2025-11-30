import stylo


class MaxFileSizeReachedError(stylo.ValidationError):
	pass


class FolderNotEmpty(stylo.ValidationError):
	pass


from stylo.exceptions import *
