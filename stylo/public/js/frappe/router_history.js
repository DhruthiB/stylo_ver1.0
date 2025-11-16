stylo.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = stylo.utils.debounce(() => {
	if (stylo.session.user === "Guest") return;
	const routes = stylo.route_history_queue;
	if (!routes.length) return;

	stylo.route_history_queue = [];

	stylo
		.xcall("stylo.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			stylo.route_history_queue.concat(routes);
		});
}, 10000);

stylo.router.on("change", () => {
	const route = stylo.get_route();
	if (is_route_useful(route)) {
		stylo.route_history_queue.push({
			creation: stylo.datetime.now_datetime(),
			route: stylo.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
