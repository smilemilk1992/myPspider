import requests
import json
import re
from xml.dom.minidom import parse
import xmltodict
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup
heard={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',

}

def mapping(xmlFile=None):
    if xmlFile is None:
        xmlFile="auto.xml"
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
            for ii in i['map']:
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
    j = ['三', '十', '坏', '九', '六', '远', '近', '大', '右', '长', '二', '下', '小', '是', '一', '八', '了', '左', '七', '和', '上', '得', '不', '好', '少', '五', '的', '低', '更', '矮', '着', '多', '短', '地', '呢', '四', '高', '很']

    if xmlFile=="auto.xml": #已知映射关系
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
    html = requests.get(url,headers=heard).text
    ttf = re.search("format\('embedded-opentype'\),url\('(//k3.autoimg.cn/g1/.*?\.ttf)",html).group(1)

    ttflink = 'http:' + ttf
    r = requests.get(ttflink)
    with open('../autoHome/auto1.ttf', "wb") as f:
        f.write(r.content)
    f.close()
    font1 = TTFont('auto1.ttf')  # 读取woff文件
    font1.saveXML('auto1.xml')  # 转成xml
    data = mapRelation(mapping('auto1.xml'), mapping())
    for k, v in data.items():
        html = html.replace("&#" + k + ";", v)

    htmltxet = BeautifulSoup(html, "html.parser")
    contents=htmltxet.find_all("div",{"class":"clearfix contstxt outer-section"})
    for c in contents[1:]:
        ct=c.find("div",{"class":"x-reply font14"}).get_text().strip()
        if "本楼已被删除" not in ct:
            pubTime=c.find("span",{"xname":"date"}).get_text().strip()
            print("评论："+ct)
            print("发布时间："+pubTime)
            print("=======")



if __name__ == '__main__':
    getContent("https://club.autohome.com.cn/bbs/thread/1f05b4da4448439b/76044817-2.html")



#     dict=["的","是","上","近","小","高","不","着","八","十","右","短","三","少",
#           "二","七","九","更","呢","得","低","一","很","大","多","左","好","长",
#           "了","坏","五","地","和","远","下","四","六","矮"]
#     uniDict=["uniED79","uniECC6","uniED18","uniEC64","uniECB6","uniEDF7","uniED43","uniED95","uniECE2","uniEC2E",
#              "uniEC80","uniEDC1","uniEC1F","uniED5F","uniECAC","uniECFE","uniEC4A","uniED8B","uniEDDD","uniED29","uniED7B",
#              "uniECC8","uniEE08","uniEC66","uniEDA7","uniECF3","uniED45","uniEC92","uniECE4","uniEC30","uniED71",
#              "uniEDC3","uniED0F","uniEC5C","uniECAE","uniEDEE","uniEC4C","uniED8D"]
