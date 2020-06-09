import requests
from bs4 import BeautifulSoup
import re
from Util import htmlFilter
import time
from faker import Faker

f=Faker()

font_size = 14
start_y = 23
heard={
    'User-Agent': f.firefox(),
    'Cookie': 's_ViewType=10; _lxsdk_cuid=16ea11c8431c8-0046e2d1e0e96a-2393f61-100200-16ea11c8433c8; _lxsdk=16ea11c8431c8-0046e2d1e0e96a-2393f61-100200-16ea11c8433c8; _hc.v=dd5a298b-2260-8d93-ce47-9695be84968f.1574661031; ctu=e7a9e6da10443310ad7c3c9e9e3ee21f692f377118c84c4642124a63f73e0957; ua=smilemilk; cy=2; cye=beijing; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1591693148; lgtoken=05dd729b3-b4f5-4ecc-b297-ee4afc1b1701; dplet=e38895d9069a72a2f942fcc4628cc8d1; dper=00e58557a1d538cede3f9b62381f48d961cadf03b06090643443659d1fea5fadc68b07f3a3eea488c91f587fac98ea54926a50f3312797199bd7583ce29f9838daf4771cd377721e1e99209eb45cccd50cdd0c3f7460f43e0cb0fa8a6bb1929f; ll=7fd06e815b796be3df069dec7836c3df; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1591693188; _lxsdk_s=172984df175-bfb-ac6-8de%7C%7C316',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}
def getCss(url):
    rs=requests.get(url,headers=heard)
    css="http:"+re.search("//s3plus.meituan.net/v1/.*?\.css",rs.text).group(0)
    return css

def getSvg(url):
    css = getCss(url)
    print(css)
    rs=requests.get(css)
    svg="http:"+re.search("width: 14px;height: 24px.*?url\((.*?)\)",rs.text).group(1)
    return svg

def getSvgDict(url):
    font_dict = {}
    svg=getSvg(url)
    html=requests.get(svg).text
    font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)
    if font_list:
        for y,string in font_list:
            y_offset=start_y-int(y)
            for j,font in enumerate(string):
                x_offset=-j*font_size
                font_dict[(x_offset,y_offset)]=font
    else:
        ids = re.findall('d="M0 (\d+)', html)
        strings = re.findall('<textPath.*?>(.*?)</textPath>', html)
        for i, s in enumerate(strings):
            y_offset = start_y - int(ids[i])
            for j, font in enumerate(s):
                x_offset = -j * font_size
                font_dict[(x_offset, y_offset)] = font
    print(font_dict)
    return font_dict



def getFontDict(url):
    font_dict = {}
    svgDict=getSvgDict(url)
    css=getCss(url)
    rs=requests.get(css).text
    group_offset_list=re.findall(r'}\.(.*?){background:(.*?)px (.*?)px;', rs)
    for class_name, x_offset, y_offset in group_offset_list:
        x_offset = x_offset.replace('.0', '')
        y_offset = y_offset.replace('.0', '')
        font_dict[class_name]=svgDict.get((int(x_offset),int(y_offset)))
    return font_dict

def getContent(url):
    font_dict=getFontDict(url)
    rs=requests.get(url,headers=heard)
    soup=BeautifulSoup(rs.text,"lxml")
    lis=soup.find_all(attrs={"class":re.compile("review-words")})
    i=0
    for li in lis:
        i=i+1
        ct = re.split('"></svgmtsi><svgmtsi class="|"></svgmtsi><svgmtsi class="|<svgmtsi class="|"></svgmtsi>|<div class="review-words.*?">', str(li))
        ct = [x.strip().replace("\n", "") for x in ct if x.strip().replace("\n", "")]
        st=""
        for c in ct:
            if c in font_dict.keys():
                st=st+font_dict[c]
            else:
                st=st+c
        result=htmlFilter.filters(st)
        print(str(i)+"、"+result)
        with open("dzdp_comments.txt",'a',encoding="utf-8") as f:
            f.write(result+"\n")
        # print(st)

if __name__ == '__main__':
    for i in range(1,115):
        print("~~~~~~~~~~~~~第{}页~~~~~~~~~~~~~~~~~".format(i))
        time.sleep(10)
        getContent("http://www.dianping.com/shop/98408264/review_all/p{}".format(i))