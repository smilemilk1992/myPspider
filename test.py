import json
from xml.dom.minidom import parse
import xmltodict
def TT():
    xmldoc1 = parse("my1.xml")
    text = json.dumps(xmltodict.parse(xmldoc1.toxml()), indent=4)
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

    temp1 = {}
    for i in list1[1:]:
        for k, v in i.items():
            data1 = []
            if k == 'contour':
                if type(v) == dict:
                    for iiii in v.get('pt'):
                        data1.append(iiii)
                else:
                    for iiii in v:
                        for iiii in iiii.get('pt'):
                            data1.append(iiii)
                temp1[i['@name']] = data1

    data2 = {}
    j=["5","1","6","2","7","0","4","9","3","8"]
    numb=0
    for k, v in ysbm.items():
        data2[j[numb]] = temp1[k]
        numb=numb+1
    print("====",data2)
    return data2

def th1(xmldoc1):
    xmldoc = parse(xmldoc1)
    text = json.dumps(xmltodict.parse(xmldoc.toxml()), indent=4)
    text_json = json.loads(text)
    print(json.dumps(text_json))
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
    print("list",list1)
    print(ysbm)
    temp1={}
    for i in list1[1:]:
        for k, v in i.items():
            data1=[]
            if k == 'contour':
                if type(v)==dict:
                    for iiii in v.get('pt'):
                        data1.append(iiii)
                else:
                    for iiii in v:
                        for jjjj in iiii.get('pt'):
                            data1.append(jjjj)
                temp1[i['@name']]=data1
    data2={}
    for k,v in ysbm.items():
        data2[v]=temp1[k]
    print("========",json.dumps(data2))
    return data2
x1=TT()
x2=th1("tt.xml")

data={}
for k,v in x2.items():
    aa=[x["@on"] for x in v]
    print(aa)
    for i in v:
        for k1,v1 in x1.items():
            bb = [y["@on"] for y in v1]
            # print("===", bb)
            if aa==bb or len(set(aa))==len(set(bb))==1: #防止出现相同
                # print("===",aa)
                data[k] = k1
                break
            if aa[:len(bb)]== bb or bb[:len(aa)] == aa:#防止出现子集
                data[k] = k1
                break
            for ii in v1:
                if i==ii:
                    data[k]=k1
                    break

print(data)
