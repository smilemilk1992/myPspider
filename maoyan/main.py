#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
import json
from xml.dom.minidom import parse
import xmltodict
from fontTools.ttLib import TTFont
import requests
import re
from bs4 import BeautifulSoup

heard={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Cookie":"__mta=149208329.1602057328429.1602057805335.1602058231797.6; uuid_n_v=v1; uuid=719A1770087211EBA1A7D5F8AE217AFCA0E7263D83264BD99B5395B2A7753889; _csrf=fc979134b15c6dbb096cb6a9ecef7f88eef22186f3d990c0226beeeaccd08142; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=175020ecd114-03d9ff5eee2f3c-333376b-100200-175020ecd12c8; _lxsdk=719A1770087211EBA1A7D5F8AE217AFCA0E7263D83264BD99B5395B2A7753889; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1602057328; __mta=149208329.1602057328429.1602057344929.1602057347977.4; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1602058231; _lxsdk_s=175020ecd13-85a-317-79b%7C%7C16"
}

def mapping(xmlFile=None):
    if xmlFile is None:
        xmlFile="my1.xml"
    xmldoc = parse(xmlFile)
    text = json.dumps(xmltodict.parse(xmldoc.toxml()), indent=4) #xml 转json
    text_json = json.loads(text)
    list = []
    list1 = []
    for k, v in text_json.get('ttFont').items():
        if k == 'cmap':
            list = v.get('cmap_format_4')
        if k == 'glyf':
            list1 = v.get('TTGlyph')

    ysbm = {}
    for i in list:
        if i['@platEncID'] == '3':
            for ii in i['map'][1:]:
                ysbm[ii['@name']] = ii['@code'][1:]
    temp1={}
    for i in list1[1:]:
        for k, v in i.items():
            ybm = ''
            data1=[]
            if k == 'contour':
                if type(v)==dict:
                    for ii in v.get('pt'):
                        ybm = ybm+json.dumps(ii)
                        data1.append(ii)
                else:
                    for ii in v:
                        for ii in ii.get('pt'):
                            ybm = ybm+json.dumps(ii)
                            data1.append(ii)
                temp1[i['@name']]=data1

    data2={}
    j = ["5", "1", "6", "2", "7", "0", "4", "9", "3", "8"]
    if xmlFile=="my1.xml": #已知映射关系
        numb = 0
        for k, v in ysbm.items():
            data2[j[numb]] = temp1[k]
            numb = numb + 1
    else:
        for k,v in ysbm.items():
            data2[v]=temp1[k]
    return data2

def mapRelation(s,ss):
    '''
    :param s: 目标文件映射关系
    :param ss:  已知映射关系
    :return: 新的映射关系
    '''
    data={}
    for k,v in s.items():
        aa = [x["@on"] for x in v]
        for i in v:
            for k1,v1 in ss.items():
                bb = [y["@on"] for y in v1]
                # if aa == bb or len(set(aa))==len(set(bb))==1: #防止出现相同
                #     data[k] = k1
                #     break
                # if aa[:len(bb)] == bb or bb[:len(aa)] == aa:  # 防止出现子集
                #     data[k] = k1
                #     break
                # c = []
                # for ii, a in enumerate(aa):
                #     for jj, b in enumerate(bb):
                #         if ii == jj and a != b:
                #             c.append(1)
                # if len(c) <= 1:
                #     data[k] = k1
                #     break
                if len(aa) % 2 == 0:
                    aaS = aa[:(len(aa) // 2) - 1]
                    aaE = aa[(len(aa) // 2) + 1:]
                else:
                    aaS = aa[:len(aa) // 2]
                    aaE = aa[(len(aa) // 2) + 1:]
                if len(bb) % 2 == 0:
                    bbS = bb[:(len(bb) // 2) - 1]
                    bbE = bb[(len(bb) // 2) + 1:]
                else:
                    bbS = bb[:len(bb) // 2]
                    bbE = bb[(len(bb) // 2) + 1:]
                if aaE == bbE or aaS == bbS:
                    data[k] = k1
                    break
                for ii in v1:
                    if i==ii:
                        data[k]=k1
                        break
    return data

def getContent(url):
    html = requests.get(url, headers=heard).text
    # woff=html[html.find("embedded-opentype")+39:html.find("'woff'")-10]
    # wofflink = 'http://' + woff
    # wofflink="http://vfile.meituan.net/colorstone/66a0b32ae3f15c63dc89d4868f61d22e2284.woff"
    woff = re.search("//vfile.*?\.woff",html).group(0)
    wofflink = 'http:' + woff
    print(wofflink)
    r = requests.get(wofflink, headers=heard)
    with open('../maoyan/tt.woff', "wb") as f:
        f.write(r.content)
    f.close()
    font1 = TTFont('tt.woff')  # 读取woff文件
    font1.saveXML('tt.xml')  # 转成xml
    data=mapRelation(mapping('tt.xml'),mapping())
    for k ,v in data.items():
        # print(k,v)
        html=html.replace("&#"+k+";",v)
    print(data.items())
    htmltxet = BeautifulSoup(html, "html.parser")
    title=htmltxet.find("h1",attrs={"class":"name"}).text.strip()
    type=" ".join([x.get_text().strip() for x in htmltxet.find_all("a",attrs={"class":"text-link"})])
    shany = htmltxet.find_all("li", attrs={"class": "ellipsis"})[1].text.strip().replace("\n","").replace(" ","").split("/")
    dalu = htmltxet.find_all("li", attrs={"class": "ellipsis"})[2].text.strip().replace("大陆上映","")
    scoreNum=htmltxet.find("span",attrs={"class":"score-num"}).get_text().strip().replace("人评分","")
    source=shany[0]
    time=shany[1]
    print("标题："+title)
    print("类型："+type)
    print("来源："+source)
    print("时长："+time)
    print("评分人数："+scoreNum)
    print("上映时间："+dalu)
    if htmltxet.find("span", attrs={"class": "stonefont"}) != None:
        pingfen = htmltxet.find("span", attrs={"class": "stonefont"}).text
    else:
        pingfen = '暂无'
    if htmltxet.find("div",attrs={"class":"movie-index-content box"}) != None:
        bofang=htmltxet.find("div",attrs={"class":"movie-index-content box"}).text
    else:
        bofang = '暂无'
    print("票房：",pingfen.strip())
    print("播放量：",bofang.strip())


if __name__ == '__main__':
    # while True:
        getContent("https://maoyan.com/films/1277939")
    # pass



