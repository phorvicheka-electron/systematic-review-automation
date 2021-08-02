import pdfbox

from common import log
import os
import errno

def convert_pdf_to_html(file):
    log.debug("convert pdf to html")
    p = pdfbox.PDFBox()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(file)
    filePath = os.path.join(dir_path, "out-html", tail.rsplit('.', 1)[0] + '.html')
    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    p.extract_text(file, output_path=filePath, html=True)
    path = file.split('.pdf')

    # return path[0]+".html"
    return filePath

# def convert_pdf_to_html(directory_path):
#     log.debug("convert_pdf_to_html")
#     p = pdfbox.PDFBox()
#     file_list = os.listdir(directory_path)
#     pdf_list = []
#
#     for file in file_list:
#         if file.endswith(".pdf"):
#             path = directory_path+"/"+file
#             p.extract_text(path, html=True)
#
#             path = path.split('.pdf')
#             pdf_list.append(path[0]+".html")
#
#     return pdf_list[0]