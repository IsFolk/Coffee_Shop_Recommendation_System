from django.shortcuts import render
from rest_framework import viewsets
from .models import Store_labels
from .models import Review_tokens
from .serializers import YourModelSerializer
from django.http import JsonResponse

import pandas as pd
import csv
import json
import re
from ckiptagger import WS, POS, NER, construct_dictionary
import gensim
from gensim.models.word2vec import Word2Vec
import numpy as np


import pandas as pd
import re
from snownlp import SnowNLP
import jieba
from collections import Counter

from django_pandas.io import read_frame


# Create your views here.
def index(request):
    obj = Store_labels.objects.all()
    context = {
        "obj": obj
    }
    return render(request, "index.html", context)

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = Store_labels.objects.all()
    serializer_class = YourModelSerializer


def call_store_labels():
    # 使用包含指定字串的數據
    # data_from_db = Store_labels.objects.filter(CafeLabel__icontains=search_string)  # 替換成實際的字段名稱
    data_from_db = Store_labels.objects.all()  # 替換成實際的字段名稱
    data_list = [{'link': item.link.lstrip('\ufeff'), 'id': item.id,'name': item.name, 'time': item.time,\
                  'address': item.address, 'phone': item.phone, 'img': item.img,\
                    'website': item.website, 'star': item.star, 'review_num': item.review_num,\
                        'labels': item.labels} for item in data_from_db]  # 替換成實際的字段名稱
    
    
    return {'data': data_list}

def call_tokens():
    data_from_db = Review_tokens.objects.all()
    data_list = [{'link':item.link.lstrip('\ufeff'), 'review': item.review, 'time': item.review_time, 'id': item.Cafeid, 'name': item.name, \
                  'review_tokenization': item.review_tokenization} for item in data_from_db]
    return {'data': data_list}

# 先都算好
store_labels_df = pd.DataFrame(call_store_labels()['data'])
review_tokenization_df = pd.DataFrame(call_tokens()['data'])
labels_list = []
labels_dict = {}
with open(r"D:\User\user\Desktop\台大\112-1\IR\Final\Web\backend\Django\DjangoAPI\Cafeapp\Query_data\cafe_keyword_v2.csv", 'r', encoding = 'utf-8-sig') as file:
    csvreader = csv.reader(file)
    headings = next(csvreader)
    for row in csvreader:
        row_filter = [t for t in row if t != '']
        labels_list.append(row_filter)
        for label in row_filter:
            labels_dict[label] = 1
ws = WS(r"D:\User\user\Desktop\台大\112-1\IR\Final\Web\backend\Django\DjangoAPI\Cafeapp\data")
ckip_dict = construct_dictionary(labels_dict)

corpus = []
ckip_results = review_tokenization_df['review_tokenization']
for c in range(len(ckip_results)):
    corpus.append(ckip_results[c][2:-2].replace("'", "").split(", "))
model = Word2Vec(corpus)

# 最重要的
def query_word2vec(request, q):
    reg = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    q_pre = reg.sub('', q)
    queries = ws([q_pre], coerce_dictionary = ckip_dict)
    q_flag = [False] * len(queries[0])
    
    if len(queries[0]) > 1:
        for q in range(len(queries[0])):
            for labels in labels_list:
                if queries[0][q] in labels:
                    q_flag[q] = True
                    break
    
    weights = [1 / len(q_flag)] * len(q_flag)
    t_num = 0
    f_num = 0
    for q in q_flag:
        if q == True:
            t_num += 1
        else:
            f_num += 1
    if t_num != 0 and f_num != 0:
        for q in range(len(q_flag)):
            if q_flag[q]:
                weights[q] = 0.8 / t_num
            else:
                weights[q] = 0.2 / f_num
    
    sims = {}
    for labels in labels_list:
        for qr in range(len(queries[0])):
            if queries[0][qr] not in model.wv.index_to_key:
                continue
            for label in labels:
                if label not in model.wv.index_to_key:
                    continue
                sim = model.wv.similarity(queries[0][qr], label)
                if sims.get(labels[0]) == None:
                    sims[labels[0]] = sim * weights[qr]
                else:
                    sims[labels[0]] += sim * weights[qr]
                break
    if len(sims) == 0:
        print('Your query is not in model!')

    sims = {k: v for k, v in sorted(sims.items(), key = lambda item: item[1], reverse = True)}
    top_labels = list(sims.keys())[0:3]
    scores = {}
    results_dict = {"query_label": top_labels, "stores": []}
    
    for i in range(len(store_labels_df)):
        rating = store_labels_df.iloc[i]['star']
        scores[i] = rating / 5 * 0.2
        for l in range(len(top_labels)):
            store_labels = store_labels_df.iloc[i]['labels'].replace("'", '"')
            store_labels = json.loads(store_labels)
            if top_labels[l] in store_labels.keys():
                score = store_labels[top_labels[l]]
                if l == 0:
                    scores[i] += score * 0.6
                else:
                    scores[i] += score * 0.1
                    
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse = True)}
    attr = list(store_labels_df.columns)
    top_num = 0
    for i in scores.keys():
        
        if top_num == 10:
            break
            
        result = {}
        result["link"] = store_labels_df.iloc[i]['link']
        result["id"] = int(store_labels_df.iloc[i]['id'])
        result["name"] = store_labels_df.iloc[i]['name']
        result["time"] = store_labels_df.iloc[i]['time']
        result["address"] = store_labels_df.iloc[i]['address']
        result["phone"] = store_labels_df.iloc[i]['phone']
        result["img"] = store_labels_df.iloc[i]['img']
        result["website"] = store_labels_df.iloc[i]['website']
        result["star"] = float(store_labels_df.iloc[i]['star'])
        result["review_num"] = int(store_labels_df.iloc[i]['review_num'])
        
        top_labels_i = store_labels_df.iloc[i]['labels'].replace("'", '"')
        top_labels_i = json.loads(top_labels_i)
        top_labels_i = {k: v for k, v in sorted(top_labels_i.items(), key = lambda item: item[1], reverse = True)}
        top_labels_i = list(top_labels_i.keys())[0:3]
        result['labels'] = top_labels_i
        
        top_num += 1
        results_dict["stores"].append(result)

    return JsonResponse(results_dict)










