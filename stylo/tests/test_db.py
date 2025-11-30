# Copyright (c) 2022, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import inspect
from math import ceil
from random import choice
from unittest.mock import patch

import stylo
from stylo.core.utils import find
from stylo.custom.doctype.custom_field.custom_field import create_custom_field
from stylo.database import savepoint
from stylo.database.database import get_query_execution_timeout
from stylo.database.utils import FallBackDateTimeStr
from stylo.query_builder import Field
from stylo.query_builder.functions import Concat_ws
from stylo.tests.test_query_builder import db_type_is, run_only_if
from stylo.tests.utils import StyloTestCase, timeout
from stylo.utils import add_days, cint, now, random_string, set_request
from stylo.utils.testutils import clear_custom_fields


class TestDB(StyloTestCase):
	def test_datetime_format(self):
		now_str = now()
		self.assertEqual(stylo.db.format_datetime(None), FallBackDateTimeStr)
		self.assertEqual(stylo.db.format_datetime(now_str), now_str)

	@run_only_if(db_type_is.MARIADB)
	def test_get_column_type(self):
		desc_data = stylo.db.sql("desc `tabUser`", as_dict=1)
		user_name_type = find(desc_data, lambda x: x["Field"] == "name")["Type"]
		self.assertEqual(stylo.db.get_column_type("User", "name"), user_name_type)

	def test_get_database_size(self):
		self.assertIsInstance(stylo.db.get_database_size(), (float, int))

	def test_db_statement_execution_timeout(self):
		stylo.db.set_execution_timeout(2)
		# Setting 0 means no timeout.
		self.addCleanup(stylo.db.set_execution_timeout, 0)

		try:
			savepoint = "statement_timeout"
			stylo.db.savepoint(savepoint)
			stylo.db.multisql(
				{
					"mariadb": "select sleep(10)",
					"postgres": "select pg_sleep(10)",
				}
			)
		except Exception as e:
			self.assertTrue(stylo.db.is_statement_timeout(e), f"exepcted {e} to be timeout error")
			stylo.db.rollback(save_point=savepoint)
		else:
			stylo.db.rollback(save_point=savepoint)
			self.fail("Long running queries not timing out")

	@patch.dict(stylo.conf, {"http_timeout": 20, "enable_db_statement_timeout": 1})
	def test_db_timeout_computation(self):
		set_request(method="GET", path="/")
		self.assertEqual(get_query_execution_timeout(), 30)
		stylo.local.request = None
		self.assertEqual(get_query_execution_timeout(), 0)

	def test_get_value(self):
		self.assertEqual(stylo.db.get_value("User", {"name": ["=", "Administrator"]}), "Administrator")
		self.assertEqual(stylo.db.get_value("User", {"name": ["like", "Admin%"]}), "Administrator")
		self.assertNotEqual(stylo.db.get_value("User", {"name": ["!=", "Guest"]}), "Guest")
		self.assertEqual(stylo.db.get_value("User", {"name": ["<", "Adn"]}), "Administrator")
		self.assertEqual(stylo.db.get_value("User", {"name": ["<=", "Administrator"]}), "Administrator")
		self.assertEqual(
			stylo.db.get_value("User", {}, ["Max(name)"], order_by=None),
			stylo.db.sql("SELECT Max(name) FROM tabUser")[0][0],
		)
		self.assertEqual(
			stylo.db.get_value("User", {}, "Min(name)", order_by=None),
			stylo.db.sql("SELECT Min(name) FROM tabUser")[0][0],
		)
		self.assertIn(
			"for update",
			stylo.db.get_value("User", Field("name") == "Administrator", for_update=True, run=False).lower(),
		)
		user_doctype = stylo.qb.DocType("User")
		self.assertEqual(
			stylo.qb.from_(user_doctype).select(user_doctype.name, user_doctype.email).run(),
			stylo.db.get_values(
				user_doctype,
				filters={},
				fieldname=[user_doctype.name, user_doctype.email],
				order_by=None,
			),
		)
		self.assertEqual(
			stylo.db.sql("""SELECT name FROM `tabUser` WHERE name > 's' ORDER BY MODIFIED DESC""")[0][0],
			stylo.db.get_value("User", {"name": [">", "s"]}),
		)

		self.assertEqual(
			stylo.db.sql("""SELECT name FROM `tabUser` WHERE name >= 't' ORDER BY MODIFIED DESC""")[0][0],
			stylo.db.get_value("User", {"name": [">=", "t"]}),
		)
		self.assertEqual(
			stylo.db.get_values(
				"User",
				filters={"name": "Administrator"},
				distinct=True,
				fieldname="email",
			),
			stylo.qb.from_(user_doctype)
			.where(user_doctype.name == "Administrator")
			.select("email")
			.distinct()
			.run(),
		)

		self.assertIn(
			"concat_ws",
			stylo.db.get_value(
				"User",
				filters={"name": "Administrator"},
				fieldname=Concat_ws(" ", "LastName"),
				run=False,
			).lower(),
		)
		self.assertEqual(
			stylo.db.sql("select email from tabUser where name='Administrator' order by modified DESC"),
			stylo.db.get_values("User", filters=[["name", "=", "Administrator"]], fieldname="email"),
		)

		# test multiple orderby's
		delimiter = '"' if stylo.db.db_type == "postgres" else "`"
		self.assertIn(
			"ORDER BY {deli}creation{deli} DESC,{deli}modified{deli} ASC,{deli}name{deli} DESC".format(
				deli=delimiter
			),
			stylo.db.get_value("DocType", "DocField", order_by="creation desc, modified asc, name", run=0),
		)

	def test_escape(self):
		stylo.db.escape("香港濟生堂製藥有限公司 - IT".encode())

	def test_get_single_value(self):
		# setup
		values_dict = {
			"Float": 1.5,
			"Int": 1,
			"Percent": 55.5,
			"Currency": 12.5,
			"Data": "Test",
			"Date": datetime.datetime.now().date(),
			"Datetime": datetime.datetime.now(),
			"Time": datetime.timedelta(hours=9, minutes=45, seconds=10),
		}
		test_inputs = [{"fieldtype": fieldtype, "value": value} for fieldtype, value in values_dict.items()]
		for fieldtype in values_dict:
			create_custom_field(
				"Print Settings",
				{
					"fieldname": f"test_{fieldtype.lower()}",
					"label": f"Test {fieldtype}",
					"fieldtype": fieldtype,
				},
			)

		# test
		for inp in test_inputs:
			fieldname = f"test_{inp['fieldtype'].lower()}"
			stylo.db.set_value("Print Settings", "Print Settings", fieldname, inp["value"])
			self.assertEqual(stylo.db.get_single_value("Print Settings", fieldname), inp["value"])

		# teardown
		clear_custom_fields("Print Settings")

	def test_get_single_value_destructuring(self):
		[[lang, date_format]] = stylo.db.get_values_from_single(
			["language", "date_format"], None, "System Settings"
		)
		self.assertEqual(lang, stylo.db.get_single_value("System Settings", "language"))
		self.assertEqual(date_format, stylo.db.get_single_value("System Settings", "date_format"))

	def test_log_touched_tables(self):
		stylo.flags.in_migrate = True
		stylo.flags.touched_tables = set()
		stylo.db.set_value("System Settings", "System Settings", "backup_limit", 5)
		self.assertIn("tabSingles", stylo.flags.touched_tables)

		stylo.flags.touched_tables = set()
		todo = stylo.get_doc({"doctype": "ToDo", "description": "Random Description"})
		todo.save()
		self.assertIn("tabToDo", stylo.flags.touched_tables)

		stylo.flags.touched_tables = set()
		todo.description = "Another Description"
		todo.save()
		self.assertIn("tabToDo", stylo.flags.touched_tables)

		if stylo.db.db_type != "postgres":
			stylo.flags.touched_tables = set()
			stylo.db.sql("UPDATE tabToDo SET description = 'Updated Description'")
			self.assertNotIn("tabToDo SET", stylo.flags.touched_tables)
			self.assertIn("tabToDo", stylo.flags.touched_tables)

		stylo.flags.touched_tables = set()
		todo.delete()
		self.assertIn("tabToDo", stylo.flags.touched_tables)

		stylo.flags.touched_tables = set()
		cf = create_custom_field("ToDo", {"label": "ToDo Custom Field"})
		self.assertIn("tabToDo", stylo.flags.touched_tables)
		self.assertIn("tabCustom Field", stylo.flags.touched_tables)
		if cf:
			cf.delete()
		stylo.db.commit()
		stylo.flags.in_migrate = False
		stylo.flags.touched_tables.clear()

	def test_db_keywords_as_fields(self):
		"""Tests if DB keywords work as docfield names. If they're wrapped with grave accents."""
		# Using random.choices, picked out a list of 40 keywords for testing
		all_keywords = {
			"mariadb": [
				"CHARACTER",
				"DELAYED",
				"LINES",
				"EXISTS",
				"YEAR_MONTH",
				"LOCALTIME",
				"BOTH",
				"MEDIUMINT",
				"LEFT",
				"BINARY",
				"DEFAULT",
				"KILL",
				"WRITE",
				"SQL_SMALL_RESULT",
				"CURRENT_TIME",
				"CROSS",
				"INHERITS",
				"SELECT",
				"TABLE",
				"ALTER",
				"CURRENT_TIMESTAMP",
				"XOR",
				"CASE",
				"ALL",
				"WHERE",
				"INT",
				"TO",
				"SOME",
				"DAY_MINUTE",
				"ERRORS",
				"OPTIMIZE",
				"REPLACE",
				"HIGH_PRIORITY",
				"VARBINARY",
				"HELP",
				"IS",
				"CHAR",
				"DESCRIBE",
				"KEY",
			],
			"postgres": [
				"WORK",
				"LANCOMPILER",
				"REAL",
				"HAVING",
				"REPEATABLE",
				"DATA",
				"USING",
				"BIT",
				"DEALLOCATE",
				"SERIALIZABLE",
				"CURSOR",
				"INHERITS",
				"ARRAY",
				"TRUE",
				"IGNORE",
				"PARAMETER_MODE",
				"ROW",
				"CHECKPOINT",
				"SHOW",
				"BY",
				"SIZE",
				"SCALE",
				"UNENCRYPTED",
				"WITH",
				"AND",
				"CONVERT",
				"FIRST",
				"SCOPE",
				"WRITE",
				"INTERVAL",
				"CHARACTER_SET_SCHEMA",
				"ADD",
				"SCROLL",
				"NULL",
				"WHEN",
				"TRANSACTION_ACTIVE",
				"INT",
				"FORTRAN",
				"STABLE",
			],
		}
		created_docs = []

		# edit by rushabh: added [:1]
		# don't run every keyword! - if one works, they all do
		fields = all_keywords[stylo.conf.db_type][:1]
		test_doctype = "ToDo"

		def add_custom_field(field):
			create_custom_field(
				test_doctype,
				{
					"fieldname": field.lower(),
					"label": field.title(),
					"fieldtype": "Data",
				},
			)

		# Create custom fields for test_doctype
		for field in fields:
			add_custom_field(field)

		# Create documents under that doctype and query them via ORM
		for _ in range(10):
			docfields = {key.lower(): random_string(10) for key in fields}
			doc = stylo.get_doc({"doctype": test_doctype, "description": random_string(20), **docfields})
			doc.insert()
			created_docs.append(doc.name)

		random_field = choice(fields).lower()
		random_doc = choice(created_docs)
		random_value = random_string(20)

		# Testing read
		self.assertEqual(next(iter(stylo.get_all("ToDo", fields=[random_field], limit=1)[0])), random_field)
		self.assertEqual(
			next(iter(stylo.get_all("ToDo", fields=[f"`{random_field}` as total"], limit=1)[0])), "total"
		)

		# Testing read for distinct and sql functions
		self.assertEqual(
			next(
				iter(
					stylo.get_all(
						"ToDo",
						fields=[f"`{random_field}` as total"],
						distinct=True,
						limit=1,
					)[0]
				)
			),
			"total",
		)
		self.assertEqual(
			next(
				iter(
					stylo.get_all(
						"ToDo",
						fields=[f"`{random_field}`"],
						distinct=True,
						limit=1,
					)[0]
				)
			),
			random_field,
		)
		self.assertEqual(
			next(iter(stylo.get_all("ToDo", fields=[f"count(`{random_field}`)"], limit=1)[0])),
			"count" if stylo.conf.db_type == "postgres" else f"count(`{random_field}`)",
		)

		# Testing update
		stylo.db.set_value(test_doctype, random_doc, random_field, random_value)
		self.assertEqual(stylo.db.get_value(test_doctype, random_doc, random_field), random_value)

		# Cleanup - delete records and remove custom fields
		for doc in created_docs:
			stylo.delete_doc(test_doctype, doc)
		clear_custom_fields(test_doctype)

	def test_savepoints(self):
		stylo.db.rollback()
		save_point = "todonope"

		created_docs = []
		failed_docs = []

		for _ in range(5):
			stylo.db.savepoint(save_point)
			doc_gone = stylo.get_doc(doctype="ToDo", description="nope").save()
			failed_docs.append(doc_gone.name)
			stylo.db.rollback(save_point=save_point)
			doc_kept = stylo.get_doc(doctype="ToDo", description="nope").save()
			created_docs.append(doc_kept.name)
		stylo.db.commit()

		for d in failed_docs:
			self.assertFalse(stylo.db.exists("ToDo", d))
		for d in created_docs:
			self.assertTrue(stylo.db.exists("ToDo", d))

	def test_savepoints_wrapper(self):
		stylo.db.rollback()

		class SpecificExc(Exception):
			pass

		created_docs = []
		failed_docs = []

		for _ in range(5):
			with savepoint(catch=SpecificExc):
				doc_kept = stylo.get_doc(doctype="ToDo", description="nope").save()
				created_docs.append(doc_kept.name)

			with savepoint(catch=SpecificExc):
				doc_gone = stylo.get_doc(doctype="ToDo", description="nope").save()
				failed_docs.append(doc_gone.name)
				raise SpecificExc

		stylo.db.commit()

		for d in failed_docs:
			self.assertFalse(stylo.db.exists("ToDo", d))
		for d in created_docs:
			self.assertTrue(stylo.db.exists("ToDo", d))

	def test_transaction_writes_error(self):
		from stylo.database.database import Database

		stylo.db.rollback()

		stylo.db.MAX_WRITES_PER_TRANSACTION = 1
		note = stylo.get_last_doc("ToDo")
		note.description = "changed"
		with self.assertRaises(stylo.TooManyWritesError):
			note.save()

		stylo.db.MAX_WRITES_PER_TRANSACTION = Database.MAX_WRITES_PER_TRANSACTION

	def test_transaction_write_counting(self):
		note = stylo.get_doc(doctype="Note", title="transaction counting").insert()

		writes = stylo.db.transaction_writes
		stylo.db.set_value("Note", note.name, "content", "abc")
		self.assertEqual(1, stylo.db.transaction_writes - writes)
		writes = stylo.db.transaction_writes

		stylo.db.sql(
			"""
			update `tabNote`
			set content = 'abc'
			where name = %s
			""",
			note.name,
		)
		self.assertEqual(1, stylo.db.transaction_writes - writes)

	def test_pk_collision_ignoring(self):
		# note has `name` generated from title
		for _ in range(3):
			stylo.get_doc(doctype="Note", title="duplicate name").insert(ignore_if_duplicate=True)

		with savepoint():
			self.assertRaises(
				stylo.DuplicateEntryError, stylo.get_doc(doctype="Note", title="duplicate name").insert
			)
			# recover transaction to continue other tests
			raise Exception

	def test_read_only_errors(self):
		stylo.db.rollback()
		stylo.db.begin(read_only=True)
		self.addCleanup(stylo.db.rollback)

		with self.assertRaises(stylo.InReadOnlyMode):
			stylo.db.set_value("User", "Administrator", "full_name", "Haxor")

	def test_exists(self):
		dt, dn = "User", "Administrator"
		self.assertEqual(stylo.db.exists(dt, dn, cache=True), dn)
		self.assertEqual(stylo.db.exists(dt, dn), dn)
		self.assertEqual(stylo.db.exists(dt, {"name": ("=", dn)}), dn)

		filters = {"doctype": dt, "name": ("like", "Admin%")}
		self.assertEqual(stylo.db.exists(filters), dn)
		self.assertEqual(filters["doctype"], dt)  # make sure that doctype was not removed from filters

		self.assertEqual(stylo.db.exists(dt, [["name", "=", dn]]), dn)

	def test_estimated_count(self):
		self.assertGreater(stylo.db.estimate_count("DocField"), 100)

	def test_bulk_insert(self):
		current_count = stylo.db.count("ToDo")
		test_body = f"test_bulk_insert - {random_string(10)}"
		chunk_size = 10

		for number_of_values in (1, 2, 5, 27):
			current_transaction_writes = stylo.db.transaction_writes

			stylo.db.bulk_insert(
				"ToDo",
				["name", "description"],
				[[f"ToDo Test Bulk Insert {i}", test_body] for i in range(number_of_values)],
				ignore_duplicates=True,
				chunk_size=chunk_size,
			)

			# check that all records were inserted
			self.assertEqual(number_of_values, stylo.db.count("ToDo") - current_count)

			# check if inserts were done in chunks
			expected_number_of_writes = ceil(number_of_values / chunk_size)
			self.assertEqual(
				expected_number_of_writes, stylo.db.transaction_writes - current_transaction_writes
			)

		stylo.db.delete("ToDo", {"description": test_body})

	def test_count(self):
		stylo.db.delete("Note")

		stylo.get_doc(doctype="Note", title="note1", content="something").insert()
		stylo.get_doc(doctype="Note", title="note2", content="someting else").insert()

		# Count with no filtes
		self.assertEqual((stylo.db.count("Note")), 2)

		# simple filters
		self.assertEqual((stylo.db.count("Note", [["title", "=", "note1"]])), 1)

		stylo.get_doc(doctype="Note", title="note3", content="something other").insert()

		# List of list filters with tables
		self.assertEqual(
			(
				stylo.db.count(
					"Note",
					[["Note", "title", "like", "note%"], ["Note", "content", "like", "some%"]],
				)
			),
			3,
		)

		stylo.db.rollback()

	@run_only_if(db_type_is.POSTGRES)
	def test_modify_query(self):
		from stylo.database.postgres.database import modify_query

		query = "select * from `tabtree b` where lft > 13 and rgt <= 16 and name =1.0 and parent = 4134qrsdc and isgroup = 1.00045"
		self.assertEqual(
			"select * from \"tabtree b\" where lft > '13' and rgt <= '16' and name = '1' and parent = 4134qrsdc and isgroup = 1.00045",
			modify_query(query),
		)

		query = 'select locate(".io", "stylo.io"), locate("3", cast(3 as varchar)), locate("3", 3::varchar)'
		self.assertEqual(
			'select strpos( "stylo.io", ".io"), strpos( cast(3 as varchar), "3"), strpos( 3::varchar, "3")',
			modify_query(query),
		)

	@run_only_if(db_type_is.POSTGRES)
	def test_modify_values(self):
		from stylo.database.postgres.database import modify_values

		self.assertEqual(
			{"a": "23", "b": 23.0, "c": 23.0345, "d": "wow", "e": ("1", "2", "3", "abc")},
			modify_values({"a": 23, "b": 23.0, "c": 23.0345, "d": "wow", "e": [1, 2, 3, "abc"]}),
		)
		self.assertEqual(
			["23", 23.0, 23.00004345, "wow", ("1", "2", "3", "abc")],
			modify_values((23, 23.0, 23.00004345, "wow", [1, 2, 3, "abc"])),
		)


