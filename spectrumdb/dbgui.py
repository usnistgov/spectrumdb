import sys
import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import QStringList
import pymongo
import json
import populatedb


def drawMetadataList(metadataList):
    global mainWindow
    columnNames = ["prefix", "measurementDate","instrumentDate",
            "measurementTimeStamp", "instrumentTimeStamp",
            "universalTimeStamp", "PeakAmplitude", "tdms",
            "tdmsMetadata", "maxSpectraStats"]
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
                elif fieldName == "maxSpectraStats":
                    tableWidget.setItem(row,col,
                        QTableWidgetItem("Show_maxSpectraStats"))
                else :
                    tableWidget.setItem(row,col,
                        QTableWidgetItem(str(metadata[fieldName])))
            else:
                tableWidget.setItem(row,col,
                        QTableWidgetItem("N/A"))
            col += 1
        row += 1

    mainWindow.setCentralWidget(tableWidget)


def drawDatasets() :
    global mainWindow

    datasets = populatedb.list_datasets()
    if len(datasets) == 0:
        print "No data found"
        sys.exit()
    cols = len(datasets[0])

    tableWidget = QTableWidget(len(datasets),cols, mainWindow)
    headerNames = QStringList()
    for hdrName in datasets[0].keys():
        headerNames.append(hdrName)

    tableWidget.setHorizontalHeaderLabels(headerNames)

    col = 0
    row = 0
    for dataset in datasets:
        for fieldName in datasets[0].keys():
            fieldVal = dataset[fieldName]
            tableWidget.setItem(row,col, QTableWidgetItem(str(fieldVal)))
            col = col + 1
        row = row + 1

    def handleItemClicked(item) :
        keyName = datasets[0].keys()[item.column()]
        print "Key val ", str(item.text()), "name ", keyName
        if keyName == "name":
            metadataList = populatedb.get_metadata_list(str(item.text()))
            drawMetadataList(metadataList)


    tableWidget.itemClicked.connect(handleItemClicked)

    screenSize = QDesktopWidget().availableGeometry()
    mainWindow.setFixedSize(screenSize.width(), screenSize.height() * 0.7)
    mainWindow.setCentralWidget(tableWidget)

def createDataset():
    dialog = QDialog()
    dialog.setWindowTitle("Create dataset")
    msglabel = QLabel()
    layout = QGridLayout()
    dialog.setLayout(layout)

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
    layout.addWidget(QLabel("fft_size :"),row,0)
    fftSizeWidget = QLineEdit()
    layout.addWidget(fftSizeWidget,row,1)

    row += 1
    layout.addWidget(QLabel("flo_mhz :"),row,0)
    floMhzWidget = QLineEdit()
    layout.addWidget(floMhzWidget,row,1)

    row += 1
    layout.addWidget(QLabel("sample_rate :"),row,0)
    sampleRateWidget = QLineEdit()
    layout.addWidget(sampleRateWidget,row,1)

    row += 1
    layout.addWidget(QLabel("gain :"),row,0)
    gainWidget = QLineEdit()
    layout.addWidget(gainWidget,row,1)

    row += 1
    layout.addWidget(QLabel("fmin :"),row,0)
    fminWidget = QLineEdit()
    layout.addWidget(fminWidget,row,1)

    row += 1
    layout.addWidget(QLabel("fmax :"),row,0)
    fmaxWidget = QLineEdit()
    layout.addWidget(fmaxWidget,row,1)

    row += 1
    layout.addWidget(QLabel("instrumentTz :"),row,0)
    instrumentTzWidget = QLineEdit()
    layout.addWidget(instrumentTzWidget,row,1)

    cancel = QPushButton('Cancel',dialog)
    cancel.clicked.connect(dialog.reject)
    cancel.setDefault(True)
    ok = QPushButton('OK', dialog)
    ok.setDefault(True)
    layout.addWidget(ok,row,0)
    layout.addWidget(cancel,row,1)

    def accept():
        print "TOOD: Accept -- create dataset"

    ok.clicked.connect(accept)

    dialog.exec_()



if __name__ == "__main__":
    global mainWindow
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    mainWindow.resize(200,300)
    menuBar = mainWindow.menuBar()
    fileMenu = menuBar.addMenu('File')

    mainWindow.setWindowTitle("Radar Waveform DB")
    # Add create button
    createButton = QAction(QIcon('create.png'),"Create",mainWindow)
    createButton.setShortcut('Ctrl+N')
    createButton.setStatusTip('Create new data set')
    createButton.triggered.connect(createDataset)
    fileMenu.addAction(createButton)

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
