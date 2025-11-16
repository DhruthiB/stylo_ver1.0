import stylo


def execute():
	Event = stylo.qb.DocType("Event")
	query = (
		stylo.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
