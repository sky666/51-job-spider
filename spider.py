import os
import re
import requests
import pandas as pd
from pyquery import PyQuery as pq


'''
    步骤：
    1. 下载页面          
    2. 解析页面            
    3. 保存数据
'''


def cached_url(url):
    """
    缓存一次, 避免重复下载浪费时间
    """
    folder = 'cached'  # 缓存在 cached 文件夹中
    filename = url.split(',')[-1]    # 用 url 中页面数命名 html 页面
    path = os.path.join(folder, filename)
    if os.path.exists(path):  # 判断是否页面已缓存在本地，如果已缓存，直接读取本地页面
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:  # 如果是第一次下载页面，使用 requests 请求页面并保存到本地文件夹
        if not os.path.exists(folder):
            # 建立 cached 文件夹
            os.makedirs(folder)

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def job_cached_url(url):
    '''
    从 url 中下载网页并解析出页面内所有的职位信息
    '''
    folder = "job_cached"
    id = re.findall(r'\d\d\d\d+', url)[0]  # 使用正则表达式定位页面 ID
    print(id)
    name = id + '.html'  # 以页面 ID 命名 html 页面
    path = os.path.join(folder, name)
    if os.path.exists(path):  # 判断是否页面已缓存在本地，如果已缓存，直接读取本地页面
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:  # 如果是第一次下载页面，使用 requests 请求页面并保存到本地文件夹
        if not os.path.exists(folder):
            # 建立 job_cached 文件夹
            os.makedirs(folder)

        headers = {
            'user-agent': '''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
        }
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def job_from_div(div):
    """
    从一个 div 里面获取到一个招聘岗位信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = {}  # 保存为字典
    m['job_position'] = e('.t1').text()   # 职位名
    m['company'] = e('.t2').text()   # 公司名
    m['location'] = e('.t3').text()   # 工作地点
    m['salary'] = e('.t4').text()     # 薪资
    m['date'] = e('.t5').text()     # 发布日期
    m['url'] = e('.t1')('a').attr('href')  # 招聘职位网址
    url = e('.t1')('a').attr('href')
    s = pq(job_cached_url(url))
    m['work_experience'] = s('.msg.ltype').text()  # 工作经验要求
    m['company type'] = s('.com_tag').text() # 公司类型

    return m


def jobs_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的职位
    """
    # 页面只需要下载一次
    page = cached_url(url)
    e = pq(page)
    items = e('.dw_table')('.el')[1:]
    # 调用 job_from_div
    jobs = [job_from_div(i) for i in items]
    return jobs


def append_to_csv(data):
    '''
    保存数据
    '''
    file_name = './招聘信息.csv'
    df = pd.DataFrame(data)
    df.to_csv(file_name, mode='a', encoding='utf_8_sig', header=False, index=False)


def main():
    for i in range(1, 2001):
        # 一共 2000 页招聘信息
        url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,数据分析,2,{}.html'.format(i)
        cached_url(url)
        jobs = jobs_from_url(url)
        print(jobs)
        append_to_csv(jobs)  # 保存招聘信息


if __name__ == '__main__':
    main()
