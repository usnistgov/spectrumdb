
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
import unittest
import populatedb
import reference_values
import numpy as np

class PeakStatsTest(unittest.TestCase):
    def setUp(self):
        pass

    def testPeakStats(self):
        fname = "VST12Sep16_155710_MaxSpectra.tsv"
        fmin = 3500
        fmax = 3650
        flo_mhz = reference_values.flo_mhz
        fft_size = 1024
        gain =26.4
        sample_rate = 225
        retval = populatedb.compute_peak_stats_worker(fname,fmin,fmax,flo_mhz,fft_size,sample_rate,gain)
        self.assertTrue(retval["pmax_dbm"] == reference_values.pmax_dbm)
        self.assertTrue(np.array_equal(retval["pmean_dbm"]
            ,reference_values.pmean_dbm))
        self.assertTrue(np.array_equal(retval["iqr_dbm"],reference_values.iqr_dbm))
        self.assertTrue(retval["fpeak_mhz"] == reference_values.fc)

if __name__ == "__main__":
     suite = unittest.TestLoader().loadTestsFromTestCase(PeakStatsTest)
     unittest.TextTestRunner(verbosity=2).run(suite)


