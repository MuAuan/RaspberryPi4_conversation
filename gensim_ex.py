from gensim.models import FastText
model=FastText.load_fasttext_format('model300.bin')
print("model.most_similar(positive=['フランス', '東京'], negative=['パリ'])",model.most_similar(positive=['フランス', '東京'], negative=['パリ']))