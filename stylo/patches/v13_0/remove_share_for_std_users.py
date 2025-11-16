import stylo
import stylo.share


def execute():
	for user in stylo.STANDARD_USERS:
		stylo.share.remove("User", user, user)
