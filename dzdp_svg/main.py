import requests
from bs4 import BeautifulSoup
import re
font_size = 14
start_y = 23
heard={
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
    'Cookie': '_lxsdk_cuid=16ea7ff0adcc8-0d1067849a6dba-3963720f-13c680-16ea7ff0adcb0; _lxsdk=16ea7ff0adcc8-0d1067849a6dba-3963720f-13c680-16ea7ff0adcb0; _hc.v=4878cd03-04cb-0b3c-d4b4-805f9c1b034b.1574776541; ctu=33e63b010c1df6f33e3453754299bdc73ec1478bd1f9ebb0702492eae3e72ec0; s_ViewType=10; _dp.ac.v=d404491d-8772-45dc-80d2-5f5ac17a9825; ua=smilemilk; cy=2; cye=beijing; _lxsdk_s=1709a6181b4-678-8b7-6da%7C%7C41',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}
def getCss(url):
    rs=requests.get(url,headers=heard)
    css="http:"+re.search("//s3plus.sankuai.com/v1/.*?\.css",rs.text).group(0)
    return css

def getSvg(url):
    css = getCss(url)
    rs=requests.get(css)
    svg="http:"+re.search("width: 14px;height: 24px.*?url\((.*?)\)",rs.text).group(1)
    return svg

def getSvgDict(url):
    font_dict = {}
    svg=getSvg(url)
    html=requests.get(svg).text
    font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)
    for y,string in font_list:
        y_offset=start_y-int(y)
        for j,font in enumerate(string):
            x_offset=-j*font_size
            font_dict[(x_offset,y_offset)]=font
    return font_dict



def getFontDict(url):
    font_dict = {}
    svgDict=getSvgDict(url)
    css=getCss(url)
    rs=requests.get(css).text
    group_offset_list=re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', rs)
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
    for li in lis:
        ct = re.split('"></svgmtsi><svgmtsi class="|"></svgmtsi><svgmtsi class="|<svgmtsi class="|"></svgmtsi>|<div class="review-words.*?">', str(li))
        ct = [x.strip().replace("\n", "") for x in ct if x.strip().replace("\n", "")]
        st=""
        for c in ct:
            if c in font_dict.keys():
                st=st+font_dict[c]
            else:
                st=st+c
        print(st)

if __name__ == '__main__':
    getContent("http://www.dianping.com/shop/4208148/review_all")