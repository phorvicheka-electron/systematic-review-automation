import re
import numpy as np
from common import log, util
import os
import errno


def convert_html_to_text(html_file):
    log.debug("convert html to txt")

    lines = util.read_file_lines(html_file)

    collect_sentence = False
    make_sentence = False

    sentences = []
    sentence = []

    for each_line in lines:

        if collect_sentence is True:
            each_line = each_line.rstrip('\n')

            # 문단 시작점 판단
            if make_sentence is False and each_line.__contains__("<p>"):
                # 소제목 판단 ex) 1. Introduction, 2.1. Study design and data acquisition
                if re.compile('<p><b>[0-9][.][ \t\n\r\f\v].+').match(each_line) \
                        or re.compile('<p><i>[0-9][.][0-9][.][ \t\n\r\f\v].+').match(each_line):
                    make_sentence = False
                else:
                    make_sentence = True # 유의미한 문단 시작점일 경우

            # <p>문단 시작, 문단 중간일 경우 : sentence[] 추가
            if make_sentence is True:
                sentence.append(each_line)

            # 문단 마지막</p> 일 경우 : sentence[] 전처리
            if make_sentence is True and each_line.endswith("</p>"):

                sentence = remove_html_tag(' '.join(sentence))
                sentence = replace_special_char(sentence)
                sentence = concat_word(sentence)
                sentence = remove_ref(sentence)
                sentence = remove_bracket_number(sentence)

                # End of loop
                if end_flag(sentence):
                    break

                if can_be_a_sentence(sentence):
                    sentences.append(sentence)

                make_sentence = False
                sentence = []

        # 논문 ABSTRACT 시작 판단
        if not collect_sentence and start_flag(each_line):
            collect_sentence = True

    # write to file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(html_file[:-4])
    filePath = os.path.join(dir_path, "out-text", tail.rsplit('.', 1)[0] + '.txt')
    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    log.debug('out-text - file name: ' + filePath)
    txt_file = filePath
    # txt_file = html_file[:-4] + "txt"
    save_file = open(txt_file, "w")
    np.savetxt(save_file, sentences, fmt='%s')
    save_file.close()

    return txt_file


def remove_html_tag(raw_html):
    remove_text = re.sub('<.*?>', '', raw_html)
    return remove_text


def replace_special_char(text):
    text = text.replace('&lt;', '<') \
        .replace('&gt;', '>') \
        .replace('&amp;', '&') \
        .replace('&#169;', '(C)') \
        .replace('&#8211;', '-') \
        .replace('&#8216;', '\'') \
        .replace('&#8217;', '\'') \
        .replace('&quot;', '"') \
        .replace('&#8220;', '"') \
        .replace('&#8221;', '"') \
        .replace('&#8230;', '...') \
        .replace('&#8242;', '"') \
        .replace('&#8270;', '*') \
        .replace('&#8722;', '-') \
        .replace('&#8805;', '>=')

    return text


def concat_word(sentence):
    return sentence.replace("- ", "").replace("  ", " ")


def remove_ref(text):
    text = re.sub('[ ]*\\(.+?[et al]*\\)', '', text)
    #text = re.sub('.+?[et al]*\\)', '', text)
    #text = re.sub(' \\(.+?[et al]+', '', text)
    #text = re.sub(' \\(([a-zA-Z ]+, \d{4};)*[a-zA-Z ]+, \d{4}\\)', '', text)
    #text = re.sub('/\w/g', '', text)

    return text


def remove_bracket_number(text):
    #text = re.sub('( \\([+-<]?\d*(\.?\d*)\\))*', '', text)
    return text


def end_flag(txt):
    end_list = ['authorcontributionstatement',
                'fundingsource',
                'declarationofcompetinginterest',
                'disclosures/conflictsofinterest',
                'conflictsofinterest',
                'funding',
                'ethicalapproval',
                'acknowledgements']

    txt = txt.lower().replace(' ', '')

    return (txt in end_list)


def start_flag(txt):
    return txt.lower().replace(' ', '').find('abstract') > -1


def can_be_a_sentence(text):
    text = text.lower()

    result = contains_alpha(text) and\
             len(remove_bracket_text(text).strip()) > 10 and\
             not check_misc(text) and\
             not has_journal_info(text) and\
             meaningful_len(text)

    return result


def contains_alpha(txt):
    return bool(re.search('[a-zA-Z]', txt))


def remove_bracket_text(text):
    text = re.sub('\\(.+?\\)', '', text)
    return text


def check_misc(text):
    result = re.search("(received.+accepted)|(https.+doi)|(available.+online)|(corresponding.+author)|(abbreviations:)|(previous presentation)|(author contributions)|(equal contribution)|(Role of the funding)|(sciencedirect)|(journal of)", text)
    result_email = re.search(r"[.]*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[.]*", text)

    return result or result_email


def has_journal_info(text):
    result = re.search("journal.+(\(\d{4}\)|homepage)", text)

    return result


def meaningful_len(text):
    text_len = len(text)
    text_trim_len = len(text.replace(' ', ''))

    return ( text_trim_len / text_len ) > 0.7
