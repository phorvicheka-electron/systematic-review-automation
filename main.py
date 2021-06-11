import sys
import os
import glob
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from common import util
from process import html_to_text, pdf_to_html, detec_sentence, LDA

form_class = uic.loadUiType("main.ui")[0]


# 참고 : https://wikidocs.net/book/2944
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.set_file_path)
        self.pushButton_2.clicked.connect(self.start_process)
        self.pushButton_3.clicked.connect(self.start_lda_process)

    def set_log(self, text):
        self.textEdit_2.append(text)

    # 폳더 경로 정하기
    def set_directory_path(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory', './')
        if directory:
            self.lineEdit.setText(directory)

    # 파일 경로 정하기
    def set_file_path(self):
        file = QFileDialog.getOpenFileName(self, 'Load File', './', "*.pdf")
        if file[0]:
            self.lineEdit.setText(file[0])
            print(file[0])

    def start_process(self):
        file_path = self.lineEdit.text()
        if(file_path != ''):
            self.textEdit_2.append('Start conversion processing ....')
            self.workder = ConvertThread(file_path)
            self.workder.finished.connect(self.set_text_convert)
            self.workder.start()

    def start_lda_process(self):
        file_path = self.lineEdit.text()
        if (file_path != ''):
            file_list = glob.glob(os.path.dirname(file_path) + '/*')
            max_features = int(self.lineEdit_2.text())
            n_components = int(self.lineEdit_3.text())
            n_words = int(self.lineEdit_4.text())

            self.textEdit_2.append('Start LDA processing ....')
            self.lda = LDAThread(file_list, max_features, n_components, n_words)
            self.lda.finished.connect(self.set_text_lda)
            self.lda.start()

    @pyqtSlot(str, str, str)
    def set_text_convert(self, html_data, text_data, sentence_date):
        self.textEdit.setText(html_data)
        self.plainTextEdit.setPlainText(html_data)
        self.plainTextEdit_2.setPlainText(text_data)
        self.plainTextEdit_3.setPlainText(sentence_date)
        self.tabWidget.setCurrentIndex(3)
        self.textEdit_2.append('Finish conversion.')

    @pyqtSlot(str, str)
    def set_text_lda(self, lda_result, topic_result):
        self.plainTextEdit_7.setPlainText(lda_result)
        self.plainTextEdit_8.setPlainText(topic_result)
        self.textEdit_2.append('Finish LDA process.')


class ConvertThread(QThread):
    finished = pyqtSignal(str, str, str)

    def __init__(self, file, parent=None):
        super(ConvertThread, self).__init__(parent)
        self.file = file

    def run(self):
        # pdf -> html
        html_file = pdf_to_html.convert_pdf_to_html(self.file)
        html_data = util.read_file(html_file)

        # html -> text
        text_file = html_to_text.convert_html_to_text(html_file)
        text_data = util.read_file(text_file)

        # text -> sentence
        sentence_data = detec_sentence.extract_sentence(text_file, text_data)

        self.finished.emit(html_data, text_data, sentence_data)


class LDAThread(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, file_list, max_features, n_components, n_words, parent=None):
        super(LDAThread, self).__init__(parent)
        self.file_list = file_list
        self.max_features = max_features
        self.n_components = n_components
        self.n_words = n_words

    def run(self):
        # LDA
        components, feature_names = LDA.do_lda(self.file_list, self.max_features, self.n_components)
        # topics
        topic_list = LDA.extract_topics(components, feature_names, self.n_words)
        self.finished.emit('\n'.join(LDA.print_lda_process), '\n'.join(topic_list))


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()

    app.exec_()
