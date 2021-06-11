import os
import numpy as np
from sparknlp.annotator import *
from sparknlp.base import *
from pyspark.sql import SparkSession

import common.log
from common.util import *


# 모델 생성
# 참고1 : https://nlp.johnsnowlabs.com/docs/en/install#offline (Spark NLP 적용)
# 참고2 : https://nlp.johnsnowlabs.com/docs/en/install#windows-support (Spark NLP, Windows)
# 참고3 : https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Public/2.Text_Preprocessing_with_SparkNLP_Annotators_Transformers.ipynb (Sentence Detector DL)
def create_model():
    os.environ["HADOOP_HOME"] = "C:/hadoop" # windows winutils.exe 경로

    spark = SparkSession.builder \
        .appName("Spark NLP") \
        .master("local[*]") \
        .config("spark.driver.memory", "16G") \
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.kryoserializer.buffer.max", "2000M") \
        .config("spark.jars", base_dir_path()+"/lib/spark-nlp-assembly-3.0.3.jar") \
        .getOrCreate()

    documenter = DocumentAssembler() \
        .setInputCol("text") \
        .setOutputCol("document")

    sentenceDetector = SentenceDetector() \
        .setInputCols(['document']) \
        .setOutputCol('sentences')

    sd_pipeline = PipelineModel(stages=[documenter, sentenceDetector])
    sd_model = LightPipeline(sd_pipeline)

    return sd_model

global model
model = create_model()

# 문장 토큰화
def get_sentences(text):
    sentence_list = []

    for anno in model.fullAnnotate(text)[0]["sentences"]:
        #print("{}".format(anno.result.replace('\n', '')))
        sentence = "{}".format(anno.result.replace('\n', ''))
        sentence_list.append(sentence)
    return sentence_list


# 문장 토큰화 프로세스
def extract_sentence(file, text):
    common.log.debug('detect sentence')
    sentence_list = get_sentences(text)

    txt_file = file[:-5] + "_sentence.txt"
    save_file = open(txt_file, "w")
    np.savetxt(save_file, sentence_list, fmt='%s')
    save_file.close()

    return '\n'.join(sentence_list)








