# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer

model = TfidfVectorizer()
print(model)
text_list = ['(?u)私は 醤油 ラーメン と とんこつ ラーメン が 好き です。', '(?u)私は とんこつ ラーメン と 味噌 ラーメン が 好き です。']
model.fit(text_list)
print(model.vocabulary_)
stop_words = ['が','です','私は','と']

model = TfidfVectorizer(token_pattern='(?u)\\b\\w\\w+\\b',stop_words=stop_words)

text_list = ['(?u)私は 醤油 ラーメン と とんこつ ラーメン が 好き です。', '(?u)私は とんこつ ラーメン と 味噌 ラーメン が 好き です。']
X=model.fit_transform(text_list)
print(model.vocabulary_)

for k,v in model.vocabulary_.items():
    print(k, v)
    
print(model.get_feature_names())
print(X)

text_list = ['(?u)私は 醤油 ラーメン と とんこつ ラーメン が 好き です。', '(?u)私は とんこつ ラーメン と 味噌 ラーメン が 好き です。', '(?u)私は かつ丼　と ラーメン と お好み焼き が 好き です。']
X=model.fit_transform(text_list)
print(model.vocabulary_)

from sklearn.metrics.pairwise import cosine_similarity
sims = cosine_similarity(X, X)
print(X)
print(sims)