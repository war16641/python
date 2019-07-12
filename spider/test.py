import requests  # 导入requests包
import json



# url = 'http://www.cntour.cn/'
# strhtml = requests.get(url)  # Get方式获取网页数据
# print(strhtml.text)
def get_translate(word=None):
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
    dic = {'i': '我爱中国',
           'from': 'AUTO',
           'to': 'AUTIO',
           'smartresult': 'dict',
           'client': 'fanyideskweb',
           'salt': '15628944275134',
           'sign': 'a0b138d0d8633b654f96d3694c7459a9',
           'ts': '1562894427513',
           'bv': 'e2a78ed30c66e16a857c5b6486a1d326',
           'doctype': 'json',
           'version': '2.1',
           'keyfrom': 'fanyi.web',
           'action': 'FY_BY_REALTlME'
           }
    # 请求表单数据
    response = requests.post(url, data=dic)
    # 将Json格式字符串转字典
    content = json.loads(response.text)
    print(content)
    # 打印翻译后的数据
    # print(content['translateResult'][0][0]['tgt'])

def get_translate_date(word=None):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    From_data={'i':word,'from':'zh-CHS','to':'en','smartresult':'dict','client':'fanyideskweb','salt':'15477056211258','sign':'b3589f32c38bc9e3876a570b8a992604','ts':'1547705621125','bv':'b33a2f3f9d09bde064c9275bcb33d94e','doctype':'json','version':'2.1','keyfrom':'fanyi.web','action':'FY_BY_REALTIME','typoResult':'false'}
    #请求表单数据
    response = requests.post(url,data=From_data)
    #将Json格式字符串转字典
    content = json.loads(response.text)
    print(content)
    #打印翻译后的数据
    #print(content['translateResult'][0][0]['tgt'])
if __name__ == '__main__':
    get_translate('我爱中国')

