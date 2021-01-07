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
from Segmentation import Segmentation
# import Segmentation

def sort_words(vertex_source, edge_source, window = 2, pagerank_config = {'alpha': 0.85,}):
    """将单词按关键程度从大到小排序. 实现? 先构建了词和数的双向索引. 然后构建了共现矩阵, 用zip的方法, 很漂亮. 然后调用networkx的pagerank函数, 得到了每个状态的得分, 
    首先一个问题是vertex_source与edge_source有何不同? 它们都是长这样[['结罪', '理狱', '君', '常理'], ['敢', '贪生', '公法']]. 前者是用来构建词与id的双向索引. 决定了矩阵的大小, 决定了这个矩阵会考虑哪些词. 后者是决定了, 哪些词的关系会被考虑在内. 那么谁应该大一些呢? vertex不应该小于edge
    Keyword arguments:
    vertex_source   --  二维列表，子列表代表句子，子列表的元素是单词，这些单词用来构造pagerank中的节点
    edge_source     --  二维列表，子列表代表句子，子列表的元素是单词，根据单词位置关系构造pagerank中的边
    window          --  一个句子中相邻的window个单词，两两之间认为有边
    返回长这样: [{'word': '国民革命军', 'weight': 0.0001555855201742558}, {'word': '集团军', 'weight': 0.0001555855201742558}], 从高到低排序
    """
    sorted_words   = []
    word_index     = {} # 映射关系, 具体是谁和谁的映射关系, 是词->index的映射关系
    index_word     = {} # index->词的映射关系
    _vertex_source = vertex_source
    _edge_source   = edge_source
    words_number   = 0 # 不同的词数
    for word_list in _vertex_source: # 构建word_index, index_word, words_number, 也就是构建这几个映射关系
        for word in word_list:
            if not word in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1
    # 上面一段是在构建双向索引, 但我总觉得它可以写得更好看一些, 通过去重之类的
    graph = np.zeros((words_number, words_number)) # 我想是转移矩阵
    
    for word_list in _edge_source:
        for w1, w2 in combine(word_list, window):
            if w1 in word_index and w2 in word_index: # 难道还能不在么?
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] = 1.0 # 注意是直接置1, 没有考虑出现次数的差别
                graph[index2][index1] = 1.0

    debug('graph:\n', graph)
    
    nx_graph = nx.from_numpy_matrix(graph) # 构建了这个: networkx.classes.graph.Graph, 已经实现好了pagerank算法
    scores = nx.pagerank(nx_graph, **pagerank_config)  # pagerank_config只有一个参数: {'alpha': 0.85} # 返回是啥呢? 是一个字典, key为这个图的序号, value就是得分, 比如{0: 0.012329385979072585, 1: 0.002640200031317955, 2: 0.010181957937614436}这样
    sorted_scores = sorted(scores.items(), key = lambda item: item[1], reverse=True) # 根据value来排序
    for index, score in sorted_scores: 
        item = AttrDict(word=index_word[index], weight=score)
        sorted_words.append(item)

    return sorted_words # 得到是一个这样的列表: [{'word': '国民革命军', 'weight': 0.0001555855201742558}, {'word': '集团军', 'weight': 0.0001555855201742558}]

def combine(word_list, window = 2):
    """构造在window下的单词组合，用来构造单词之间的边。
    
    Keyword arguments:
    word_list  --  list of str, 由单词组成的列表。
    windows    --  int, 窗口大小。
    """
    if window < 2: window = 2
    for x in xrange(1, window): # xrange其实是为了兼容性, 就是range
        if x >= len(word_list):
            break
        word_list2 = word_list[x:] # 这个很奇怪啊, 难道不是左边, 右边么?
        res = zip(word_list, word_list2) # 长度不同啊, 
        for r in res:
            yield r

class TextRank4Keyword(object):
    
    def __init__(self, text, stop_words_file = None, 
                 allow_speech_tags = util.allow_speech_tags, 
                 delimiters = util.sentence_delimiters):
        """
        Keyword arguments:
        stop_words_file  --  str，指定停止词文件路径（一行一个停止词），若为其他类型，则使用默认停止词文件
        delimiters       --  默认值是`?!;？！。；…\n`，用来将文本拆分为句子。
        
        Object Var:
        self.words_no_filter      --  对sentences中每个句子分词而得到的两级列表。
        self.words_no_stop_words  --  去掉words_no_filter中的停止词而得到的两级列表。
        self.words_all_filters    --  保留words_no_stop_words中指定词性的单词而得到的两级列表。
        """
        # self.text = ''
        # self.keywords = None # 在analyze被赋值, 长这样[{'word': '国民革命军', 'weight': 0.0001555855201742558}, {'word': '集团军', 'weight': 0.0001555855201742558}], 从按得分高到低排序的
        self.seg = Segmentation(stop_words_file=stop_words_file, 
                                allow_speech_tags=allow_speech_tags, 
                                delimiters=delimiters)

        # self.sentences = None
        # self.words_no_filter = None     # 2维列表
        # self.words_no_stop_words = None
        # self.words_all_filters = None

        
    def analyze(self, doc_list_in_num):
        """构建矩阵

        Keyword arguments:
        text       --  文本内容，字符串。
        window     --  窗口大小，int，用来构造单词之间的边。默认值为2。
        lower      --  是否将文本转换为小写。默认为False。
        vertex_source   --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点。
                            默认值为`'all_filters'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。关键词也来自`vertex_source`。
        edge_source     --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点之间的边。
                            默认值为`'no_stop_words'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。边的构造要结合`window`参数。
        """
        
        # self.text = util.as_text(text)
            # testclass=Segmentation()


        # self.word_index = {}
        # self.index_word = {}
        # self.keywords = []
        # self.graph = None
        # self.text = text
        # result = self.seg.segment(text=text, lower=lower)
        # self.sentences = result.sentences
        # self.words_no_filter = result.words_no_filter
        # self.words_no_stop_words = result.words_no_stop_words
        # self.words_all_filters   = result.words_all_filters

        # util.debug(20*'*')
        # util.debug('self.sentences in TextRank4Keyword:\n', ' || '.join(self.sentences))
        # util.debug('self.words_no_filter in TextRank4Keyword:\n', self.words_no_filter)
        # util.debug('self.words_no_stop_words in TextRank4Keyword:\n', self.words_no_stop_words)
        # util.debug('self.words_all_filters in TextRank4Keyword:\n', self.words_all_filters)


        # options = ['no_filter', 'no_stop_words', 'all_filters']

        # if vertex_source in options:
        #     _vertex_source = result['words_'+vertex_source]
        # else:
        #     _vertex_source = result['words_all_filters']

        # if edge_source in options:
        #     _edge_source   = result['words_'+edge_source]
        # else:
        #     _edge_source   = result['words_no_stop_words']

        self.keywords = util.sort_words(_vertex_source, _edge_source, window = window, pagerank_config = pagerank_config)

    def get_keywords(self, num = 6, word_min_len = 1):
        """获取最重要的num个长度大于等于word_min_len的关键词。

        Return:
        关键词列表。
        """
        result = []
        count = 0
        for item in self.keywords:
            if count >= num:
                break
            if len(item.word) >= word_min_len:
                result.append(item)
                count += 1
        return result # 我感觉这个函数用itertools一行就能写完, itertools.islice(filter(lambda x:len(x)>word_min_len,self.keywords),0,num)

if __name__ == '__main__':
    pass