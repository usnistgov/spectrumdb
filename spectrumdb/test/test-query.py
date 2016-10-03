import sys
sys.path.append("../")
import querydb as query
import unittest

class QueryTest(unittest.TestCase):
    def setUp(self):
        pass

    def testQuery(self):
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3540,radar3="N")
        self.assertTrue(res is not None and len(res) == 0)
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3570,radar3="N")
        self.assertTrue(res is not None and len(res) == 1)
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3540,radar3="Y")
        self.assertTrue(res is not None and len(res) == 1)
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3540)
        self.assertTrue(res is not None and len(res) == 1)
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3540,
                radar3="Y",
                startDate = "2016-04-10 21:47:11",
                endDate = "2016-04-10 22:47:11")
        print res
        self.assertTrue(res is not None and len(res) == 1)
        res = query.find_radar1(datasetName="SanDiego",fc_mhz=3540,
                radar3="N",
                startDate = "2016-04-10 21:47:11",
                endDate = "2016-04-10 22:47:11")
        self.assertTrue(res is not None and len(res) == 0)


if __name__ == "__main__":
     suite = unittest.TestLoader().loadTestsFromTestCase(QueryTest)
     unittest.TextTestRunner(verbosity=2).run(suite)
