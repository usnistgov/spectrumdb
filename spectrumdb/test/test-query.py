
# This software was developed by employees of the National Institute
# of Standards and Technology (NIST), an agency of the Federal
# Government. Pursuant to title 17 United States Code Section 105, works
# of NIST employees are not subject to copyright protection in the United
# States and are considered to be in the public domain. Permission to freely
# use, copy, modify, and distribute this software and its documentation
# without fee is hereby granted, provided that this notice and disclaimer
# of warranty appears in all copies.
#
# THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
# EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
# TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
# AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
# WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
# ERROR FREE. IN NO EVENT SHALL NASA BE LIABLE FOR ANY DAMAGES, INCLUDING,
# BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
# ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS
# SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR
# OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY
# OR OTHERWISE, AND WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT
# OF THE RESULTS OF, OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.
#
# Distributions of NIST software should also include copyright and licensing
# statements of any third-party software that are legally bundled with
# the code in compliance with the conditions of those licenses.
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
