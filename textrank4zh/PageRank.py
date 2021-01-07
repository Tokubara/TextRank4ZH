import numpy as np
import abc
import itertools
from collections import namedtuple

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
        self.pagerank_matrix = PageRank.convert2pagerank_matrix(self.matrix) # TODO 看起来有点浪费内存, 到底需要保存哪些
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