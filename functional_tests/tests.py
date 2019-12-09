from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import os

MAX_WAIT = 10

class NewVisitorTest(StaticLiveServerTestCase):

	item_display_format = '{0}: {1}'
	to_do_item_1 = 'Buy peacock feathers'
	to_do_item_2 = 'Use peacock feathers to make a fly'
	to_do_item_3 = 'Buy milk'

	def setUp(self):
		self.browser = webdriver.Firefox()
		staging_server = os.environ.get('STAGING_SERVER')
		if staging_server:
			self.live_server_url='http://' + staging_server

	def tearDown(self):
		self.browser.quit()

	def format_item(self, position, text):
		return self.item_display_format.format(position, text)

	def add_item(self, item_text):
		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys(item_text)
		inputbox.send_keys(Keys.ENTER)

	def check_for_row_in_list_table(self, row_text):
		table = self.browser.find_element_by_id('id_list_table')
		rows = table.find_elements_by_tag_name('tr')
		self.assertIn(row_text, [row.text for row in rows])

	def wait_for_row_in_list_table(self, row_text):
		start_time = time.time()
		while True:
			try:
				self.check_for_row_in_list_table(row_text)
				return
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)	


	def test_can_start_a_list_and_retrive_it_later(self):

		# Eduth has heard about a cool new online to-do app. She goes
		# to check out its home
		self.browser.get(self.live_server_url)

		# She notices the page title and header mention to-do lists
		self.assertIn('To-Do', self.browser.title) #"Browser title was {0}".format(browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do', header_text)
		
		# She is invited to enter a to-do item straight away
		inputbox = self.browser.find_element_by_id('id_new_item')
		self.assertEquals(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

		# She types "Buy peacock feathers" into a text box (Edith's hobby
		# is tying fly-fishing lures)
		self.add_item(self.to_do_item_1)

		# When she hits enter, the page updates, and now the page lists
		# "1: Buy peacock feathers" as an item in a to-do list

		self.wait_for_row_in_list_table(self.format_item(1, self.to_do_item_1))

		# There is still a text box inviting her to add another item. She
		# enters "Use peacock feathers to make a fly" (Edith is very methodical)
		self.add_item(self.to_do_item_2)

		# The page updates again, and now shows both items on her list
		self.wait_for_row_in_list_table(self.format_item(1, self.to_do_item_1))
		self.wait_for_row_in_list_table(self.format_item(2, self.to_do_item_2))

		# Edith wonders whether the site will remember her list. Then she sees
		# that the site has generated a unique URL for her -- there is some
		# explanatory text to that effect.

		# She visits that URL - her to-do list is still there.

		# Satisfied, she goes back to sleep

	def test_multiple_users_can_start_lists_at_different_urls(self):
		# Edith starts a new to-do list
		self.browser.get(self.live_server_url)
		self.add_item(self.to_do_item_1)
		self.wait_for_row_in_list_table(self.format_item(1, self.to_do_item_1))

		# She noticed that her list has a unique URL
		edith_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')

		# Now a new user, Francis, comes along to the site.

		## We use a new browser session to make sure that no information
		## of Edith's is coming through from cookies etc

		self.browser.quit()
		self.browser = webdriver.Firefox()

		# Francis visits the home page. There is no sign of Edith's list
		self.browser.get(self.live_server_url)
		page_text = self.browser.find_element_by_tag_name('body').text
		self.assertNotIn(self.to_do_item_1, page_text)
		self.assertNotIn(self.to_do_item_2, page_text)

		# Francis starts a new list by entering a new item.
		# He is less interesting then Edith...
		self.add_item(self.to_do_item_3)
		self.wait_for_row_in_list_table(self.format_item(1, self.to_do_item_3))

		# Francis gets his unique URL
		francis_list_url = self.browser.current_url
		self.assertRegex(francis_list_url, '/lists/.+')
		self.assertNotEquals(francis_list_url, edith_list_url)

		# Again, there is no trace of Edith's list
		page_text = self.browser.find_element_by_tag_name('body').text
		self.assertNotIn(self.to_do_item_1, page_text)
		self.assertIn(self.to_do_item_3, page_text)

		# Satisfied, they both go back to sleep

	def test_layout_and_styling(self):
		# Edith goes th the home page
		self.browser.get(self.live_server_url)
		self.browser.set_window_size(1024, 768)

		# She notices the input box is nicely centred
		inputbox = self.browser.find_element_by_id('id_new_item')
		self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] /2, 512, delta=10)

		# She starts a new list and sees the input is nicely centred there to-do
		self.add_item('testing')
		self.wait_for_row_in_list_table(self.format_item(1, 'testing'))
		inputbox = self.browser.find_element_by_id('id_new_item')
		self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] /2, 512, delta=10)

