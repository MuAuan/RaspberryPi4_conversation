#>python tf_idf_classical.py -d C:\PROGRA~1\mecab\dic\ipadic conversation_anzen.csv  -s stop_words.txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import MeCab

import argparse

parser = argparse.ArgumentParser(description="convert csv")
parser.add_argument("input", type=str, help="csv file")
parser.add_argument("--dictionary", "-d", type=str, help="mecab dictionary")
parser.add_argument("--stop_words", "-s", type=str, help="stop words list")
args = parser.parse_args()

mecab = MeCab.Tagger("-Owakati" + ("" if not args.dictionary else " -d " + args.dictionary))

questions = []
#answers = []

def train_conv(mecab,input_file):
    questions = []
    with open(input_file) as f:
        cols = f.read().strip().split('\n')
        for i in range(len(cols)):
            questions.append(mecab.parse(cols[i]).strip())
    return questions

stop_words = []
if args.stop_words:
    for line in open(args.stop_words, "r", encoding="utf-8"):
        stop_words.append(line.strip())

questions = train_conv(mecab,args.input)        
vectorizer = TfidfVectorizer(token_pattern="(?u)\\b\\w+\\b", stop_words=stop_words)
vecs = vectorizer.fit_transform(questions)

#for k,v in vectorizer.vocabulary_.items():
#    print(k, v)

while True:
    line = input("> ")
    if not line:
        break

    #print(mecab.parse(line))
        
    #index = np.argmax(cosine_similarity(vectorizer.transform([mecab.parse(line)]), vecs))
    #print(questions[index])
    
    print()
    
    sims = cosine_similarity(vectorizer.transform([mecab.parse(line)]), vecs)    
    index = np.argsort(sims[0])
    sk=0
    for j in range(-1,-100,-1):
        if sims[0][index[j]]>=0.2:
            print("{}_({:.2f}): {}".format(sk,sims[0][index[j]],questions[index[j]]))
            print()
            sk += 1
