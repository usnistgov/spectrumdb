
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
import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pymongo
import json
import populatedb
import traceback
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg \
        import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import ShowMaxSpectraStats
import os

activeColor = QColor(200,200,0)
currentDataset = None

def getTableWidth(table):
    x = table.verticalHeader().size().width()
    for i in range(table.columnCount()):
        x += table.columnWidth(i)
    return x


def showTdmsMetadata(tdmsMetadata):
    """
    Show the TDMS metadatada in a popup.
    """
    dialog = QDialog()
    dialog.setWindowTitle("TDMS Metadata (extracted from TDMS File)")
    layout = QGridLayout()
    dialog.setLayout(layout)
    row  = 0
    for key in tdmsMetadata.keys():
        layout.addWidget(QLabel(str(key) + " :"),row,0)
        val = str(tdmsMetadata[key])
        layout.addWidget(QLabel(str(val)),row,1)
        row += 1

    ok = QPushButton('OK', dialog)
    ok.setDefault(True)
    ok.clicked.connect(dialog.reject)
    layout.addWidget(ok,row,0)
    dialog.exec_()

def  showMaxSpectraStats(dataset, metadata,maxSpectraFile):
        print "showMaxSpectraStats - todo put charts here "
        fmin = dataset["fmin"]
        fmax = dataset["fmax"]
        freqs = np.arange(fmin,fmax + 10,10)
        print "pmax_dbm",  metadata["pmax_dbm"]
        print "fpeak_mhz", metadata["fpeak_mhz"]
        print "freqs ", freqs
        print "pmean_dbm", metadata["pmean_dbm"]
        print  "iqr_dbm", metadata["iqr_dbm"]
        global plotWindow
        plotWindow = ShowMaxSpectraStats.ShowMaxSpectraStats(dataset,
                metadata,maxSpectraFile)
        plotWindow.show()


def showRadar1(metadata):
    """
    print list of radar1 records.
    """
    radar1List = metadata["RADAR1"]
    dialog = QDialog()
    dialog.setWindowTitle("RADAR1 info")
    layout = QGridLayout()
    dialog.setLayout(layout)
    row  = 0
    for radar in radar1List:
        layout.addWidget(QLabel("RADAR1 : "),row,0)
        val =  str(radar)
        layout.addWidget(QLabel(str(val)),row,1)
        row += 1
    ok = QPushButton('OK', dialog)
    ok.setDefault(True)
    ok.clicked.connect(dialog.reject)
    layout.addWidget(ok,row,0)
    dialog.exec_()

def drawMetadataList(metadataList):
    """
    Show the metadata list in a table view.
    """
    global mainWindow
    global currentDataset
    dataset = currentDataset
    columnNames = ["prefix", "measurementDate","instrumentDate",
            "PeakAmplitude", "tdms", "tdmsMetadata",
            "maxSpectraStats","refLvl","RADAR1","RADAR3","Comments"]
    tableWidget = QTableWidget(len(metadataList),len(columnNames), mainWindow)
    headerNames = QStringList()
    for hdrName in columnNames:
        headerNames.append(hdrName)
    tableWidget.setHorizontalHeaderLabels(headerNames)
    row = 0
    for metadata in metadataList:
        col = 0
        for fieldName in columnNames:
            if fieldName in metadata:
                if fieldName == "tdmsMetadata":
                    tableWidget.setItem(row,col,
                        QTableWidgetItem("Show_tdmsMetadata"))
                    tableWidget.item(row,col).setBackground(activeColor)
                elif fieldName == "maxSpectraStats":
                    tableWidget.setItem(row,col,
                        QTableWidgetItem("Show_maxSpectraStats"))
                    tableWidget.item(row,col).setBackground(activeColor)
                elif fieldName == "RADAR1":
                    tableWidget.setItem(row,col,
                        QTableWidgetItem("Show_RADAR1"))
                    tableWidget.item(row,col).setBackground(activeColor)
                else :
                    tableWidget.setItem(row,col,
                        QTableWidgetItem(str(metadata[fieldName])))
            else:
                tableWidget.setItem(row,col,
                        QTableWidgetItem("N/A"))
            col += 1
        row += 1
    # The following code gets invoked when a user clicks on 
    # a cell.
    def handleItemClicked(item) :
        keyName = columnNames[item.column()]
        row = item.row()
        if keyName == "tdmsMetadata":
            if "tdmsMetadata" in metadataList[row]:
                metadata = metadataList[row]["tdmsMetadata"]
                showTdmsMetadata(metadata)
        elif keyName == "maxSpectraStats":
            maxSpectraStats = metadataList[row]["maxSpectraStats"]
            maxSpectraFile = metadataList[row]["MaxSpectra"]
            showMaxSpectraStats(dataset, maxSpectraStats,maxSpectraFile)
        elif keyName == "RADAR1":
            if "RADAR1" in metadataList[row]:
                showRadar1(metadataList[row])

    screenSize = QDesktopWidget().availableGeometry()
    tableWidget.itemClicked.connect(handleItemClicked)
    #mainWindow.setFixedSize(getTableWidth(tableWidget),
    #        screenSize.height() * 0.7)
    mainWindow.setWindowState(PyQt4.QtCore.Qt.WindowMaximized)
    mainWindow.setCentralWidget(tableWidget)


