# -*- coding: utf-8 -*-
#$ python3 auto_conversation_cycle2.py -i1 data/negativ_all_n.txt -i2 data/conversation_s.txt  -s data/stop_words.txt -d /usr/lib/arm-linux-gnueabihf/mecab/dic/mecab-ipadic-neologd

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
parser.add_argument("--input1", "-i1",type=str, help="speaker1 txt file")
parser.add_argument("--input2", "-i2",type=str, help="speaker2 txt file")
parser.add_argument("--dictionary", "-d", type=str, help="mecab dictionary")
parser.add_argument("--stop_words", "-s", type=str, help="stop words list")
args = parser.parse_args()

RATE=44100 #48000
CHUNK = 22050
p=pyaudio.PyAudio()
kakasi_ = kakasi()
stream=p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = int(48000),
        frames_per_buffer = CHUNK,
        input = True,
        output = True)

def text2speak(num0):
    sentence=num0

    kakasi_.setMode('J', 'H') # J(Kanji) to H(Hiragana)
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

    w = wave.Wave_write("./wav/ohayo_.wav")
    p = (1, 2, RATE, CHUNK, 'NONE', 'not compressed')
    w.setparams(p)
    for i in f_list:
        i = re.sub(r"[^a-z]", "", i)
        if i== '':
            continue
        else:
            wavfile = './wav/'+i+'.wav'
        #print(wavfile)
        try:
            wr = wave.open(wavfile, "rb")
        except:
            wavfile = './wav/n.wav'
            continue
        input = wr.readframes(wr.getnframes())
        output = stream.write(input)
        w.writeframes(input)

def save_questions(file, line): #'conversation_n.txt'
    with open(file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow({line})

def hiroko(index,speaker,line):
    sk = 0
    while True:
        index_= index[-np.random.randint(1,5)]
        line = speaker[index_]
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
        if ss == 0:
            line="分かりません"
            sk += 1
            if sk>5:
                return line, index_
            continue
        else:
            return line, index_

def conversation(speaker1,speaker2,mecab):
    line = input("> ")
    file = 'conversation_n.txt'
    file2 = 'conversation_n2.txt'
    vectorizer1 = TfidfVectorizer(token_pattern="(?u)\\b\\w+\\b", stop_words=stop_words)
    vecs1 = vectorizer1.fit_transform(speaker1)
    vectorizer2 = TfidfVectorizer(token_pattern="(?u)\\b\\w+\\b", stop_words=stop_words)
    vecs2 = vectorizer2.fit_transform(speaker2)

    while True:
        sims1 = cosine_similarity(vectorizer1.transform([mecab.parse(line)]), vecs1)
        index1 = np.argsort(sims1[0])
           
        line, index_1 = hiroko(index1,speaker1,line)
            
        save_questions(file, line)
        if line=="分かりません":
            print("ひろこ>"+line)
            save_questions(file2, "ひろこ>"+line)
        else:
            print("ひろこ>({:.2f}): {}".format(sims1[0][index_1],line))
            save_questions(file2,"ひろこ>({:.2f}): {}".format(sims1[0][index_1],line))
        text2speak(line)
        time.sleep(2)
            
        sims2 = cosine_similarity(vectorizer2.transform([mecab.parse(line)]), vecs2)
        index2 = np.argsort(sims2[0])
            
        line, index_2 = hiroko(index2,speaker2,line)
     
        save_questions(file, line)
        if line=="分かりません":
            print("ひろみ>"+line)
            save_questions(file2, "ひろみ>"+line)
        else:
            print("ひろみ>({:.2f}): {}".format(sims2[0][index_2],line))  
            save_questions(file2, "ひろみ>({:.2f}): {}".format(sims2[0][index_2],line))
        text2speak(line)
        time.sleep(2)
        if not line:
            break

def train_conv(mecab,input,encoding):
    questions = []
    print(input)
    with open(input, encoding=encoding) as f:  #, encoding="utf-8"
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
    speaker1 = train_conv(mecab,args.input1,encoding="shift-jis")
    speaker2 = train_conv(mecab,args.input2,encoding="utf-8")

    conversation(speaker1,speaker2,mecab)
   