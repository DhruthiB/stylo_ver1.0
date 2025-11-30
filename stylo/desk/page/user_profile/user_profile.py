from datetime import datetime

import stylo
from stylo.query_builder import Interval, Order
from stylo.query_builder.functions import Date, Sum, UnixTimestamp
from stylo.utils import getdate


@stylo.whitelist()
def get_energy_points_heatmap_data(user: str, date: str | None):
	try:
		date = getdate(date)
	except Exception:
		date = getdate()

	eps_log = stylo.qb.DocType("Energy Point Log")

	return dict(
		stylo.qb.from_(eps_log)
		.select(UnixTimestamp(Date(eps_log.creation)), Sum(eps_log.points))
		.where(eps_log.user == user)
		.where(eps_log["type"] != "Review")
		.where(Date(eps_log.creation) > Date(date) - Interval(years=1))
		.where(Date(eps_log.creation) < Date(date) + Interval(years=1))
		.groupby(Date(eps_log.creation))
		.orderby(Date(eps_log.creation), order=Order.asc)
		.run()
	)


@stylo.whitelist()
def get_energy_points_percentage_chart_data(user: str, field: str):
	if field not in ("type", "reference_doctype", "rule"):
		stylo.throw(stylo._("Invalid field for grouping"))

	result = stylo.get_all(
		"Energy Point Log",
		filters={"user": user, "type": ["!=", "Review"]},
		group_by=field,
		order_by=field,
		fields=[field, "ABS(sum(points)) as points"],
		as_list=True,
	)

	return {
		"labels": [r[0] for r in result if r[0] is not None],
		"datasets": [{"values": [r[1] for r in result]}],
	}


@stylo.whitelist()
def get_user_rank(user: str):
	month_start = datetime.today().replace(day=1)
	monthly_rank = stylo.get_all(
		"Energy Point Log",
		group_by="`tabEnergy Point Log`.`user`",
		filters={"creation": [">", month_start], "type": ["!=", "Review"]},
		fields=["user", "sum(points)"],
		order_by="sum(points) desc",
		as_list=True,
	)

	all_time_rank = stylo.get_all(
		"Energy Point Log",
		group_by="`tabEnergy Point Log`.`user`",
		filters={"type": ["!=", "Review"]},
		fields=["user", "sum(points)"],
		order_by="sum(points) desc",
		as_list=True,
	)

	return {
		"monthly_rank": [i + 1 for i, r in enumerate(monthly_rank) if r[0] == user],
		"all_time_rank": [i + 1 for i, r in enumerate(all_time_rank) if r[0] == user],
	}


@stylo.whitelist()
def update_profile_info(profile_info):
	profile_info = stylo.parse_json(profile_info)
	keys = ("location", "interest", "user_image", "bio")

	for key in list(profile_info.keys()):
		if key not in keys:
			del profile_info[key]

	user = stylo.get_doc("User", stylo.session.user)
	user.update(profile_info)
	user.save()
	return user


@stylo.whitelist()
def get_energy_points_list(start: int, limit: int, user: str):
	return stylo.db.get_list(
		"Energy Point Log",
		filters={"user": user, "type": ["!=", "Review"]},
		fields=[
			"name",
			"user",
			"points",
			"reference_doctype",
			"reference_name",
			"reason",
			"type",
			"seen",
			"rule",
			"owner",
			"creation",
			"revert_of",
		],
		start=start,
		limit=limit,
		order_by="creation desc",
	)
