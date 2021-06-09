import glob
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer

from common.util import *
from common import log

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))

# 단어 토큰화
def word_tokenize(text):
    word_tokens = nltk.word_tokenize(text)
    print("* tokenized:")
    print(word_tokens)
    return word_tokens


# 불용어 제거
def stopword(words):
    new_words = []
    for w in words:
        if w not in stop_words:
            new_words.append(w)
    print("* stop:")
    print(new_words)
    return new_words


# 표제어 추출
def lemmatization(words):
    n = WordNetLemmatizer()
    new_lemms = [n.lemmatize(w, pos='v') for w in words]

    print("* lemmatized:")
    print(new_lemms)

    return new_lemms


# 텍스트 전처리
def text_preprocessing(file):

    full_doc = []
    lines = read_file_lines(file)

    for each_line in lines:
        print("-------------------------------------------------------------")
        print("* origin:")
        print(each_line)

        # 단어 토큰화
        word_tokens = word_tokenize(each_line)

        # 불용어 제거
        words = stopword(word_tokens)

        # 표제어 추출
        new_lemms = lemmatization(words)

        # 역토큰화
        full_sentence = ' '.join(new_lemms)

        print("* Full sentence:")
        print(full_sentence)

        full_doc.append(full_sentence)

    return full_doc



# 참고1 : https://wikidocs.net/40710 (LDA 코드)
# 참고2 : https://wikidocs.net/30708 (LDA 개념)
# 참고2 : https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html
def do_lda(multiple_doc, max_features, n_components, n_words):
    log.debug('do LDA')
    # TF-IDF 행렬 만들기
    vectorizer = TfidfVectorizer(stop_words='english',
                                 max_features=max_features)  # 상위 1,000개의 단어 보존


    X = vectorizer.fit_transform(multiple_doc)
    var = X.shape
    print("* TF-IDF matrix : " + str(var)) # TF-IDF 행렬의 크기 확인

    # LDA 토픽 모델링
    lda_model = LatentDirichletAllocation(n_components=n_components, # topic 수
                                          learning_method='batch',
                                          random_state=800,
                                          max_iter=1000) # 최대 반복 횟수

    lda_top = lda_model.fit_transform(X)

    print("* lda_top")
    print(lda_top)
    print("* lda_model.components_")
    print(lda_model.components_)
    print("* lda_model.components_.shape")
    print(lda_model.components_.shape)

    feature_names = vectorizer.get_feature_names()  # 단어 집합. 1,000개의 단어 저장

    # 토픽 추출
    def get_topics(components, feature_names, n_words):
        log.debug('extract topics')
        topic_list = []
        for idx, topic in enumerate(components):
            print("Topic %d:" % (idx + 1), [feature_names[i] for i in topic.argsort()[:-n_words - 1:-1]])
            topic = [feature_names[i] for i in topic.argsort()[:-n_words - 1:-1]]
            topic_list.append(topic)

        print(topic_list)
        return topic_list

    topic_list = get_topics(lda_model.components_, feature_names, n_words)

    return topic_list


# 토픽 추출 과정
def extract_topics(file_list, max_features, n_components, n_words):

    multiple_doc = []
    count = 1
    for file in file_list:
        if file.endswith('_sentence.txt'):
            print("----------------------------------------------------")
            print("Start!")
            print("----------------------------------------------------")
            print("* txt file name [{0}] : {1}".format(count, file))

            # 텍스트 전처리
            doc = text_preprocessing(file)
            multiple_doc = multiple_doc + doc
            count += 1

    print("---------------------------------------------")
    print("Final document")
    print("---------------------------------------------")
    print(multiple_doc)
    print("---------------------------------------------")
    print("Final document //")
    print("---------------------------------------------")

    print("---------------------------------------------")
    print("LDA Processing...")
    print("---------------------------------------------")
    topic_list = do_lda(multiple_doc, max_features, n_components, n_words)
    print("---------------------------------------------")
    print("LDA processing has been done.")
    print("---------------------------------------------")

    return topic_list



