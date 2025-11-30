# Copyright (c) 2017, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo


@stylo.whitelist()
def get_leaderboard_config():
	leaderboard_config = stylo._dict()
	leaderboard_hooks = stylo.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(stylo.get_attr(hook)())

	return leaderboard_config