@run_only_if(db_type_is.MARIADB)
class TestDDLCommandsMaria(StyloTestCase):
	test_table_name = "TestNotes"

	def setUp(self) -> None:
		stylo.db.sql_ddl(
			f"""
			CREATE TABLE IF NOT EXISTS `tab{self.test_table_name}` (`id` INT NULL, content TEXT, PRIMARY KEY (`id`));
			"""
		)

	def tearDown(self) -> None:
		stylo.db.sql(f"DROP TABLE tab{self.test_table_name};")
		self.test_table_name = "TestNotes"

	def test_rename(self) -> None:
		new_table_name = f"{self.test_table_name}_new"
		stylo.db.rename_table(self.test_table_name, new_table_name)
		check_exists = stylo.db.sql(
			f"""
			SELECT * FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_NAME = N'tab{new_table_name}';
			"""
		)
		self.assertGreater(len(check_exists), 0)
		self.assertIn(f"tab{new_table_name}", check_exists[0])

		# * so this table is deleted after the rename
		self.test_table_name = new_table_name

	def test_describe(self) -> None:
		self.assertSequenceEqual(
			[
				("id", "int(11)", "NO", "PRI", None, ""),
				("content", "text", "YES", "", None, ""),
			],
			stylo.db.describe(self.test_table_name),
		)

	def test_change_type(self) -> None:
		def get_table_description():
			return stylo.db.sql(f"DESC `tab{self.test_table_name}`")

		# try changing from int to varchar
		stylo.db.change_column_type("TestNotes", "id", "varchar(255)")
		self.assertIn("varchar(255)", get_table_description()[0])

		# try changing from varchar to bigint
		stylo.db.change_column_type("TestNotes", "id", "bigint")
		self.assertIn("bigint(20)", get_table_description()[0])

	def test_add_index(self) -> None:
		index_name = "test_index"
		stylo.db.add_index(self.test_table_name, ["id", "content(50)"], index_name)
		indexs_in_table = stylo.db.sql(
			f"""
			SHOW INDEX FROM tab{self.test_table_name}
			WHERE Key_name = '{index_name}';
			"""
		)
		self.assertEqual(len(indexs_in_table), 2)


