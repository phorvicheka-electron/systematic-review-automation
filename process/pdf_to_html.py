import pdfbox

from common import log


def convert_pdf_to_html(file_path):
    log.debug("convert pdf to html")
    p = pdfbox.PDFBox()
    p.extract_text(file_path, html=True)
    path = file_path.split('.pdf')

    return path[0]+".html"

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
#     #WindowClass().set_log("안료")
#     return pdf_list[0]