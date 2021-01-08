import numpy as np
from PageRank import PageRank
from TextProcessor import TextProcessor
import codecs
from util import AttrDict
import math

class TextRank4Sentence(PageRank):
    def build_matrix(self, text_processor):
        # text_processor.words_all_filters
        n = len(text_processor.sentences)
        self.matrix=np.zeros((n,n))
        for i in range(n):
            for j in range(i+1,n): # 对称矩阵
                self.matrix[i,j]=TextRank4Sentence.sentence_similarity(text_processor.words_all_filters[i], text_processor.words_all_filters[j])
        # self.num2item = text_processor.num2word[2]
        self.matrix=np.maximum(self.matrix,self.matrix.T)
        self.num2item=list(enumerate(text_processor.sentences))
            # self.text_processor = text_processor # 这个地方存在共用, 可能会有问题
    def analyze(self, text_processor):
        self.build_matrix(text_processor)
        super().analyze()
            
    @staticmethod
    def sentence_similarity(word_list1, word_list2):
        """
        基于词的共现情况计算两个句子相似度的函数
        """
        co_occur_num = len(set(word_list1) & set(word_list2))
        if co_occur_num==0 or len(word_list1)==0 or len(word_list2)==0: # 有可能发生的, 有可能有的句子过滤词性后就为空
            return 0 
        denominator = math.log(len(word_list1)) + math.log(len(word_list2)) # 分母, 其实就是论文中的公式
        if denominator<1e-12: # 也有可能长度都为1
            return 0
        return co_occur_num / denominator

if __name__ == '__main__':
    import pprint
    textclass=TextRank4Sentence()
    text = codecs.open("../data/期末报告.md", 'r', 'utf-8').read()
    text_processor=TextProcessor(text)
    textclass.analyze(text_processor)
    pprint.pprint(list(textclass.get_top_items(10)))