class TestDBSetValue(StyloTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.todo1 = stylo.get_doc(doctype="ToDo", description="test_set_value 1").insert()
		cls.todo2 = stylo.get_doc(doctype="ToDo", description="test_set_value 2").insert()

	def test_update_single_doctype_field(self):
		value = stylo.db.get_single_value("System Settings", "deny_multiple_sessions")
		changed_value = not value

		stylo.db.set_value("System Settings", "System Settings", "deny_multiple_sessions", changed_value)
		current_value = stylo.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

		changed_value = not current_value
		stylo.db.set_value("System Settings", None, "deny_multiple_sessions", changed_value)
		current_value = stylo.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

		changed_value = not current_value
		stylo.db.set_single_value("System Settings", "deny_multiple_sessions", changed_value)
		current_value = stylo.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

	def test_update_single_row_single_column(self):
		stylo.db.set_value("ToDo", self.todo1.name, "description", "test_set_value change 1")
		updated_value = stylo.db.get_value("ToDo", self.todo1.name, "description")
		self.assertEqual(updated_value, "test_set_value change 1")

	def test_update_single_row_multiple_columns(self):
		description, status = "Upated by test_update_single_row_multiple_columns", "Closed"

		stylo.db.set_value(
			"ToDo",
			self.todo1.name,
			{
				"description": description,
				"status": status,
			},
			update_modified=False,
		)

		updated_desciption, updated_status = stylo.db.get_value(
			"ToDo", filters={"name": self.todo1.name}, fieldname=["description", "status"]
		)

		self.assertEqual(description, updated_desciption)
		self.assertEqual(status, updated_status)

	def test_update_multiple_rows_single_column(self):
		stylo.db.set_value("ToDo", {"description": ("like", "%test_set_value%")}, "description", "change 2")

		self.assertEqual(stylo.db.get_value("ToDo", self.todo1.name, "description"), "change 2")
		self.assertEqual(stylo.db.get_value("ToDo", self.todo2.name, "description"), "change 2")

	def test_update_multiple_rows_multiple_columns(self):
		todos_to_update = stylo.get_all(
			"ToDo",
			filters={"description": ("like", "%test_set_value%"), "status": ("!=", "Closed")},
			pluck="name",
		)

		stylo.db.set_value(
			"ToDo",
			{"description": ("like", "%test_set_value%"), "status": ("!=", "Closed")},
			{"status": "Closed", "priority": "High"},
		)

		test_result = stylo.get_all(
			"ToDo", filters={"name": ("in", todos_to_update)}, fields=["status", "priority"]
		)

		self.assertTrue(all(x for x in test_result if x["status"] == "Closed"))
		self.assertTrue(all(x for x in test_result if x["priority"] == "High"))

	def test_update_modified_options(self):
		self.todo2.reload()

		todo = self.todo2
		updated_description = f"{todo.description} - by `test_update_modified_options`"
		custom_modified = datetime.datetime.fromisoformat(add_days(now(), 10))
		custom_modified_by = "user_that_doesnt_exist@example.com"

		stylo.db.set_value("ToDo", todo.name, "description", updated_description, update_modified=False)
		self.assertEqual(updated_description, stylo.db.get_value("ToDo", todo.name, "description"))
		self.assertEqual(todo.modified, stylo.db.get_value("ToDo", todo.name, "modified"))

		stylo.db.set_value(
			"ToDo",
			todo.name,
			"description",
			"test_set_value change 1",
			modified=custom_modified,
			modified_by=custom_modified_by,
		)
		self.assertTupleEqual(
			(custom_modified, custom_modified_by),
			stylo.db.get_value("ToDo", todo.name, ["modified", "modified_by"]),
		)

	def test_set_value(self):
		self.todo1.reload()

		stylo.db.set_value(
			self.todo1.doctype,
			self.todo1.name,
			"description",
			f"{self.todo1.description}-edit by `test_for_update`",
		)
		query = stylo.db.last_query

		if stylo.conf.db_type == "postgres":
			from stylo.database.postgres.database import modify_query

			self.assertTrue(modify_query("UPDATE `tabToDo` SET") in str(query))
		if stylo.conf.db_type == "mariadb":
			self.assertTrue("UPDATE `tabToDo` SET" in query)

	def test_cleared_cache(self):
		self.todo2.reload()
		stylo.get_cached_doc(self.todo2.doctype, self.todo2.name)  # init cache

		description = f"{self.todo2.description}-edit by `test_cleared_cache`"

		stylo.db.set_value(self.todo2.doctype, self.todo2.name, "description", description)
		cached_doc = stylo.get_cached_doc(self.todo2.doctype, self.todo2.name)
		self.assertEqual(cached_doc.description, description)

	@classmethod
	def tearDownClass(cls):
		stylo.db.rollback()


@run_only_if(db_type_is.POSTGRES)
class TestDDLCommandsPost(StyloTestCase):
	test_table_name = "TestNotes"

	def setUp(self) -> None:
		stylo.db.sql(
			f"""
			CREATE TABLE "tab{self.test_table_name}" ("id" INT NULL, content text, PRIMARY KEY ("id"))
			"""
		)

	def tearDown(self) -> None:
		stylo.db.sql(f'DROP TABLE "tab{self.test_table_name}"')
		self.test_table_name = "TestNotes"

	def test_rename(self) -> None:
		new_table_name = f"{self.test_table_name}_new"
		stylo.db.rename_table(self.test_table_name, new_table_name)
		check_exists = stylo.db.sql(
			f"""
			SELECT EXISTS (
			SELECT FROM information_schema.tables
			WHERE  table_name = 'tab{new_table_name}'
			);
			"""
		)
		self.assertTrue(check_exists[0][0])

		# * so this table is deleted after the rename
		self.test_table_name = new_table_name

	def test_describe(self) -> None:
		self.assertSequenceEqual([("id",), ("content",)], stylo.db.describe(self.test_table_name))

	def test_change_type(self) -> None:
		from psycopg2.errors import DatatypeMismatch

		def get_table_description():
			return stylo.db.sql(
				f"""
				SELECT
					table_name,
					column_name,
					data_type
				FROM
					information_schema.columns
				WHERE
					table_name = 'tab{self.test_table_name}'"""
			)

		# try changing from int to varchar
		stylo.db.change_column_type(self.test_table_name, "id", "varchar(255)")
		self.assertIn("character varying", get_table_description()[0])

		# try changing from varchar to int
		try:
			stylo.db.change_column_type(self.test_table_name, "id", "bigint")
		except DatatypeMismatch:
			stylo.db.rollback()

		# try changing from varchar to int (using cast)
		stylo.db.change_column_type(self.test_table_name, "id", "bigint", use_cast=True)
		self.assertIn("bigint", get_table_description()[0])

	def test_add_index(self) -> None:
		index_name = "test_index"
		stylo.db.add_index(self.test_table_name, ["id", "content(50)"], index_name)
		indexs_in_table = stylo.db.sql(
			f"""
			SELECT indexname
			FROM pg_indexes
			WHERE tablename = 'tab{self.test_table_name}'
			AND indexname = '{index_name}' ;
			""",
		)
		self.assertEqual(len(indexs_in_table), 1)

	def test_sequence_table_creation(self):
		from stylo.core.doctype.doctype.test_doctype import new_doctype

		dt = new_doctype("autoinc_dt_seq_test", autoname="autoincrement").insert(ignore_permissions=True)

		if stylo.db.db_type == "postgres":
			self.assertTrue(
				stylo.db.sql(
					"""select sequence_name FROM information_schema.sequences
				where sequence_name ilike 'autoinc_dt_seq_test%'"""
				)[0][0]
			)
		else:
			self.assertTrue(
				stylo.db.sql(
					"""select data_type FROM information_schema.tables
				where table_type = 'SEQUENCE' and table_name like 'autoinc_dt_seq_test%'"""
				)[0][0]
			)

		dt.delete(ignore_permissions=True)

	def test_is(self):
		user = stylo.qb.DocType("User")
		self.assertIn(
			'coalesce("name",',
			stylo.db.get_values(user, filters={user.name: ("is", "set")}, run=False).lower(),
		)
		self.assertIn(
			'coalesce("name",',
			stylo.db.get_values(user, filters={user.name: ("is", "not set")}, run=False).lower(),
		)


@run_only_if(db_type_is.POSTGRES)
class TestTransactionManagement(StyloTestCase):
	def test_create_proper_transactions(self):
		def _get_transaction_id():
			return stylo.db.sql("select txid_current()", pluck=True)

		self.assertEqual(_get_transaction_id(), _get_transaction_id())

		stylo.db.rollback()
		self.assertEqual(_get_transaction_id(), _get_transaction_id())

		stylo.db.commit()
		self.assertEqual(_get_transaction_id(), _get_transaction_id())


# Treat same DB as replica for tests, a separate connection will be opened
class TestReplicaConnections(StyloTestCase):
	def test_switching_to_replica(self):
		with patch.dict(stylo.local.conf, {"read_from_replica": 1, "replica_host": "localhost"}):

			def db_id():
				return id(stylo.local.db)

			write_connection = db_id()
			read_only_connection = None

			@stylo.read_only()
			def outer():
				nonlocal read_only_connection
				read_only_connection = db_id()

				# A new connection should be opened
				self.assertNotEqual(read_only_connection, write_connection)
				inner()
				# calling nested read only function shouldn't change connection
				self.assertEqual(read_only_connection, db_id())

			@stylo.read_only()
			def inner():
				# calling nested read only function shouldn't change connection
				self.assertEqual(read_only_connection, db_id())

			outer()
			self.assertEqual(write_connection, db_id())


class TestConcurrency(StyloTestCase):
	@timeout(5, "There shouldn't be any lock wait")
	def test_skip_locking(self):
		with self.primary_connection():
			name = stylo.db.get_value("User", "Administrator", for_update=True, skip_locked=True)
			self.assertEqual(name, "Administrator")

		with self.secondary_connection():
			name = stylo.db.get_value("User", "Administrator", for_update=True, skip_locked=True)
			self.assertFalse(name)

	@timeout(5, "Lock timeout should have been 0")
	def test_no_wait(self):
		with self.primary_connection():
			name = stylo.db.get_value("User", "Administrator", for_update=True)
			self.assertEqual(name, "Administrator")

		with self.secondary_connection():
			self.assertRaises(
				stylo.QueryTimeoutError,
				lambda: stylo.db.get_value("User", "Administrator", for_update=True, wait=False),
			)

	@timeout(5, "Deletion stuck on lock timeout")
	def test_delete_race_condition(self):
		note = stylo.new_doc("Note")
		note.title = note.content = stylo.generate_hash()
		note.insert()
		stylo.db.commit()  # ensure that second connection can see the document

		with self.primary_connection():
			n1 = stylo.get_doc(note.doctype, note.name)
			n1.save()

		with self.secondary_connection():
			self.assertRaises(stylo.QueryTimeoutError, stylo.delete_doc, note.doctype, note.name)


class TestSqlIterator(StyloTestCase):
	def test_db_sql_iterator(self):
		test_queries = [
			"select * from `tabCountry` order by name",
			"select code from `tabCountry` order by name",
			"select code from `tabCountry` order by name limit 5",
		]

		for query in test_queries:
			self.assertEqual(
				stylo.db.sql(query, as_dict=True),
				list(stylo.db.sql(query, as_dict=True, as_iterator=True)),
				msg=f"{query=} results not same as iterator",
			)

			self.assertEqual(
				stylo.db.sql(query, pluck=True),
				list(stylo.db.sql(query, pluck=True, as_iterator=True)),
				msg=f"{query=} results not same as iterator",
			)

			self.assertEqual(
				stylo.db.sql(query, as_list=True),
				list(stylo.db.sql(query, as_list=True, as_iterator=True)),
				msg=f"{query=} results not same as iterator",
			)

	@run_only_if(db_type_is.MARIADB)
	def test_unbuffered_cursor(self):
		with stylo.db.unbuffered_cursor():
			self.test_db_sql_iterator()