def drawDatasets() :
    """
    Draw all the datasets on the main window.
    """
    global mainWindow
    global currentDataset

    datasets = populatedb.list_datasets()
    columnNames = ["name","lat","lon","alt","measurementTz","instrumentTz",
            "fmin","fmax","flo_mhz","fft_size",
            "sample_rate","antenna","gain"]

    tableWidget = QTableWidget(len(datasets),len(columnNames), mainWindow)
    headerNames = QStringList()
    for hdrName in columnNames:
        headerNames.append(hdrName)

    tableWidget.setHorizontalHeaderLabels(headerNames)

    row = 0
    for dataset in datasets:
        col = 0
        for fieldName in columnNames:
            fieldVal = dataset[fieldName]
            tableWidget.setItem(row,col, QTableWidgetItem(str(fieldVal)))
            if fieldName == "name":
                tableWidget.item(row,col).setBackground(activeColor)
            col = col + 1
        row = row + 1

    datasets = populatedb.list_datasets()
    if len(datasets) > 0:
        currentDataset = populatedb.list_datasets()[0]
    else:
        currentDataset = "UNKNOWN"

    def handleItemClicked(item) :
        global currentDataset
        keyName = columnNames[item.column()]
        print "Key val ", str(item.text()), "name ", keyName
        if keyName == "name":
            metadataList = populatedb.get_metadata_list(str(item.text()))
            currentDataset = populatedb.get_dataset(str(item.text()))
            drawMetadataList(metadataList)


    tableWidget.itemClicked.connect(handleItemClicked)

    screenSize = QDesktopWidget().availableGeometry()
    mainWindow.setWindowState(PyQt4.QtCore.Qt.WindowMaximized)
    mainWindow.setCentralWidget(tableWidget)

