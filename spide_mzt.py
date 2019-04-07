import requests
import time
from lxml import etree
import os
from concurrent import futures

url_base='https://www.mzitu.com/'
url=url_base
file_saved_dir='D:/迅雷下载/imgs_mm/{}/'

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
'Referer':'https://www.mzitu.com/'}

#下载图片函数
def download_img(src,dirname):
    filename=src.split('/')[-1:]
    dirnames=file_saved_dir.format(dirname)
    if not os.path.exists(dirnames):
        os.makedirs(dirnames)
    img_mm=requests.get(src,headers=headers)
    with open(dirnames+filename[0],'wb') as file:
        file.write(img_mm.content)

#解析子网页，实现下载和翻页
def get_page_2(url,dirname):
    resp_href=requests.get(url,headers=headers)
    print(resp_href,url)
    html_href=etree.HTML(resp_href.text)
    srcs=html_href.xpath('.//div[@class="content"]/div/p/a/img/@src')
    #多线程方案
    ex=futures.ThreadPoolExecutor(max_workers=20)
    for src in srcs:
        ex.submit(download_img,src,dirname)
    '''
    单线程方案
    for src in srcs:
        download_img(src,dirname)
    '''
    marks=html_href.xpath('.//div[@class="pagenavi"]/a/span')
    if marks[-1].text=="下一页»":
        next_link_2=html_href.xpath('.//div[@class="content"]/div/p/a/@href')
    else:
        next_link_2=[]    
    return next_link_2

#解析主网页，实现翻页
def get_page_1(url):
    resp_1=requests.get(url,headers=headers)
    print(resp_1,url)
    html_1=etree.HTML(resp_1.text)
    hrefs_1=html_1.xpath('//*[@id="pins"]/li/a/@href')
    #爬取主页第一页
    for href_1 in hrefs_1:
        loc_num=href_1.split('/')[-1]
        resp_2=requests.get(href_1,headers=headers)
        html_2=etree.HTML(resp_2.text)
        srcs_2=html_2.xpath('.//div[@class="content"]/div/p/a/img/@src')
        for src_2 in srcs_2:
            download_img(src_2,loc_num)
        #子页翻页
        next_link_base_2=url_base + loc_num + '/'
        next_link_2=html_2.xpath('.//div[@class="content"]/div/p/a/@href')
        current_num=1
        while next_link_2:
            time.sleep(0.05)
            current_num=current_num+1
            next_link_2=get_page_2(next_link_base_2+str(current_num),loc_num)
    #主页翻页
    next_link_1=html_1.xpath('.//a[@class="next page-numbers"]/@href')
    return next_link_1

#主函数
def main(): 
    resp_1=requests.get(url,headers=headers) #拿到第一页响应数据
    #解析主页图片链接
    html_1=etree.HTML(resp_1.text)
    hrefs_1=html_1.xpath('//*[@id="pins"]/li/a/@href')
    #爬取主页第一页
    for href_1 in hrefs_1:
        loc_num=href_1.split('/')[-1]
        resp_2=requests.get(href_1,headers=headers)
        html_2=etree.HTML(resp_2.text)
        srcs_2=html_2.xpath('.//div[@class="content"]/div/p/a/img/@src')
        for src_2 in srcs_2:
            download_img(src_2,loc_num)
        #子页翻页
        next_link_base_2=url_base + loc_num + '/'
        next_link_2=html_2.xpath('.//div[@class="content"]/div/p/a/@href')
        current_num=1
        while next_link_2:
            time.sleep(0.05)
            current_num=current_num+1
            next_link_2=get_page_2(next_link_base_2+str(current_num),loc_num)
    #主页翻页
    next_link_base_1=url_base+'page/'
    next_link_1=html_1.xpath('.//a[@class="next page-numbers"]/@href')
    page_num=1
    while next_link_1:
        time.sleep(0.5)
        page_num=page_num+1
        next_link_1=get_page_1(next_link_base_1+str(page_num)+'/')

if __name__=="__main__":
    main()