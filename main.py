import sys
from threading import Thread

import pynmea2
from PyQt5.QtCore import QDateTime, QFile, QIODevice, QTextStream
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget

from ui_mainwindow import Ui_MainWindow

namePrefix = QDateTime.currentDateTimeUtc().toString("zzz")

lang = {
    "Timestamp": "Мітка часу",
    "Latitude": "Широта",
    "Latitude Direction": "Напрямок широти",
    "Longitude": "Довгота",
    "Longitude Direction": "Напрямок довготи",
    "GPS Quality Indicator": "Індикатор розрахунку координат",
    "Number of Satellites in use": "Кількість супутників",
    "Horizontal Dilution of Precision": "Горизонтальний геометричний \nпоказник погіршення точності (HDOP)",
    "Antenna Alt above sea level (mean)": "Висота над рівнем моря",
    "Units of altitude (meters)": "Одиниці виміру висоти",
    "Geoidal Separation": "Різниця між єліпсоїдом \nта рівнем моря",
    "Units of Geoidal Separation (meters)": "Одиниці виміру різниці",
    "Age of Differential GPS Data (secs)": "Вік даних GPS",
    "Differential Reference Station ID": "Ідентифікатор опорної станції",
    "Status": "Статус",
    "FAA mode indicator": "Індикатор режиму",
    "Mode": "Режим вибору формату",
    "Mode fix type": "Режим формату",
    "SV ID01": "ID активного супутника 01",
    "SV ID02": "ID активного супутника 02",
    "SV ID03": "ID активного супутника 03",
    "SV ID04": "ID активного супутника 04",
    "SV ID05": "ID активного супутника 05",
    "SV ID06": "ID активного супутника 06",
    "SV ID07": "ID активного супутника 07",
    "SV ID08": "ID активного супутника 08",
    "SV ID09": "ID активного супутника 09",
    "SV ID10": "ID активного супутника 10",
    "SV ID11": "ID активного супутника 11",
    "SV ID12": "ID активного супутника 12",
    "PDOP (Dilution of precision)": "Просторовий геометричний \nпоказник погіршення точності (PDOP)",
    "HDOP (Horizontal DOP)": "Горизонтальний геометричний \nпоказник погіршення точності (HDOP)",
    "VDOP (Vertical DOP)": "Вертикальний геометричний \nпоказник погіршення точності (VDOP)",
    "Number of messages of type in cycle": "Кількість повідомлень",
    "Message Number": "Номер повідомлення",
    "Total number of SVs in view": "Кількість супутників",
    "SV PRN number 1": "ID супутника 1",
    "Elevation in degrees 1": "Высота в градусах 1",
    "Azimuth, deg from true north 1": "Азимут супутника 1",
    "SNR 1": "Рівень сигналу 1",
    "SV PRN number 2": "ID супутника 2",
    "Elevation in degrees 2": "Высота в градусах 2",
    "Azimuth, deg from true north 2": "Азимут супутника 2",
    "SNR 2": "Рівень сигналу 2",
    "SV PRN number 3": "ID супутника 3",
    "Elevation in degrees 3": "Высота в градусах 3",
    "Azimuth, deg from true north 3": "Азимут супутника 3",
    "SNR 3": "Рівень сигналу 3",
    "SV PRN number 4": "ID супутника 4",
    "Elevation in degrees 4": "Высота в градусах 4",
    "Azimuth, deg from true north 4": "Азимут супутника 4",
    "SNR 4": "Рівень сигналу 4",
    "Speed Over Ground": "Швидкість над землею",
    "True Course": "Напрямок на полюс",
    "Datestamp": "Часова мітка",
    "Magnetic Variation": "Магнітне схилення",
    "Magnetic Variation Direction": "Напрямок магнітного схилення",
    "True Track made good": "Курс на істиний полюс",
    "True Track made good symbol": "Достовірність",
    "Magnetic Track made good": "Магнітне схилення",
    "Magnetic Track symbol": "М - магнітний",
    "Speed over ground knots": "Швидкість через наземні вузли",
    "Speed over ground symbol": "Символ швидкості над землею",
    "Speed over ground kmph": "Швидкість над землею",
    "Speed over ground kmph symbol": "Символ швидкості над землею",
}


