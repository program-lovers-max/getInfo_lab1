import os.path
import re
from collections import OrderedDict

import requests
import jsonpath
from lxml import etree
import json


def get_resp(url):
    """根据翻页url提取信息，为json格式"""
    headers = {
        # 此处的cookie为翻页时候提取的cookie
        "Cookie": "UM_distinctid=1882a0c953c196-0606ca8949d97b-26031a51-144000-1882a0c953d56f; wdcid=6e86a0dfb4080c90",
        "Host": "newssearch.chinadaily.com.cn",
        "Referer": "https://newssearch.chinadaily.com.cn/en/search?query=",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27",
        "X-Requested-With": "XMLHttpRequest"
    }
    response = requests.get(headers=headers, url=url)
    return response.json()


def format_data(data):
    """
    提取url两种方案，因为目前发现根据网页风格url至少存在两种提取方案
    :param data:
    :return:
    """
    # 方案1
    url_list = jsonpath.jsonpath(data, "$..shareUrl")

    # 方案2
    url_list_1 = jsonpath.jsonpath(data, "$..url")

    i = 0
    for url in url_list:
        if url is None:  # 如果第一种方案提取不到
            url_list[i] = url_list_1[i]  # 用第二种方案提取到的url替换第一种
        i += 1
    url_list = [s for s in url_list if "global" not in s]
    print(url_list)
    return url_list


def save_data(title, pub_time, content):
    """
    :param title:  标题
    :param pub_time:  发布时间
    :param content:  发布内容
    :return:
    """
    if (not os.path.exists('../news_cabin')):
        os.mkdir('../news_cabin')
    # 定义不允许用作文件名的字符集合
    unallowed_chars = r'[\\/:*?"<>|\s]'
    # 使用正则表达式替换不允许的字符
    file_title = re.sub(unallowed_chars, ' ', title)
    with open(f'../news_cabin/{file_title}.txt', mode='w', encoding='utf-8') as news:
        news.writelines('\t' + title + '\n')
        news.writelines('\t' + pub_time + '\n')
        news.writelines(content)


def get_url_per_detail(url_list):
    """
    获取每页具体详细内容
    :param url_list:
    :return:
    """
    headers = {
        "referer": "http://newssearch.chinadaily.com.cn/",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        # 此处的cookie为具体请求详情页时候提取的cookie
        "cookie": 'UM_distinctid=1882a0c953c196-0606ca8949d97b-26031a51-144000-1882a0c953d56f; wdcid=6e86a0dfb4080c90; pt_s_3bfec6ad=vt=1684397399474&cad=; pt_3bfec6ad=uid=HUgdy02MXm4Yifnjzcr6ZA&nid=1&vid=rrqfhBaaZ-WFG7BUr-ZvLg&vn=1&pvn=1&sact=1684397419616&to_flag=0&pl=0SJT/jOEH5Rb2p2jzb290Q*pt*1684397399474; wdses=7ae962fc26230a00; wdlast=1684417618'
    }

    for url in url_list:
        try:
            resp = requests.get(headers=headers, url=url)
            html = etree.HTML(resp.text)
            # 多规则匹配标题，目前发现两种风格
            title_list = html.xpath("//h1/text() | //h2/text()")
            # 多规则匹配出版时间，目前发现四种风格
            pub_time_list = html.xpath(
                '//div[@class="info"]/span[1]/text() |  //div[@class="content"]/div[1]/p/text() | //div[@class="articl"]//h5/text() | //div[@id="Title_e"]/h6/text()')
            # 多规则匹配内容，目前发现两种风格
            content_list = html.xpath(
                '//div[@id="Content"]/p/text() | //div[@id="Content"]/p[position()<last()]/text()')
            # 只要有一个字段为空，我们就舍弃这条新闻
            if not pub_time_list or not content_list or not title_list:
                continue
            title = title_list[0]
            pub_time = pub_time_list[0].strip().rsplit(": ", 1)[-1]

            content = ""
            for sentence in content_list:
                sentence = sentence.strip()
                sentence = "    " + sentence
                content += sentence + '\n'
            save_data(title=title, pub_time=pub_time, content=content)

        except Exception as html:
            continue


if __name__ == '__main__':
    i = 1
    for page in range(50):
        print(f"当前正在下载第{i}页......................")
        url = f"http://newssearch.chinadaily.com.cn/rest/en/search?&sort=dp&page={page}&curType=story&type=&channel=&source="

        # 获取分页内容，为json格式
        resp = get_resp(url=url)

        # 获取每页的十条url列表
        url_list = format_data(resp)

        # 处理每一页具体内容
        get_url_per_detail(url_list)

        i += 1
