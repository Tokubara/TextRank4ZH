import codecs
from TextRank4Keyword import TextRank4Keyword
from TextRank4Sentence import TextRank4Sentence
from TextProcessor import TextProcessor
import sys
import time
import pprint

text_path="../data/期末报告.md" if len(sys.argv)==1 else sys.argv[1]
text = codecs.open(text_path, 'r', 'utf-8').read()
t0=time.time()
text_processor=TextProcessor(text)
t1=time.time() # 仅在关键词的时候需要

t2=time.time()
textrank_keyword = TextRank4Keyword()
textrank_keyword.analyze(text_processor)
t3=time.time()

textrank_sentence = TextRank4Sentence()
textrank_sentence.analyze(text_processor)
t4=time.time()
pprint.pprint(list(textrank_keyword.get_top_items(10)))
print()
pprint.pprint(list(textrank_sentence.get_top_items(10)))
print("处理分词用时:{:.5f}s,计算词用时{:.5f}s, 计算句用时:{:.5f}s".format(t1-t0,t3-t2,t4-t3))