import sys
sys.path.append("../")
import unittest
import populatedb

class PeakStatsTest(unittest.TestCase):
    def setUp(self):
        pass

    def testPeakStats(self):
        fname = "VST12Sep16_155710_MaxSpectra.tsv"
        fmin = 3500
        fmax = 3650
        flo_mhz = 3577
        fft_size = 1024
        gain =3
        sample_rate = 225
        populatedb.compute_peak_stats_worker(fname,fmin,fmax,flo_mhz,fft_size,sample_rate,gain)

if __name__ == "__main__":
     suite = unittest.TestLoader().loadTestsFromTestCase(PeakStatsTest)
     unittest.TextTestRunner(verbosity=2).run(suite)


