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
import abc
# import Segmentation

Item=namedtuple("Item",["item","score"])

class PageRank(abc.ABC):
    @abc.abstractmethod
    def build_matrix(self):
        """
        构建矩阵, 矩阵名必须是self.matrix
        """
        pass
    
    def analyze(self):
        '''
        计算得分, 保存但不返回, 继承的时候可以先build_matrix
        '''
        if not hasattr(self,"matrix"):
            raise KeyError("no attribute matrix, you must call build_matrix() before calling analyze()")
        self.pagerank_matrix = util.convert2pagerank_matrix(self.matrix) # TODO 看起来有点浪费内存, 到底需要保存哪些
        self.pr = self.solve_pagerank_matrix(self.pagerank_matrix)
        # 得到了每一个词的概率分布
        self.pr_argsort = np.argsort(-self.pr) # 从大到小
        
    def get_top_items(self, num = 6, filter_func=lambda x:True):
        """
        获取最重要的num个长度大于等于word_min_len的关键词
        返回关键词和得分
        """
        if not hasattr(self,"num2item"):
            raise KeyError("no attribute num2item, you have to give it")
        all_sort_items=(Item(item=self.num2item[i],score=self.pr[i]) for i in self.pr_argsort)
        return itertools.islice( filter(filter_func,all_sort_items) ,num)
    @staticmethod
    def convert2pagerank_matrix(matrix,rsp=0.15):
        '''
        将一个不规则的matrix(必须是方阵), 这个matrix的列可能全为0, 列和也不唯一的转化为pagerank矩阵, 列和为1. 列表示状态的转移概率.
        '''
        n=matrix.shape[0]
        matrix[:,np.all(matrix==0,axis=0)]=1 # 全0列的转换
        matrix=matrix/np.sum(matrix,axis=0) # 单位化
        matrix=matrix*(1-rsp)+rsp/n # 概率
        return matrix
    @staticmethod
    def solve_pagerank_matrix(matrix,tol=1e-6):
        '''
        用幂法解pagerank方程
        '''
        n=matrix.shape[0]
        pr=np.ones(n)
        pr=pr/n
        while True:
            new_pr=matrix@pr
            if(np.sum((new_pr-pr)**2)<tol):
                break
            pr=new_pr
        return pr/np.sum(pr) # 按理来说, pr应该保持和为1,但是舍入误差保证不了

class TextRank4Keyword(PageRank):
    def build_matrix(self, text_processor):
        self.matrix = self.build_word_cooccurence_matrix(len(self.num2word[2]),text_processor.doc_list_in_num[2])
        self.num2item = text_processor.num2word
            # self.text_processor = text_processor # 这个地方存在共用, 可能会有问题,
    def analyze(self, text_processor):
        self.build_matrix(text_processor)
        super().analyze()
    @staticmethod
    def build_word_cooccurence_matrix(n,doc_list_in_num,window=2):
        '''
        接受的已经是一个数的列表
        n表示总的状态数
        '''
        matrix_size = n
        word_matrix=np.zeros((matrix_size,matrix_size))
        for doc in doc_list_in_num:
            for i in range(len(doc)-1):
                for j in range(i+1,min(i+1+window,len(doc))):
                    word_matrix[min(doc[i],doc[j]),max(doc[i],doc[j])]+=1
        word_matrix=np.maximum(word_matrix,word_matrix.T)
        return word_matrix
    

if __name__ == '__main__':
    textclass=TextRank4Keyword()
    text = codecs.open("../data/期末报告.md", 'r', 'utf-8').read()
    text_processor=TextProcessor(text)
    text_processor.word2num()
    textclass.analyze(text_processor)
    print(textclass.get_top_items(10))
    # import pdb;pdb.set_trace()
