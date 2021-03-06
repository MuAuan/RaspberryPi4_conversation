# -*- coding: utf-8 -*-
#$ python3 auto_conversation_.py -i data/conversation_n.txt  -s data/stop_words.txt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import MeCab

import argparse
import pyaudio
import wave
from pykakasi import kakasi
import re
import csv
import time

parser = argparse.ArgumentParser(description="convert csv")
parser.add_argument("--input", "-i",type=str, help="faq txt file")
parser.add_argument("--dictionary", "-d", type=str, help="mecab dictionary")
parser.add_argument("--stop_words", "-s", type=str, help="stop words list")
args = parser.parse_args()

def text2speak(num0):
    RATE=44100
    CHUNK = 22050
    p=pyaudio.PyAudio()
    kakasi_ = kakasi()

    sentence=num0

    kakasi_.setMode('J', 'H')  # J(Kanji) to H(Hiragana)
    kakasi_.setMode('H', 'H') # H(Hiragana) to None(noconversion)
    kakasi_.setMode('K', 'H') # K(Katakana) to a(Hiragana)

    conv = kakasi_.getConverter()

    char_list = list(conv.do(sentence))

    kakasi_.setMode('H', 'a') # H(Hiragana) to a(roman)
    conv = kakasi_.getConverter()
    sentences=[]
    for i in range(len(char_list)):
        sent= conv.do(char_list[i])
        sentences.append(sent)
    
    f_list=[]
    f_list=sentences

    stream=p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = int(RATE*1.8),
        frames_per_buffer = CHUNK,
        input = True,
        output = True)

    w = wave.Wave_write("./pyaudio/ohayo005_sin.wav")
    p = (1, 2, RATE, CHUNK, 'NONE', 'not compressed')
    w.setparams(p)
    for i in f_list:
        i = re.sub(r"[^a-z]", "", i)
        if i== '':
            continue
        else:
            wavfile = './pyaudio/aiueo/'+i+'.wav'
        #print(wavfile)
        try:
            wr = wave.open(wavfile, "rb")
        except:
            wavfile = './pyaudio/aiueo/n.wav'
            continue
        input = wr.readframes(wr.getnframes())
        output = stream.write(input)
        w.writeframes(input)

def save_questions(line):
    with open('conversation_n.txt', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow({line})
        
def conversation(questions,vecs,mecab):
    line = input("> ")
    with open('conversation_n.txt', 'a', newline='') as f: #a+ #w
        writer = csv.writer(f)
        while True:
            #writer.writerow({line})
            sims = cosine_similarity(vectorizer.transform([mecab.parse(line)]), vecs)
            index = np.argsort(sims[0])
            sk = 0
            while True:
                index_= index[-np.random.randint(1,5)]
                line = questions[index_]
                conv_new=read_conv(mecab)
                s=1
                ss=1
                for j in range(0,len(conv_new),1):
                    line_ = re.sub(r"[^一-龥ぁ-んァ-ン]", "", line)
                    conv_new_ = re.sub(r"[^一-龥ぁ-んァ-ン]", "", conv_new[j])
                    if line_==conv_new_:
                        s=0
                    else:
                        s=1
                    ss *= s
                    #rint(j,ss)
                if ss == 0:
                    line="分かりません"
                    sk += 1
                    if sk>5:
                        break
                    continue
                else:
                    break
            save_questions(line)
            if line=="分かりません":
                print("同じ質問ばかりでつまらない")
            else:
                print("({:.2f}): {}".format(sims[0][index_],questions[index_]))
            #text2speak(questions[index_])
            time.sleep(2)
            line = input("> ")
            save_questions(line)
            if not line:
                break

def train_conv(mecab,input):
    questions = []
    print(input)
    with open(input, encoding="utf-8") as f:
        cols = f.read().strip().split('\n')
        for i in range(len(cols)):
            questions.append(mecab.parse(cols[i]).strip())
    return questions        

def read_conv(mecab):
    conv_new = []
    with open('conversation_n.txt') as f:
        cols = f.read().strip().split('\n')
        for i in range(len(cols)):
            conv_new.append(mecab.parse(cols[i]).strip())
    return conv_new

mecab = MeCab.Tagger("-Owakati" + ("" if not args.dictionary else " -d " + args.dictionary))
#mecab = MeCab.Tagger("-Owakati")
stop_words = []
if args.stop_words:
    for line in open(args.stop_words, "r", encoding="utf-8"):
        stop_words.append(line.strip())

while True:
    questions = train_conv(mecab,args.input)
    vectorizer = TfidfVectorizer(token_pattern="(?u)\\b\\w+\\b", stop_words=stop_words)
    vecs = vectorizer.fit_transform(questions)
    conversation(questions,vecs,mecab)
   