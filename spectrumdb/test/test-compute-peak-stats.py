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


