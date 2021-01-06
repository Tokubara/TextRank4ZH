#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import math
import networkx as nx
import numpy as np
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass
    
sentence_delimiters = {'?', '.', '!', ';', '？', '！', '。', '；', '……', '…', '\n'} # 未考虑引号
allow_speech_tags = {'an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng'}

PY2 = sys.version_info[0] == 2
if not PY2:
    # Python 3.x and up
    text_type    = str
    string_types = (str,)
    xrange       = range

    def as_text(v):  ## 生成unicode字符串 '''我觉得是多余的'''
        if v is None:
            return None
        elif isinstance(v, bytes):
            return v.decode('utf-8', errors='ignore')
        elif isinstance(v, str):
            return v
        else:
            raise ValueError('Unknown type %r' % type(v))

    def is_text(v):
        return isinstance(v, text_type)

else:
    # Python 2.x
    text_type    = unicode
    string_types = (str, unicode)
    xrange       = xrange

    def as_text(v):
        if v is None:
            return None
        elif isinstance(v, unicode):
            return v
        elif isinstance(v, str):
            return v.decode('utf-8', errors='ignore')
        else:
            raise ValueError('Invalid type %r' % type(v))

    def is_text(v):
        return isinstance(v, text_type)

__DEBUG = None

def debug(*args):
    global __DEBUG
    if __DEBUG is None:
        try:
            if os.environ['DEBUG'] == '1':
                __DEBUG = True
            else:
                __DEBUG = False
        except:
            __DEBUG = False
    if __DEBUG:
        print( ' '.join([str(arg) for arg in args]) )

class AttrDict(dict):
    __slot__=()
    __getattr__=dict.__getitem__
    __setattr__=dict.__setitem__

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

def get_similarity(word_list1, word_list2):
    """默认的用于计算两个句子相似度的函数。

    Keyword arguments:
    word_list1, word_list2  --  分别代表两个句子，都是由单词组成的列表
    """
    words   = list(set(word_list1 + word_list2))  # 两句话的词的并集
    vector1 = [float(word_list1.count(word)) for word in words] # 出现次数
    vector2 = [float(word_list2.count(word)) for word in words]
    
    vector3 = [vector1[x]*vector2[x]  for x in xrange(len(vector1))] # len(vector1)就是len(words), 没有区别. vector3记录的是共现乘积, 比如一个词在s1在s2各出现了2,3次, 那么这个词对应就是6, 如果只在s1出现没有在s2出现, 则为0
    vector4 = [1 for num in vector3 if num > 0.] # 总感觉它的意思是, [1]*sum(vector3>0)
    co_occur_num = sum(vector4) # 似乎它的意思是, sum(vector3>0), 但不能, 必须改成numpy

    if abs(co_occur_num) <= 1e-12: # 不可能出现这个概率, 只是想表达为0罢了(浮点数的舍入误差).
        return 0.
    
    denominator = math.log(float(len(word_list1))) + math.log(float(len(word_list2))) # 分母, 其实就是论文中的公式
    
    if abs(denominator) < 1e-12:
        return 0.
    
    return co_occur_num / denominator

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

def sort_sentences(sentences, words, sim_func = get_similarity, pagerank_config = {'alpha': 0.85,}):
    """将句子按照关键程度从大到小排序

    Keyword arguments:
    sentences         --  列表，元素是句子
    words             --  二维列表，子列表和sentences中的句子对应，子列表由单词组成, 长这样[['郑', '陈复', '家仇', '雪国', '恨', '无可', '原之情'], ['况', '郑', '陈', '事后', '认', '行凶', '潜逃', '情同', '自首', '法', '减等', '条'], ['笔者', '认为', '高级法院', '最高法院', '判决', '受到', '舆论', '公众', '同情', '影响']]
    sim_func          --  计算两个句子的相似性，参数是两个由单词组成的列表
    pagerank_config   --  pagerank的设置
    """
    sorted_sentences = []
    _source = words
    sentences_num = len(_source)  # 虽然输出与len(sorted_sentences)也没有什么不同
    graph = np.zeros((sentences_num, sentences_num)) # 矩阵大小是句子了
    
    for x in xrange(sentences_num):
        for y in xrange(x, sentences_num): # 这里大概是有bug吧, 应该是x+1. # TODO, 似乎应该改成x+1
            similarity = sim_func( _source[x], _source[y] )
            graph[x, y] = similarity
            graph[y, x] = similarity
            
    nx_graph = nx.from_numpy_matrix(graph)
    scores = nx.pagerank(nx_graph, **pagerank_config)              # this is a dict
    sorted_scores = sorted(scores.items(), key = lambda item: item[1], reverse=True)

    for index, score in sorted_scores:
        item = AttrDict(index=index, sentence=sentences[index], weight=score)
        sorted_sentences.append(item)

    return sorted_sentences

if __name__ == '__main__':
    pass