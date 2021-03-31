from __future__ import unicode_literals

import argparse
import json
import requests
import base64
import os.path as osp


def convert_b64(file):
    if osp.isfile(file):
        with open(file, 'rb') as fh:
            x = base64.b64encode(fh.read())
            return x.decode('ascii').replace('\n', '')
    else:
        return None


def post(url, host, port, json=None, timeout=10000):
    url = 'http://%s:%d%s' % (host, port, url)
    r = requests.post(url=url, json=json, timeout=timeout)
    #print(r.status_code)
    return r

def postfile(file):
    url = "/lab/ocr/predict/general"
    host = "ocr.4paradigm.com"
    port = 80
    data = {
        "scene": "chinese_print",
        "image": convert_b64(file)
    }
    return post(url, host, port, data)

def gettext(r):
    #print(r)
    dataresult=json.dumps(r.json(), ensure_ascii=False, indent=2)
    datadict=json.loads(dataresult)
    return datadict["data"]["result"][0]["data"]

def getbox(r):
    dataresult=json.dumps(r.json(), ensure_ascii=False, indent=2)
    datadict=json.loads(dataresult)
    return datadict["data"]["json"]["general_ocr_res"]["bboxes"]

def strategy_index_add0(i):
    #值为本身
    return i

def strategy_index_add1(i):
    return i+1

def strategy_compare_full(var1, var2):
    return var1 == var2

def strategy_compare_part(var1, var2):
    return var1 in var2

def strategy_merge_self(var1, var2):
    return var2

def strategy_merge_direct(var1, var2):
    return var1+var2

def postprocess(var, *args):
    return var

def postproess_1(var, *args):
    #“甲方(卖方)”
    return var.replace('::', ':')

def postprocess_substring(var, varlist):
    #print(varlist)
    index_start = var.index(varlist[0][0])
    index_end = var.index(varlist[0][1])
    result = var[index_start:(index_end + len(varlist[0][1]))]
    return result

def find_element_name(element_value, text, strategy_index, strategy_compare, strategy_merge, postprocess=postprocess, *args):
    for i in range(len(text)):
        if strategy_compare(element_value, text[i]["element_value"]):
            #print("key:", element_value)
            result = postprocess(strategy_merge(text[i]["element_value"], text[strategy_index(i)]["element_value"]), args)
            print(result)
            return (result)

def find_list_element_name(element_value, text, strategy_index, strategy_compare, strategy_merge, postprocess=postprocess, *args):
    j = 0
    for i in range(len(text)):
        if strategy_compare(element_value, text[i]["element_value"]):
            #print("key:", element_value)
            j = j + 1
            if j == 4:
                result = postprocess(strategy_merge(text[i]["element_value"], text[strategy_index(i)]["element_value"]), args)
                print(result)
                return (result)

'''--------------------------------------------------------------'''


def testhetong(file):
    r = postfile(file)
    text = gettext(r)
    box = getbox(r)
    #print(text)
    #print(box)
    #print("-----------")
    
    
    find_element_name("合同编号:", text, strategy_index_add1, strategy_compare_full, strategy_merge_direct)
    find_element_name("甲方(卖方):", text, strategy_index_add1, strategy_compare_full, strategy_merge_direct, postproess_1)
    find_element_name("乙方 (买方)", text, strategy_index_add0, strategy_compare_part, strategy_merge_self)
    find_element_name("证件类型:", text, strategy_index_add1, strategy_compare_full, strategy_merge_direct)
    find_element_name("号码:", text, strategy_index_add1, strategy_compare_full, strategy_merge_direct)
    find_list_element_name("联系电话:", text, strategy_index_add1, strategy_compare_full, strategy_merge_direct)
    find_element_name("本商品房项目:", text, strategy_index_add0, strategy_compare_part, strategy_merge_self)
    find_element_name("本商品房座落为", text, strategy_index_add0, strategy_compare_part, strategy_merge_self)
    find_element_name("本商品房建筑面积", text, strategy_index_add1, strategy_compare_part, strategy_merge_direct, postprocess_substring, ["本商品房建筑面积", "平方米"])
    find_element_name("总成交金额为", text, strategy_index_add0, strategy_compare_part, strategy_merge_self, postprocess_substring, ["总成交金额为", "元整"]) 
    find_element_name("本商品房为清水房", text, strategy_index_add1, strategy_compare_part, strategy_merge_direct, postprocess_substring, ["建筑面积单价", "平方米"])
    find_element_name("本商品房总成交金额", text, strategy_index_add0, strategy_compare_part, strategy_merge_self, postprocess_substring, ["本商品房总成交", "元整"])

    open('test.json', 'w').write(json.dumps(r.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='input image file', type=str, default=None)
    args = parser.parse_args()

    if args.file is None:
        exit(1)

    testhetong(args.file)