class GridWindow(QMainWindow):
    def __init__(self, parent=None, name="Grid Window", fields=[], ax=100, ay=100):
        super(GridWindow, self).__init__(parent)

        self.cw = QWidget(parent)
        self.cw.setObjectName("cw")

        self.gridLayout = QGridLayout(self.cw)
        self.gridLayout.setObjectName("gridLayout")

        # talker labels
        label_about_talker = QLabel(self.cw)
        label_about_talker.setObjectName('label_about_talker')
        label_about_talker.setText('Джерело')
        setattr(self, 'label_about_talker', label_about_talker)
        self.gridLayout.addWidget(label_about_talker, 0, 0, 1, 1)

        label_value_talker = QLabel(self.cw)
        label_value_talker.setObjectName('label_value_talker')
        label_value_talker.setText('-')
        setattr(self, 'label_value_talker', label_value_talker)
        self.gridLayout.addWidget(label_value_talker, 0, 1, 1, 1)

        # generate labels from list
        for index, field in enumerate(fields):
            label_about_obj_name = f"label_about_{field[1]}"
            label_value_obj_name = f"label_value_{field[1]}"

            label_about = QLabel(self.cw)
            label_about.setObjectName(label_about_obj_name)
            label_about.setText(
                field[0] if field[0] not in lang.keys() else lang[field[0]]
            )
            label_about.setToolTip('%s - %s' % (index + 1, field[0]))

            label_value = QLabel(self.cw)
            label_value.setObjectName(label_value_obj_name)
            label_value.setText("-")
            label_value.setToolTip('%s - %s' % (index + 1, field[0]))

            setattr(self, label_about_obj_name, label_about)
            setattr(self, label_value_obj_name, label_value)

            self.gridLayout.addWidget(label_about, (index + 1), 0, 1, 1)
            self.gridLayout.addWidget(label_value, (index + 1), 1, 1, 1)

        self.setCentralWidget(self.cw)
        self.setGeometry(ax, ay, 300, len(fields) * 20)
        self.setWindowTitle(name)


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Main #%s" % namePrefix)

        self.ui.comboBox_device.addItems(
            list(map(lambda x: x.portName(), QSerialPortInfo.availablePorts()))
        )
        self.ui.comboBox_rate.addItems(map(str, QSerialPortInfo.standardBaudRates()))

        self.ui.GGAGridWindow = GridWindow(
            self, "GGA #%s" % namePrefix, pynmea2.types.talker.GGA.fields, 100, 100
        )
        self.ui.GLLGridWindow = GridWindow(
            self, "GLL #%s" % namePrefix, pynmea2.types.talker.GLL.fields, 150, 150
        )
        self.ui.GSAGridWindow = GridWindow(
            self, "GSA #%s" % namePrefix, pynmea2.types.talker.GSA.fields, 100, 200
        )
        self.ui.GSVGridWindow = GridWindow(
            self, "GSV #%s" % namePrefix, pynmea2.types.talker.GSV.fields, 150, 250
        )
        self.ui.RMCGridWindow = GridWindow(
            self, "RMC #%s" % namePrefix, pynmea2.types.talker.RMC.fields, 100, 300
        )
        self.ui.VTGGridWindow = GridWindow(
            self, "VTG #%s" % namePrefix, pynmea2.types.talker.VTG.fields, 150, 350
        )

        self.ui.pushButton_openDevice.clicked.connect(self.onOpenDevice)
        self.ui.pushButton_closeDevice.clicked.connect(self.onCloseDevice)
        self.ui.pushButton_showGGA.clicked.connect(self.onShowGGA)
        self.ui.pushButton_showGLL.clicked.connect(self.onShowGLL)
        self.ui.pushButton_showGSA.clicked.connect(self.onShowGSA)
        self.ui.pushButton_showGSV.clicked.connect(self.onShowGSV)
        self.ui.pushButton_showRMC.clicked.connect(self.onShowRMC)
        self.ui.pushButton_showVTG.clicked.connect(self.onShowVTG)

        # self.printData(pynmea2.parse("$GPGGA,123252.50,5028.01141,N,03028.16118,E,1,04,5.99,181.9,M,25.8,M,,*5F"))
        # self.printData(pynmea2.parse("$GNGLL,5546.95900,N,03740.69200,E,102030.000,A*20"))
        # self.printData(pynmea2.parse("$GPGSA,A,3,14,13,01,,,,,,,,,,6.84,5.99,3.32*09"))
        # self.printData(pynmea2.parse("$GPGSV,3,3,12,21,75,089,23,26,33,222,31,27,38,298,40,29,15,127,,0*61"))
        # self.printData(pynmea2.parse("$GPRMC,123253.00,A,5028.01116,N,03028.16185,E,1.100,,110122,,,A*7F"))
        # self.printData(pynmea2.parse("$GNVTG,49.75,T,,M,0.12,N,0.22,K,A*1F"))

    def onOpenDevice(self):
        # create serial
        self.serial = QSerialPort(
            self.ui.comboBox_device.currentText(),
            readyRead=self.onReadyRead,
            baudRate=int(self.ui.comboBox_rate.currentText()),
            dataBits=QSerialPort.DataBits.Data7,
            stopBits=QSerialPort.StopBits.OneStop,
        )
        # open device
        if self.serial.open(QIODevice.OpenModeFlag.ReadOnly):
            self.printLog("Device is open", "green")
            # switch buttons state
            self.ui.pushButton_openDevice.setEnabled(False)
            self.ui.pushButton_closeDevice.setEnabled(True)
            # create log output stream
            self.onCreateStream()
        else:
            self.printLog("Device did not open", "red")

    def onCloseDevice(self):
        if self.serial:
            if self.serial.isOpen():
                # close device
                self.serial.close()
                if not self.serial.isOpen():
                    self.ui.pushButton_openDevice.setEnabled(True)
                    self.ui.pushButton_closeDevice.setEnabled(False)
                    self.printLog("Device did close", "orange")
                else:
                    self.printLog("Device did not close", "red")
            else:
                self.printLog("Device did not open", "orange")
        else:
            self.printLog("Serial error", "red")

    def onCreateStream(self):
        # create log output stream
        self.outputFile = QFile(
            "log/"
            + QDateTime.currentDateTimeUtc().toString("yyyyMMddTHHmmsszzz")
            + "_"
            + namePrefix
            + ".log"
        )
        if self.outputFile.open(
            QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Truncate
        ):
            self.outputStream = QTextStream(self.outputFile)
            self.printLog("Output stream created", "green")
        else:
            self.printLog("Output stream did not created", "red")

    def onReadyRead(self):
        while self.serial.canReadLine():
            try:
                line = self.serial.readLine().data().decode().rstrip("\r\n")
                self.printLog(line, "blue")
                obj = pynmea2.parse(line)
                self.printData(obj)
                Thread(target=self.printData, args=[obj])
            except pynmea2.nmea.ParseError as e:
                self.printLog(str(e), "red")
            except Exception as e:
                self.printLog(str(e), "red")

    def onShowGGA(self):
        self.ui.GGAGridWindow.show()

    def onShowGLL(self):
        self.ui.GLLGridWindow.show()

    def onShowGSA(self):
        self.ui.GSAGridWindow.show()

    def onShowGSV(self):
        self.ui.GSVGridWindow.show()

    def onShowRMC(self):
        self.ui.RMCGridWindow.show()

    def onShowVTG(self):
        self.ui.VTGGridWindow.show()

    def printLog(self, msg, color: str = "black"):
        datetime = QDateTime.currentDateTimeUtc().toString("yyyy-MM-ddTHH:mm:ss.zzz")
        output = '<span style="color: %s">%s: %s</span>' % (
            color,
            datetime,
            msg,
        )
        self.ui.textEdit_output.append(output)

        if hasattr(self, "outputStream"):
            self.outputStream << datetime << " " << msg << "\n"

    def printData(self, obj: pynmea2.nmea.NMEASentence):
        self.ui.statusbar.showMessage(repr(obj))

        def fillGridWindow(window, fields, obj):
            talkers = {
                "GP": "GPS",
                "GL": "Глонасс",
                "GA": "Galileo",
                "BD": "Beidou",
                "GQ": "QZSS",
                "GN": "Змішане",
            }
            window.label_value_talker.setText(talkers[obj.talker] if (obj.talker in talkers.keys()) else obj.talker)
            for field in fields:
                getattr(window, f"label_value_{field[1]}").setText(
                    str(getattr(obj, f"{field[1]}"))
                )

        if type(obj) == pynmea2.types.talker.GGA:
            gps_qual = {
                0: "Недоступно",
                1: "Автономно",
                2: "Диференціально",
                3: "PPS",
                4: "Фіксований RTK",
                5: "Не фіксований RTK",
                6: "Екстраполяція",
                7: "Фіксовані координати",
                8: "Режим симуляції",
            }
            if obj.gps_qual in gps_qual.keys():
                obj.gps_qual = gps_qual[obj.gps_qual]

            fillGridWindow(self.ui.GGAGridWindow, pynmea2.types.talker.GGA.fields, obj)

        if type(obj) == pynmea2.types.talker.GLL:
            statuses = {"A": "Дані достовірні", "V": "Помилкові дані"}
            if obj.status in statuses.keys():
                obj.status = statuses[obj.status]

            faa_modes = {
                "A": "Автономний",
                "D": "Диференціальний",
                "E": "Апроксимація",
                "M": "Фіксовані дані",
                "N": "Недостовірні дані"
            }
            if obj.faa_mode in faa_modes.keys():
                obj.faa_mode = faa_modes[obj.faa_mode]

            fillGridWindow(self.ui.GLLGridWindow, pynmea2.types.talker.GLL.fields, obj)

        if type(obj) == pynmea2.types.talker.GSA:
            modes = {"A": "Автоматичний", "M": "Ручний"}
            if obj.mode in modes.keys():
                obj.mode = modes[obj.mode]

            types = {"1": "Рішення відсутне", "2": "2D", "3": "3D"}
            if obj.mode_fix_type in types.keys():
                obj.mode_fix_type = types[obj.mode_fix_type]

            fillGridWindow(self.ui.GSAGridWindow, pynmea2.types.talker.GSA.fields, obj)

        if type(obj) == pynmea2.types.talker.GSV:
            fillGridWindow(self.ui.GSVGridWindow, pynmea2.types.talker.GSV.fields, obj)

        if type(obj) == pynmea2.types.talker.RMC:
            statuses = {"A": "Дані достовірні", "V": "Помилкові дані"}
            if obj.status in statuses.keys():
                obj.status = statuses[obj.status]

            fillGridWindow(self.ui.RMCGridWindow, pynmea2.types.talker.RMC.fields, obj)

        if type(obj) == pynmea2.types.talker.VTG:
            faa_modes = {
                "A": "Автономний",
                "D": "Диференціальний",
                "E": "Апроксимація",
                "M": "Фіксовані дані",
                "N": "Недостовірні дані"
            }
            if obj.faa_mode in faa_modes.keys():
                obj.faa_mode = faa_modes[obj.faa_mode]

            fillGridWindow(self.ui.VTGGridWindow, pynmea2.types.talker.VTG.fields, obj)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # main window widget
    main = Main()
    main.show()
    # execute app
    sys.exit(app.exec())
