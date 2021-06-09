import sys
import glob
from PyQt5 import uic
from PyQt5.QtWidgets import *

from common import util
from process import html_to_text, pdf_to_html, detec_sentence, LDA

form_class = uic.loadUiType("main.ui")[0]


# 참고 : https://wikidocs.net/book/2944
class WindowClass(QMainWindow, form_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.set_file_path)
        self.pushButton_2.clicked.connect(self.start_process)

    def set_log(self, text):
        print(text)
        self.textEdit_2.setText(text)

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

    # 토픽 추출 프로세스 시작
    def start_process(self):
        file_path = self.lineEdit.text()

        # set html file
        html_file = pdf_to_html.convert_pdf_to_html(file_path)
        html_data = util.read_file(html_file)
        self.textEdit.setText(html_data)
        self.plainTextEdit.setPlainText(html_data)

        # set text file
        text_file = html_to_text.convert_html_to_text(html_file)
        text_data = util.read_file(text_file)
        self.plainTextEdit_2.setPlainText(text_data)
        self.tabWidget.setCurrentIndex(1)

        # set sentence
        text_file, sentence_list = detec_sentence.extract_sentence(text_file, text_data)
        self.plainTextEdit_3.setPlainText('\n'.join(sentence_list))
        self.tabWidget.setCurrentIndex(2)

        # topic
        # file_list = glob.glob('C:/paper/*')
        # topic_list = LDA.extract_topics(file_list, 1000, 5, 7)
        # self.plainTextEdit_8.setPlainText('\n'.join(topic_list))


if __name__ == "__main__" :

    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    # file_list = glob.glob('C:/paper/*')
    # topic_list = LDA.extract_topics(file_list, 1000, 5, 7)
    app.exec_()
