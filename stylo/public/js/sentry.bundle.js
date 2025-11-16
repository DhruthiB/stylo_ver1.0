import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: stylo.boot.sentry_dsn,
	release: stylo?.boot?.versions?.stylo,
	autoSessionTracking: false,
	initialScope: {
		// don't use stylo.session.user, it's set much later and will fail because of async loading
		user: { id: stylo.boot.sitename },
		tags: { stylo_user: stylo.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by stylo.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("stylo.throw")
		) {
			return null;
		}
		return event;
	},
});