def createDataset():
    """
    Create a new dataset.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Create dataset")
    layout = QGridLayout()
    dialog.setLayout(layout)
    dialog.setModal(0)

    row = 0
    layout.addWidget(QLabel("Name :"),row,0)
    nameWidget = QLineEdit()
    layout.addWidget(nameWidget,row,1)

    row += 1
    layout.addWidget(QLabel("Lat :"),row,0)
    latWidget = QLineEdit()
    layout.addWidget(latWidget,row,1)

    row += 1
    layout.addWidget(QLabel("Lon :"),row,0)
    lonWidget = QLineEdit()
    layout.addWidget(lonWidget,row,1)

    row += 1
    layout.addWidget(QLabel("Alt :"),row,0)
    altWidget = QLineEdit()
    layout.addWidget(altWidget,row,1)

    row += 1
    layout.addWidget(QLabel("instrumentTz :"),row,0)
    instrumentTzWidget = QLineEdit()
    layout.addWidget(instrumentTzWidget,row,1)

    row += 1
    layout.addWidget(QLabel("fmin :"),row,0)
    fminWidget = QLineEdit()
    layout.addWidget(fminWidget,row,1)

    row += 1
    layout.addWidget(QLabel("fmax :"),row,0)
    fmaxWidget = QLineEdit()
    layout.addWidget(fmaxWidget,row,1)

    row += 1
    layout.addWidget(QLabel("flo_mhz :"),row,0)
    floMhzWidget = QLineEdit()
    layout.addWidget(floMhzWidget,row,1)

    row += 1
    layout.addWidget(QLabel("fft_size :"),row,0)
    fftSizeWidget = QLineEdit()
    layout.addWidget(fftSizeWidget,row,1)


    row += 1
    layout.addWidget(QLabel("sample_rate :"),row,0)
    sampleRateWidget = QLineEdit()
    layout.addWidget(sampleRateWidget,row,1)


    row += 1
    layout.addWidget(QLabel("antenna :"),row,0)
    antennaWidget = QLineEdit()
    layout.addWidget(antennaWidget,row,1)

    row += 1
    layout.addWidget(QLabel("gain :"),row,0)
    gainWidget = QLineEdit()
    layout.addWidget(gainWidget,row,1)

    #row += 1
    #layout.addWidget(QLabel("ref_level_dbm :"),row,0)
    #reflevelWidget = QLineEdit()
    #layout.addWidget(reflevelWidget,row,1)



    def createDataset():
        try :
            name = str(nameWidget.text())
            if name is None or name == "" :
                raise "Name cannot be null "
            lat = float(str(latWidget.text()))
            lon = float(str(lonWidget.text()))
            alt = float(str(altWidget.text()))
            fft_size = int(str(fftSizeWidget.text()))
            flo_mhz = float(str(floMhzWidget.text()))
            sample_rate = float(str(sampleRateWidget.text()))
            antenna = str(antennaWidget.text())
            if antenna is None or antenna == "" :
                raise "Antenna string is null"
            gain = float(str(gainWidget.text()))
            #reflevel_dbm = float(str(reflevelWidget.text()))
            fmin = float(str(fminWidget.text()))
            fmax = float(str(fmaxWidget.text()))
            instrumentTz = str(instrumentTzWidget.text())
            if instrumentTz is None or instrumentTz == "" :
                raise "InstrumentTz is null"
            populatedb.create_dataset(dataset_name=name,
                lat=lat,
                lon=lon,
                alt=alt,
                instrument_tz=instrumentTz,
                antenna=antenna,
                gain=gain,
                #reflevel_dbm=reflevel_dbm,
                flo_mhz=flo_mhz,
                fmin=fmin,
                fmax=fmax,
                sample_rate=sample_rate,
                fft_size=fft_size)
            drawDatasets()
        except:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error creating data set " + var))
            msgBox.exec_()


    row += 1
    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    ok = QPushButton('OK', dialog)
    ok.setDefault(True)
    ok.clicked.connect(createDataset)
    ok.clicked.connect(dialog.close)
    layout.addWidget(ok,row,0)
    layout.addWidget(cancel,row,1)
    dialog.exec_()




def deleteDatasetDialog():
    """
    Delete a dataset and all the stored metadata.
    """
    global currentDataset
    dialog = QDialog()
    dialog.setWindowTitle("Delete Dataset")
    layout = QGridLayout()
    dialog.setLayout(layout)
    dialog.setModal(0)
    row = 0
    layout.addWidget(QLabel("Name :"),row,0)
    nameWidget = QLineEdit()
    nameWidget.setText(currentDataset["name"])
    layout.addWidget(nameWidget,row,1)
    row += 1

    def deleteDataset():
        try:
            name = str(nameWidget.text())
            populatedb.purge_dataset(name)
            drawDatasets()
        except:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error purging data set " + var))
            msgBox.exec_()

    ok = QPushButton('Delete', dialog)
    ok.setDefault(True)
    ok.clicked.connect(deleteDataset)
    ok.clicked.connect(dialog.close)
    layout.addWidget(ok,row,0)
    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    layout.addWidget(cancel,row,1)
    dialog.exec_()



def configureDialog():
    """
    Configure google key. Google key is required for
    time conversions when the data is being loaded.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Configure google API key.")
    layout = QGridLayout()
    dialog.setLayout(layout)
    dialog.setModal(0)
    row = 0
    layout.addWidget(QLabel("API Key :"),row,0)
    pathname = os.environ.get("HOME") + "/.sdbconfig"
    apiKeyWidget = QLineEdit()
    if os.path.exists(pathname):
        with open(pathname) as config:
            jsonData = json.load(config)
            if "GOOGLE_TIMEZONE_API_KEY" in jsonData:
                apiKey = jsonData["GOOGLE_TIMEZONE_API_KEY"]
                apiKeyWidget.setText(QString(apiKey))
            else:
                apiKeyWidget.setText(QString("Get API Key for TimeZone API from google"))
    else:
        apiKeyWidget.setText(QString("Get API Key for TimeZone API from google"))
    layout.addWidget(apiKeyWidget,row,1)
    row += 1

    def configure():
        try:
            apiKey = str(apiKeyWidget.text())
            toWrite = {}
            toWrite['GOOGLE_TIMEZONE_API_KEY'] = apiKey
            with open(pathname,"w") as outfile:
                print "Saving to ", pathname
                jsonData = json.loads(json.dumps(toWrite))
                json.dump(jsonData,outfile)
            # TODO -- write out configuration to config file.
        except:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error purging data set " + var))
            msgBox.exec_()

    ok = QPushButton('Save', dialog)
    ok.setDefault(True)
    ok.clicked.connect(configure)
    ok.clicked.connect(dialog.close)
    layout.addWidget(ok,row,0)
    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    layout.addWidget(cancel,row,1)
    dialog.exec_()

