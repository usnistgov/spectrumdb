import sys
sys.path.append("../")
import querydb as query
import unittest

class QueryTest(unittest.TestCase):
    def setUp(self):
        pass

    def testQuery(self):
        res = query.find_radar1("SanDiego1",3540)
        self.assertTrue(res is not None and len(res) == 0)
        res = query.find_radar1("SanDiego1",3570)
        self.assertTrue(res is not None and len(res) == 1)
        res = query.find_radar1("SanDiego1",3540,radar3="Y")
        self.assertTrue(res is not None and len(res) == 1)


if __name__ == "__main__":
     suite = unittest.TestLoader().loadTestsFromTestCase(QueryTest)
     unittest.TextTestRunner(verbosity=2).run(suite)
