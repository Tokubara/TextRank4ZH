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
import itertools

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass
    


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







#  build_word_cooccurence_matrix的测试
# build_word_cooccurence_matrix([[1,7,3,2,9,5,4],[3,1,2,5,4],[5,3,7,1,9]])

# where=np.argwhere(res>0)
# num=[res[tuple(i)] for i in where if i[0]<i[1]]
# for w,n in zip(where,num):
#     print("{}:{}".format(w,n))



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