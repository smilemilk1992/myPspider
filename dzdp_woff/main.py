import requests
import json
import re
from xml.dom.minidom import parse
import xmltodict
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup
heard={
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
    'Cookie': '_lxsdk_cuid=16ea7ff0adcc8-0d1067849a6dba-3963720f-13c680-16ea7ff0adcb0; _lxsdk=16ea7ff0adcc8-0d1067849a6dba-3963720f-13c680-16ea7ff0adcb0; _hc.v=4878cd03-04cb-0b3c-d4b4-805f9c1b034b.1574776541; ctu=33e63b010c1df6f33e3453754299bdc73ec1478bd1f9ebb0702492eae3e72ec0; s_ViewType=10; _dp.ac.v=d404491d-8772-45dc-80d2-5f5ac17a9825; ua=smilemilk; cy=2; cye=beijing; _lxsdk_s=1709a6181b4-678-8b7-6da%7C%7C41',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}
#获取已知字体字典
def getDict():
    with open('../dzdp_woff/jsonFile', "r",encoding='utf8') as f:
        json_data = json.load(f)
        return json_data

#获取数字woff
def getNumWoff(url):
    rs = requests.get(url, headers=heard)
    # print(rs.text)
    css = "http:" + re.search("//s3plus.meituan.net/v1/mss_.*?\.css", rs.text).group(0)
    rss=requests.get(css)
    numWoff="http:"+re.search('PingFangSC-Regular-shopNum.*?format\("embedded-opentype"\),url\("(.*?)"\);} \.shopNum',rss.text).group(1)
    return numWoff

#获取地址woff
def getAddrWoff(url):
    rs = requests.get(url, headers=heard)
    css = "http:" + re.search("//s3plus.meituan.net/v1/mss_.*?\.css", rs.text).group(0)
    rss=requests.get(css)
    numWoff="http:"+re.search('PingFangSC-Regular-address.*?format\("embedded-opentype"\),url\("(.*?)"\);} \.address',rss.text).group(1)
    return numWoff

#获取数字mapping关系
def getNumMapping(url):
    res={}
    json_data=getDict()
    woff = getNumWoff(url)
    rs=requests.get(woff)
    with open('../dzdp_woff/numTest.woff', "wb") as f:
        f.write(rs.content)
    f.close()
    font = TTFont('numTest.woff')  # 读取woff文件
    font.saveXML('numTest.xml')  # 转成xml
    result = font['cmap']
    cmap_dict = result.getBestCmap()
    for key, value in cmap_dict.items():
        k_tmp = str(hex(eval(str(key))))
        b = k_tmp.replace("0x", '')
        glyf = font.get('glyf')
        c = glyf[value]
        coordinates=str(c.coordinates)
        for data in json_data:
            position=data["position"]
            if position==coordinates and data["word"] in ['0','1','2','3','4','5','6','7','8','9']:
                res[value.replace("uni","&#x")]=data["word"]
    print("getNumMapping", res)
    return res

#获取地址mapping关系
def getAddrMapping(url):
    res = {}
    json_data = getDict()
    woff = getAddrWoff(url)
    rs = requests.get(woff)
    with open('../dzdp_woff/addrTest.woff', "wb") as f:
        f.write(rs.content)
    f.close()
    font = TTFont('addrTest.woff')  # 读取woff文件
    font.saveXML('addrTest.xml')  # 转成xml
    result = font['cmap']
    cmap_dict = result.getBestCmap()
    for key, value in cmap_dict.items():
        k_tmp = str(hex(eval(str(key))))
        b = k_tmp.replace("0x", '')
        glyf = font.get('glyf')
        c = glyf[value]
        coordinates = str(c.coordinates)
        for data in json_data:
            position = data["position"]
            if position == coordinates and data["word"] not in ['','0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                res[value.replace("uni", "&#x")] = data["word"]
    print("getAddrMapping",res)
    return res

def getContent(url):
    numdata=getNumMapping(url)
    addrdata=dict(getAddrMapping(url))
    addrdata.update(numdata)
    html=requests.get(url,headers=heard).text
    print(html)
    for k, v in addrdata.items():
        html = html.replace(k+";", v)
    soup = BeautifulSoup(html, "lxml")
    shopAll=soup.find("div",{"id":"shop-all-list"}).find_all("div",{"class":"txt"})
    for shop in shopAll:
        title=shop.find("h4").get_text()
        score=shop.find(attrs=re.compile("star_score score_")).get_text()
        plNum = shop.find("a", {"class": "review-num"}).find("b").get_text()
        pice = shop.find("a",{"class":"mean-price"}).find("b").get_text()
        addr=shop.find("span",{"class":"addr"}).get_text()
        spans=shop.find("span",{"class":"comment-list"}).find_all("span")
        taste=spans[0].get_text().replace("口味","")
        environment=spans[1].get_text().replace("环境","")
        serve=spans[2].get_text().replace("服务","")
        print("店名："+title)
        print("评分："+score)
        print("评论人数："+plNum)
        print("人均："+pice)
        print("地址："+addr)
        print("口味："+taste)
        print("环境："+environment)
        print("服务："+serve)
        print("------------")

if __name__ == '__main__':
    getContent("http://www.dianping.com/shenzhen/ch10/r6013m5")