# 情感分析










# infoDF 跟 store_labels只差一個label欄位
def call_infoDF():
    data_from_db = Store_labels.objects.all()  # 替換成實際的字段名稱
    data_list = [{'link': item.link.lstrip('\ufeff'), 'id': item.id,'name': item.name, 'time': item.time,\
                  'address': item.address, 'phone': item.phone, 'img': item.img,\
                    'website': item.website, 'star': item.star, 'review_num': item.review_num } for item in data_from_db]  # 替換成實際的字段名稱
    
    
    return {'data': data_list}




# 情感分析
infoDF = pd.DataFrame(call_infoDF()['data'])
weight = pd.read_csv(r'D:\User\user\Desktop\台大\112-1\IR\Final\Web\backend\Django\DjangoAPI\Cafeapp\Query_data\weight_2.csv')
vocabulary = set(weight.newTokens.to_list())

# 擴充斷詞字典  (for query)
with open(r'D:\User\user\Desktop\台大\112-1\IR\Final\Web\backend\Django\DjangoAPI\Cafeapp\Query_data\segmentation_dic.txt', 'r',encoding = 'utf-8', newline='') as f:
    segmentation_dic = [word.split('\r\n')[0] for word in f.readlines()]

for addword in segmentation_dic:
    jieba.add_word(addword)


def query_sentiment(request, q):
    
    # preprocess
    q_words = [w for w in jieba.cut(q)if w in vocabulary]
    
    # search
    ranking = {}
    for q in q_words:
        if q not in vocabulary:
            continue
        for shopID in range(120):
            if q in weight[weight.id == shopID]['newTokens'].to_list():
                if ranking.get(shopID) == None:
                    ranking[shopID] = weight[(weight.id == shopID)&(weight.newTokens==q)]['weight'].to_list()[0]
                else:                ranking[shopID] += weight[(weight.id == shopID)&(weight.newTokens==q)]['weight'].to_list()[0]


    # sort the score
    ranking = {k: v for k, v in sorted(ranking.items(), key = lambda item: item[1], reverse = True)}

    # get top 10
    top = 10
    topID = list(ranking.keys())[:top]
    
    # output result
    return JsonResponse(jasonOutput(q_words,topID))



# function json type output
def jasonOutput(q_words,topID):
    results_dict = {"query_label": q_words, "stores": []}

    for shopID in topID:
            
        result = {}
        result["link"] =infoDF[infoDF.id == shopID]['link'].tolist()[0]
        result["id"] = infoDF[infoDF.id == shopID]['id'].tolist()[0]
        result["name"] = infoDF[infoDF.id == shopID]['name'].tolist()[0]
        result["time"] = infoDF[infoDF.id == shopID]['time'].tolist()[0]
        result["address"] = infoDF[infoDF.id == shopID]['address'].tolist()[0]
        result["phone"] = infoDF[infoDF.id == shopID]['phone'].tolist()[0]
        result["img"] = infoDF[infoDF.id == shopID]['img'].tolist()[0]
        result["website"] = infoDF[infoDF.id == shopID]['website'].tolist()[0]
        result["star"] = infoDF[infoDF.id == shopID]['star'].tolist()[0]
        result["review_num"] = infoDF[infoDF.id == shopID]['review_num'].tolist()[0]
        
        result['labels'] = weight[weight.id == shopID].sort_values('weight',ascending=False)[:3]['newTokens'].to_list()
        
       
    
        results_dict["stores"].append(result)
    return results_dict