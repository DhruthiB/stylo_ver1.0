import stylo


class MaxFileSizeReachedError(stylo.ValidationError):
	pass


class FolderNotEmpty(stylo.ValidationError):
	pass


class FileTypeNotAllowed(stylo.ValidationError):
	pass


from stylo.exceptions import *
