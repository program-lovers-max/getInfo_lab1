# 文本预处理
import json
import os
import re
import speech_recognition as sr
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import csv
from tkinter import Tk, Entry, Button, Label
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

with open('../json_directory/url_index.json') as f:
    url_index = json.loads(f.read())

with open('../json_directory/date_index.json') as f:
    date_index = json.loads(f.read())
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
                    cos_dict[title] = [cos]
                cos_dict[title].append(word)
    # 将字典各项提取出来存入列表
    cos_list = list(cos_dict.items())
    # 按余弦相似度降序排列（即展示时相关度从高到底）
    cos_list = sorted(cos_list, key=lambda x: x[1], reverse=True)
    return cos_list



def show_news(cos_list):
    header = ["相关度", "题目", "主要匹配内容", "URL", "日期"]  # 设置表头
    with open('./result.csv', 'w', encoding='utf-8', newline='') as result_csv:
        writer = csv.writer(result_csv)
        writer.writerow(header)
        for item in cos_list:
            correlation = item[1][0]
            title = item[0]
            del item[1][0]
            match_content = item[1]
            URL = url_index.get(title)
            date = date_index.get(title)
            info = [correlation, title, match_content, URL, date]
            writer.writerow(info)
    result_csv.close()
    os.system('start ./result.csv')


def submit():
    entered_text = entry.get()
    print("用户对本次搜索结果的评分是:", entered_text)


if __name__ == '__main__':
    r = sr.Recognizer()
    print("-------控制台文本输入请按0，语音输入请按1---------")
    choice = int(input())
    if choice:
        with sr.Microphone() as source:
            while True:
                print('请说出你想查询的词或句')
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                try:
                    sentence = r.recognize_sphinx(audio)
                    print(f'您的语音输入是{sentence}')
                    show_news(get_result(sentence))
                    break
                except Exception as e:
                    print('未能识别你的语音，请重试')
    else:
        print('请输入你想要查询的文本(词或句皆可)')
        sentence = input()
        show_news(get_result(sentence))

    # 创建主窗口
    root = Tk()

    # 设置窗口大小
    root.geometry("500x300")

    # 创建标签
    label = Label(root, text="请输入你对本次搜索结果的评分(0-10)")
    label.pack()

    # 创建输入框
    entry = Entry(root)
    entry.pack()

    # 创建按钮
    button = Button(root, text="提交", command=submit)
    button.pack()

    # 设置布局管理器
    label.pack(pady=40)  # 添加一些垂直间距
    entry.pack(pady=20)
    button.pack(pady=20)
    # 进入事件循环
    root.mainloop()
