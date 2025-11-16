import stylo
from stylo.utils import update_progress_bar


def execute():
	stylo.db.auto_commit_on_many_writes = True

	Sessions = stylo.qb.DocType("Sessions")

	current_sessions = (stylo.qb.from_(Sessions).select(Sessions.sid, Sessions.sessiondata)).run(
		as_dict=True
	)

	for i, session in enumerate(current_sessions):
		try:
			new_data = stylo.as_json(stylo.safe_eval(session.sessiondata))
		except Exception:
			# Rerunning patch or already converted.
			continue

		(
			stylo.qb.update(Sessions).where(Sessions.sid == session.sid).set(Sessions.sessiondata, new_data)
		).run()
		update_progress_bar("Patching sessions", i, len(current_sessions))
