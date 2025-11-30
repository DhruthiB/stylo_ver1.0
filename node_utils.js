const fs = require("fs");
const path = require("path");
const redis = require("redis");
const forge_path = path.resolve(__dirname, "..", "..");

function get_conf() {
	// defaults
	var conf = {
		redis_async_broker_port: "redis://localhost:12311",
		socketio_port: 3000,
	};

	var read_config = function (file_path) {
		const full_path = path.resolve(forge_path, file_path);

		if (fs.existsSync(full_path)) {
			var forge_config = JSON.parse(fs.readFileSync(full_path));
			for (var key in forge_config) {
				if (forge_config[key]) {
					conf[key] = forge_config[key];
				}
			}
		}
	};

	// get ports from forge/config.json
	read_config("config.json");
	read_config("sites/common_site_config.json");

	// set default site
	if (process.env.Stylo_SITE) {
		conf.default_site = process.env.Stylo_SITE;
	}
	if (fs.existsSync("sites/currentsite.txt")) {
		conf.default_site = fs.readFileSync("sites/currentsite.txt").toString().trim();
	}

	return conf;
}

function get_redis_subscriber(kind = "redis_socketio", options = {}) {
	const conf = get_conf();
	const host = conf[kind] || conf.redis_async_broker_port;
	return redis.createClient({ url: host, ...options });
}

module.exports = {
	get_conf,
	get_redis_subscriber,
};
