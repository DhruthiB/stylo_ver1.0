import stylo
from stylo.tests.utils import StyloTestCase
from stylo.utils import get_html_for_route


class TestSitemap(StyloTestCase):
	def test_sitemap(self):
		from stylo.test_runner import make_test_records

		make_test_records("Blog Post")
		blogs = stylo.get_all("Blog Post", {"published": 1}, ["route"], limit=1)
		xml = get_html_for_route("sitemap.xml")
		self.assertTrue("/about</loc>" in xml)
		self.assertTrue("/contact</loc>" in xml)
		self.assertTrue(blogs[0].route in xml)
