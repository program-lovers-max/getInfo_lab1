# 文本预处理
import json
import re

import numpy as np
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

# 停用词
stop_words = set(stopwords.words('english'))

# 词形归并对象
lem = WordNetLemmatizer()

with open('../json_directory/key_words.json') as f:
    key_words = json.loads(f.read())

with open('../json_directory/rev_index.json') as f:
    index = json.loads(f.read())

with open('../json_directory/text_vector.json') as f:
    text_vec = json.loads(f.read())


def pre_process(search_content):
    # 去除标点符号
    text = re.sub(r"[^a-zA-Z\d]", " ", search_content)
    # 转换成小写
    text = text.lower()
    # 去除特殊符号和数字
    text = re.sub("(\\W)+", " ", text)
    # 字符串转为List
    text = text.split()
    # 清除停用词
    text = [lem.lemmatize(word) for word in text if not word in stop_words]
    return text


def get_result(search_content):
    text = pre_process(search_content)
    # 存储搜索文本的关键词向量
    key_vector = []
    # 遍历构建向量
    for i in range(500):
        if key_words[i] in text:
            key_vector.append(1)
        else:
            key_vector.append(0)
    # 标题-余弦相似度字典
    cos_dict = {}
    for word in text:  # 遍历每一个词
        if word in key_words:  # 只处理关键词
            for index_dict in index[word]:  # 查看每一篇出现该关键词的文章
                title = index_dict
                if cos_dict.get(title) == None:  # 如果之前没有记录该文章
                    # 计算余弦相似度
                    cos = np.dot(np.array(key_vector), np.array(text_vec[title])) / (
                                np.linalg.norm(key_vector) * np.linalg.norm(text_vec[title]))
                    # 存储在字典中
                    cos_dict[title] = cos
    # 将字典各项提取出来存入列表
    cos_dict = list(cos_dict.items())
    # 按余弦相似度降序排列（即展示时相关度从高到底）
    cos_dict = sorted(cos_dict, key=lambda x: x[1], reverse=True)
    return cos_dict


def show_news(cos_dict):
    for title in cos_dict:
        print(title[0])


if __name__ == '__main__':
    print('请输入你想要查询的文本(词或句皆可)')
    sentence = input()
    show_news(get_result(sentence))
