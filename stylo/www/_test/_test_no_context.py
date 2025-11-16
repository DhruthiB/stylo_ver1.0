import stylo


# no context object is accepted
def get_context():
	context = stylo._dict()
	context.body = "Custom Content"
	return context