def populateDialog():
    """
    Dialog to select directory from which to populate the db.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Populate the db with data")
    layout = QGridLayout()
    dialog.setLayout(layout)
    dialog.setModal(0)
    row = 0
    layout.addWidget(QLabel("Dataset Name :"),row,0)
    nameWidget = QLineEdit()
    layout.addWidget(nameWidget,row,1)

    row += 1
    layout.addWidget(QLabel("Directory :"),row,0)
    dirNameWidget = QLineEdit()
    layout.addWidget(dirNameWidget,row,1)
    pushButton = QPushButton("Browse",dialog)
    layout.addWidget(pushButton,row,2)


    def getDir():
        fileDialog = QFileDialog()
        fileDialog.setOption(QFileDialog.ShowDirsOnly)
        def setDirName(dirName):
            selectedFile = QFileDialog.getExistingDirectory(fileDialog)
            dirNameWidget.setText(selectedFile)
        fileDialog.directoryEntered.connect(setDirName)
        fileDialog.exec_()

    pushButton.clicked.connect(getDir)

    def populate():
        try:
            populatedb.recursive_walk_metadata(str(nameWidget.text()),
                    str(dirNameWidget.text()))
        except Exception as detail:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error populating data set : " + var))
            msgBox.exec_()

    row += 1
    ok = QPushButton('Populate', dialog)
    ok.setDefault(True)
    ok.clicked.connect(populate)
    ok.clicked.connect(dialog.close)
    layout.addWidget(ok,row,0)
    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    layout.addWidget(cancel,row,1)
    dialog.exec_()

def importDialog():
    """
    Dialog to import a csv file. The csv file
    contains annotations which are entered on a
    excel spread sheet.
    """
    global currentDataset
    dialog = QDialog()
    dialog.setWindowTitle("Import annotations")
    layout = QGridLayout()
    dialog.setLayout(layout)
    dialog.setModal(0)
    row = 0
    layout.addWidget(QLabel("Dataset Name :"),row,0)
    nameWidget = QLineEdit()
    nameWidget.setText(currentDataset["name"])
    layout.addWidget(nameWidget,row,1)
    row += 1
    layout.addWidget(QLabel("Excel CSV file :"),row,0)
    csvFileWidget = QLineEdit()
    layout.addWidget(csvFileWidget,row,1)
    pushButton = QPushButton("Browse")
    layout.addWidget(pushButton, row,2)
    def getCsvFile():
        selfilter = QString("CSV (*.csv *.CSV)")
        fileName = QFileDialog.getOpenFileName( None,
                                "Select input file",
                                "C:/", QString("All files (*.*)" ),
                                 selfilter )
        csvFileWidget.setText(fileName)

    def importCsvFile():
        try:
            datasetName = currentDataset["name"]
            fileName = str(csvFileWidget.text())
            populatedb.import_csv_file(datasetName,fileName)
        except Exception as detail:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error populating data set : " + var))
            msgBox.exec_()


    pushButton.clicked.connect(getCsvFile)

    def import_csv():
        try:
            datasetName = str(nameWidget.text())
            fileName = str(csvFileWidget.text())
            populatedb.import_csv_file(datasetName,fileName)
        except Exception as detail:
            var = traceback.format_exc()
            msgBox = QErrorMessage()
            msgBox.setModal(1)
            msgBox.showMessage(QString("error importing from csv file : " + var))
            msgBox.exec_()

    row += 1
    ok = QPushButton('Import', dialog)
    ok.setDefault(True)
    ok.clicked.connect(dialog.close)
    ok.clicked.connect(import_csv)
    layout.addWidget(ok,row,0)
    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    layout.addWidget(cancel,row,1)
    dialog.exec_()

def main():
    global mainWindow
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    menuBar = mainWindow.menuBar()
    fileMenu = menuBar.addMenu('File')

    mainWindow.setWindowTitle("Radar Waveform DB")
    # Add create button
    createButton = QAction(QIcon('create.png'),"Create",mainWindow)
    createButton.setShortcut('Ctrl+N')
    createButton.setStatusTip('Create new data set')
    createButton.triggered.connect(createDataset)
    fileMenu.addAction(createButton)

    # Add Populate button
    populateButton = QAction(QIcon('populate.png'),"Populate",mainWindow)
    populateButton.setShortcut('Ctrl+P')
    populateButton.setStatusTip('Populate the dataset')
    populateButton.triggered.connect(populateDialog)
    fileMenu.addAction(populateButton)

    # Add import button
    importButton = QAction(QIcon('import.png'),"Import annotations",mainWindow)
    importButton.setShortcut('Ctrl+I')
    importButton.setStatusTip('Import annotations from Excel CSV file')
    importButton.triggered.connect(importDialog)
    fileMenu.addAction(importButton)

    # Add delete button
    deleteButton = QAction(QIcon('delete.png'),"Delete",mainWindow)
    deleteButton.setShortcut('Ctrl+X')
    deleteButton.setStatusTip('Delete data set')
    deleteButton.triggered.connect(deleteDatasetDialog)
    fileMenu.addAction(deleteButton)

    # Add configure button
    configureButton = QAction(QIcon('configure.png'), 'Configure', mainWindow)
    configureButton.setShortcut('Ctrl+C')
    configureButton.setStatusTip('Exit application')
    configureButton.triggered.connect(configureDialog)
    fileMenu.addAction(configureButton)

    # Add exit button
    exitButton = QAction(QIcon('exit24.png'), 'Exit', mainWindow)
    exitButton.setShortcut('Ctrl+Q')
    exitButton.setStatusTip('Exit application')
    exitButton.triggered.connect(mainWindow.close)
    fileMenu.addAction(exitButton)


    # show datasets.
    drawmenu = menuBar.addMenu("Display")
    showButton = QAction(QIcon('create.png'),"Reload",mainWindow)
    showButton.setStatusTip("Reload from DB")
    showButton.triggered.connect(drawDatasets)
    drawmenu.addAction(showButton)

    drawDatasets()

    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
