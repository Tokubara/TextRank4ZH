#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import networkx as nx
import numpy as np

# from . import util
import util
import itertools
from Segmentation import Segmentation
from collections import namedtuple
from TextProcessor import TextProcessor
import codecs
# import Segmentation

Item=namedtuple("Item",["item","score"])

class TextRank4Keyword(object):
    
    def __init__(self, stop_words_file = None, 
                 allow_speech_tags = util.allow_speech_tags, 
                 delimiters = util.sentence_delimiters):
        """
        init中只创建了segmentation
        """
        # self.text = ''
        # self.keywords = None # 在analyze被赋值, 长这样[{'word': '国民革命军', 'weight': 0.0001555855201742558}, {'word': '集团军', 'weight': 0.0001555855201742558}], 从按得分高到低排序的
        self.seg = Segmentation(stop_words_file=stop_words_file, 
                                allow_speech_tags=allow_speech_tags, 
                                delimiters=delimiters)


        
    def analyze(self, text_processor):
        """
        构建矩阵
        """
        # 只考虑关键词
        self.num2word, self.word2num, self.doc_list_in_num = util.word2num(text_processor.words_all_filters)
        self.cooccurence_matrix = util.build_word_cooccurence_matrix(len(self.num2word),self.doc_list_in_num)
        self.pagerank_matrix = util.convert2pagerank_matrix(self.cooccurence_matrix) # TODO 看起来有点浪费内存, 到底需要保存哪些
        self.pr = util.solve_pagerank_matrix(self.pagerank_matrix)
        # 得到了每一个词的概率分布
        self.pr_argsort = np.argsort(-self.pr) # 从大到小
        

    def get_keywords(self, num = 6, word_min_len = 2):
        """获取最重要的num个长度大于等于word_min_len的关键词。
        返回关键词和得分
        """
        all_sort_items=(Item(item=self.num2word[i],score=self.pr[i]) for i in self.pr_argsort)
        return itertools.islice( filter(lambda x:len(x.item)>=word_min_len,all_sort_items) ,num)

if __name__ == '__main__':
    textclass=TextRank4Keyword()
    text = codecs.open("../data/期末报告.md", 'r', 'utf-8').read()
    text_processor=TextProcessor(text)
    textclass.analyze(text_processor)
    print(textclass.get_keywords(10))
    import pdb;pdb.set_trace()
