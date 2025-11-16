# Copyright (c) 2018, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
