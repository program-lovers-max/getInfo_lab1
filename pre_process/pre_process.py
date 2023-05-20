# 文本预处理
import glob
import json
import os
import re

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# 停用词
stop_words = set(stopwords.words('english'))

# 词形归并对象
lem = WordNetLemmatizer()
# 全文字符串
corpus = []
# 未删去停用词的新闻标题-内容字典
dirty_corpus = {}
# 删去停用词的新闻标题-内容字典
clean_corpus = {}
# 存储新闻的目录
cabin_path = '../news_cabin'

# 遍历文件夹下的所有文本文件
for news_path in glob.glob(os.path.join(cabin_path, "*.txt")):
    with open(news_path, mode='r+', encoding='utf-8') as news:
        title = os.path.basename(news_path).strip().split('.')[0]
        text = news.readlines()
        text = ' '.join(text)
        # 去除标点符号
        text = re.sub(r"[^a-zA-Z\d]", " ", text)
        # 转换成小写
        text = text.lower()
        # 去除特殊符号
        text = re.sub("(\\W)+", " ", text)
        # 字符串转为List,用空格分词
        dirty_text = text.split()
        text = [lem.lemmatize(word) for word in dirty_text if not word in stop_words]
        clean_corpus[title] = text
        dirty_text = [lem.lemmatize(word) for word in dirty_text]
        text = " ".join(text)
        dirty_corpus[title] = dirty_text
        corpus.append(text)

# 创建TfidfVectorizer对象
vectorizer = TfidfVectorizer()
# 将文本数据转换为TF-IDF特征向量
matrix = vectorizer.fit_transform(corpus)
# 提取特征词和对应的TF-IDF值
features = vectorizer.get_feature_names_out()
tfidf_scores = matrix.toarray().sum(axis=0).tolist()
# 创建DataFrame存储特征词和TF-IDF值
df = pd.DataFrame({'word': features, 'tfidf': tfidf_scores})
# 按TF-IDF值降序排序
df = df.sort_values(by='tfidf', ascending=False)
# 选取排序后的前500个词作为关键词
key_words = df.head(500)['word'].tolist()
# 将关键词列表以JSON格式保存到文件
with open('../json_directory/key_words.json', 'w') as f:
    json.dump(key_words, f)

rev_index = {}
for news_name in glob.glob(os.path.join(cabin_path, "*.txt")):
    news_name = os.path.basename(news_name).strip().split('.')[0]
    for content_index in range(len(dirty_corpus[news_name])):
        word = dirty_corpus[news_name][content_index]
        if word in key_words:
            if not rev_index.get(word):
                rev_index[word] = {}
            if not rev_index[word].get(news_name):
                rev_index[word][news_name] = []
            rev_index[word][news_name].append(content_index)
with open("../json_directory/rev_index.json", "w") as f:
    json.dump(rev_index, f, indent=4)

text_vector = {}

for news_name in glob.glob(os.path.join(cabin_path, "*.txt")):
    news_name = os.path.basename(news_name).strip().split('.')[0]
    text_vector[news_name] = []
    for i in range(500):
        if key_words[i] in clean_corpus[news_name]:
            text_vector[news_name].append(1)
        else:
            text_vector[news_name].append(0)
with open('../json_directory/text_vector.json', 'w') as f:
    json.dump(text_vector, f, indent=4)
