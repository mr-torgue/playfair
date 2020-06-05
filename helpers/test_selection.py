import unittest
import selection as sl

from numpy.random import RandomState

class SelectionTestCase(unittest.TestCase):

	def setUp(self):
        self.prng = RandomState(8292)

	def test_select_elitism(self):
		scores = []
		sl.select_elitism()

	def test_resize(self):
		self.widget.resize(100,150)
		self.assertEqual(self.widget.size(), (100,150),
						 'wrong size after resize')