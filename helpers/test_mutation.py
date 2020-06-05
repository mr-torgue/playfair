import unittest
import mutations as m

class SelectionTestCase(unittest.TestCase):

	def setUp(self):
		self.s1 = "abcdefghijklmnopqrstuvwxy"
		self.s2 = "Dit is een onzin Bericht! met vreeme $%^ tekens. Dit wordt niet gebruikt maar zou wel moetne werken!."

	'''
	Swap can generate out of index bounds exceptions. NOTE: negative values do work!
	'''
	def test_swap(self):
		self.assertEqual(m.swap(self.s1, 0, 24), "ybcdefghijklmnopqrstuvwxa")
		self.assertEqual(m.swap(self.s1, 2, 2), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.swap(self.s1, 7, 1), "ahcdefgbijklmnopqrstuvwxy")
		self.assertEqual(m.swap(self.s2, 37, 38), "Dit is een onzin Bericht! met vreeme %$^ tekens. Dit wordt niet gebruikt maar zou wel moetne werken!.")
		with self.assertRaises(Exception):
			m.swap(self.s1, 1, 25)

	def test_swap_row(self):
		self.assertEqual(m.swap_row(self.s1, 1, 1, 6), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.swap_row(self.s1, 1, 1, 26), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.swap_row(self.s1, 1, 2, 6), "abcdefmnopqrghijklstuvwxy")
		self.assertEqual(m.swap_row(self.s1, 3, 4), "abcdefghijklmnouvwxypqrst")
		# onderstaande is een bug
		# self.assertEqual(m.swap_row(self.s1, 3, 4, 6), "abcdefghijklmnopqrystuvwx")
		self.assertEqual(m.swap_row(self.s2, 0, 2, 8), " Berichten onzinDit is e! met vreeme $%^ tekens. Dit wordt niet gebruikt maar zou wel moetne werken!.")
		#with self.assertRaises(Exception):
		#	m.swap_row(self.s1, 11, 2)

	def test_swap_col(self):
		self.assertEqual(m.swap_col(self.s1, 1, 1, 3), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.swap_col(self.s1, 1, 2, 10), "acbdefghijkmlnopqrstuwvxy")

	def test_shift(self):
		self.assertEqual(m.shift(self.s1, 1), "yabcdefghijklmnopqrstuvwx")
		self.assertEqual(m.shift(self.s1, 3), "wxyabcdefghijklmnopqrstuv")

	def test_shift_row(self):
		self.assertEqual(m.shift_row(self.s1, 1, 0), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.shift_row(self.s1, 1, 2), "abcdeijfghklmnopqrstuvwxy")
		self.assertEqual(m.shift_row(self.s1, 1, 2, 6), "abcdefklghijmnopqrstuvwxy")

	def test_shift_col(self):
		self.assertEqual(m.shift_col(self.s1, 1, 0), "abcdefghijklmnopqrstuvwxy")
		self.assertEqual(m.shift_col(self.s1, 1, 2), "aqcdefvhijkbmnopgrstulwxy")
		self.assertEqual(m.shift_col(self.s1, 1, 2, 6), "ancdefgtijklmbopqrshuvwxy")

if __name__ == '__main__':
	unittest.main()