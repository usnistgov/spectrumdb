import sys
import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # We want the axes cleared every time plot() is called

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MaxSpectraPlot(MyMplCanvas):
    """Max spectra plot """
    def __init__(self,  width = 5 ,
            height = 4, dpi = 100, fmin = None, fmax = None, metadata = None,statusbar=None):
        MyMplCanvas.__init__(self,width=width,  height=height, dpi = dpi)
        self.freqs = np.arange(fmin,fmax + 10,10)
        self.pmean_dbm = metadata["pmean_dbm"]
        self.iqr_dbm = metadata["iqr_dbm"]
        self.statusbar = statusbar
        self.axes = self.fig.add_subplot(111)
        self.compute_initial_figure()

    def compute_initial_figure(self):
        self.axes.hold(False)
        def onPick(event):
            i = event.ind[0]
            self.statusbar.showMessage("Freq. (MHz) : " +  str(self.freqs[i]) +
                    "; pmean (dBm) : " + str(self.pmean_dbm[i]) +
                    "; IQR (dBm) : " + str(self.iqr_dbm[i]))

        p = self.axes.errorbar(self.freqs,self.pmean_dbm, yerr=self.iqr_dbm,
                color="green", ls="dotted", picker=5)
        self.axes.set_title("Peak power (dBm) vs. Freq (MHz)")
        self.fig.canvas.mpl_connect('pick_event',onPick)
        self.axes.set_ylabel("Power (dBm)")
        self.axes.hold(True)


class SpectrogramPlot(MyMplCanvas):
    """ Spectrogram plot """
    def __init__(self, width = 5, height = 4, dpi = 100, dataset=None,
             metadata=None, dataFile = None, statusbar = None):
        MyMplCanvas.__init__(self,width=width,  height=height, dpi = dpi)
        fmin = dataset['fmin']
        fmax = dataset['fmax']
        self.freqs = np.arange(fmin,fmax + 10,10)
        flo_mhz = dataset["flo_mhz"]
        self.sample_rate = dataset["sample_rate"]
        fft_size = dataset["fft_size"]
        gaindB = dataset["gain"]
        # convert amplifier gain to linear units
        Vgain=pow(10,(gaindB/20.0))
        # VST calibration in dB
        VcaldB=1.64
        Vcal=pow(10,(VcaldB/20.0))
        self.freqs = np.arange(fmin,fmax + 10,10)
        temp = np.loadtxt(dataFile,dtype='float',delimiter='\t')
        # Normalize the data with fft size
        z = temp/fft_size
        #Apply calibrations for front end gain, cable loss, splitter loss
        z = z/Vgain
        z = z*Vcal
        z_len = len(z)
        # Power values in dbm
        self.z_dbm = 20*np.log10(z) - 10*np.log10(100) + 30
        self.rows = np.shape(self.z_dbm)[0]
        self.cols = np.shape(self.z_dbm)[1]
        self.min_power = np.amin(self.z_dbm)
        self.max_power = np.amax(self.z_dbm)
        self.compute_initial_figure()

    def compute_initial_figure(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(True)
        cmap = plt.cm.spectral
        self.axes.get_xaxis().set_visible(False)
        self.axes.set_yticklabels([str(np.round(i/float(self.sample_rate),decimals=2)) for i in range(0,self.rows,10)])
        self.axes.set_ylabel("Time (us)")
        cax = self.axes.imshow(self.z_dbm,
                         interpolation='none',
                         origin='lower',
                         aspect='auto',
                         cmap=cmap)
        self.axes.hold(True)
        cbar = self.fig.colorbar(cax, orientation = 'horizontal')
        r = (self.max_power - self.min_power)/2 + self.min_power
        cbar.set_ticks([self.min_power,r,self.max_power])




class ShowMaxSpectraStats(QMainWindow):
    def __init__(self,dataset,metadata,maxSpectraFile):
        QMainWindow.__init__(self)
        self.dataset = dataset
        fmin = dataset["fmin"]
        fmax = dataset["fmax"]
        self.fpeak_mhz = metadata["fpeak_mhz"]

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Metadata for " + dataset["name"])
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        if metadata is not None:
            metaplot = MaxSpectraPlot(fmin=fmin,fmax=fmax,metadata=metadata,
                    width=12,height=4, dpi=100,statusbar=self.statusBar())
            l.addWidget(metaplot)
            spectrogram = SpectrogramPlot(width = 12, height = 4, dpi = 100, dataset=dataset,
                    metadata=metadata, dataFile=maxSpectraFile, statusbar = None)
            l.addWidget(spectrogram)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

