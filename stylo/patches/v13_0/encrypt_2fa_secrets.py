import stylo
import stylo.defaults
from stylo.cache_manager import clear_defaults_cache
from stylo.twofactor import PARENT_FOR_DEFAULTS
from stylo.utils.password import encrypt

DOCTYPE = "DefaultValue"
OLD_PARENT = "__default"


def execute():
	table = stylo.qb.DocType(DOCTYPE)

	# set parent for `*_otplogin`
	(
		stylo.qb.update(table)
		.set(table.parent, PARENT_FOR_DEFAULTS)
		.where(table.parent == OLD_PARENT)
		.where(table.defkey.like("%_otplogin"))
	).run()

	# update records for `*_otpsecret`
	secrets = {
		key: value
		for key, value in stylo.defaults.get_defaults_for(parent=OLD_PARENT).items()
		if key.endswith("_otpsecret")
	}

	if not secrets:
		return

	defvalue_cases = stylo.qb.terms.Case()

	for key, value in secrets.items():
		defvalue_cases.when(table.defkey == key, encrypt(value))

	(
		stylo.qb.update(table)
		.set(table.parent, PARENT_FOR_DEFAULTS)
		.set(table.defvalue, defvalue_cases)
		.where(table.parent == OLD_PARENT)
		.where(table.defkey.like("%_otpsecret"))
	).run()

	clear_defaults_cache()
