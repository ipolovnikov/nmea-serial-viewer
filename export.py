import sys
import pynmea2
from PyQt5.QtCore import QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QFileDialog, QApplication


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle("Export")
        self.showDialog()

    def showDialog(self):
        input_file_path = QFileDialog.getOpenFileName(self, "Open file", "./log")[0]

        input_file = QFile(input_file_path)
        if input_file.open(QIODevice.OpenModeFlag.ReadOnly):
            output_file = QFile(input_file_path + ".txt")
            if output_file.open(QIODevice.OpenModeFlag.WriteOnly):
                output_stream = QTextStream(output_file)

                output_stream << str.join(";", ["Дата", "Час", "Джерело даних", "Тип повідомлення"]) << "\n"

                while not input_file.atEnd():
                    line = input_file.readLine().data().decode()
                    print(line)
                    try:
                        if len(line) > 24:
                            msg = pynmea2.parse(line[24:])
                            output = [
                                line[:10],
                                line[11:19],
                                msg.talker,
                                msg.sentence_type,
                            ] + msg.data
                            self.textEdit.append(str.join(";", output))
                            output_stream << str.join(";", output) << "\n"
                    except pynmea2.ParseError as e:
                        print("Parse error: {}".format(e))
                        continue
            else:
                print("Output file stream error")
        else:
            print("Input file stream error")

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
