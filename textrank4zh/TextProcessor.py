#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# from .Segmentation import Segmentation
from Segmentation import Segmentation
import codecs

class TextProcessor(object):
    sentence_delimiters = {'?', '.', '!', ';', '？', '！', '。', '；', '……', '…', '\n'} # 未考虑引号
    allow_speech_tags = {'an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng'}
    def __init__(self, text, stop_words_file = None, lower=False,
                 allow_speech_tags = TextProcessor.allow_speech_tags, 
                 delimiters = TextProcessor.sentence_delimiters):
        """
        stop_words_file  --  str，指定停止词文件路径（一行一个停止词），若为其他类型，则使用默认停止词文件
        delimiters       --  默认值是`?!;？！。；…\n`，用来将文本拆分为句子。
        
        Object Var:
        self.words_no_filter      --  对sentences中每个句子分词而得到的两级列表。
        self.words_no_stop_words  --  去掉words_no_filter中的停止词而得到的两级列表。
        self.words_all_filters    --  保留words_no_stop_words中指定词性的单词而得到的两级列表。
        """
        # 初始化参数
        self.text = text
        
        self.seg = Segmentation(stop_words_file=stop_words_file, 
                                allow_speech_tags=allow_speech_tags, 
                                delimiters=delimiters)
        # 处理      
        result = self.seg.segment(text=text, lower=lower)
        self.sentences = result.sentences
        self.words_no_filter = result.words_no_filter
        self.words_no_stop_words = result.words_no_stop_words
        self.words_all_filters   = result.words_all_filters
        self.num2word = list(None,None,None)
        self.word2num = list(None,None,None)
        self.doc_list_in_num = list(None,None,None)
    def word2num(self,mode=2):
        '''
        mode 0表示对未过滤停词的转化, 1表示对未词性过滤的转换, 2表示全过滤转换
        '''
        self.num2word[mode], self.word2num[mode], self.doc_list_in_num[mode] = TextProcessor.word2num((self.words_no_filter,self.words_no_stop_words,self.words_all_filters)[mode])
    @staticmethod
    def is_all_chinese(str):
        '''判断字符串是否全由中文构成'''
        return all(map(lambda char:'\u4e00' <= char <= '\u9fa5', str))
    @staticmethod
    def word2num(doc_list):
        '''
        接受双层iterable, 展开以后长这样[['我','喜欢'],['但','我','不喜欢']]
        返回num2word, word2num, doc_list_in_num, 前面是2个字典, 最后是将词转化为数的列表
        '''
        # word_list
        # 首先需要一个词表
        word_set=set(itertools.chain.from_iterable(doc_list))
        word_num=enumerate(word_set)
        #  词到数的映射
        num2word = dict(word_num)
        word2num=dict(zip(num2word.values(),num2word.keys()))
        # 将列表转换为数
        doc_list_in_num=[list(map(lambda x:word2num[x], doc)) for doc in doc_list] # 这里要不要返回list?
        return num2word, word2num, doc_list_in_num   
if __name__ == '__main__':
    # 测试
    text = codecs.open("../data/期末报告.md", 'r', 'utf-8').read()
    text_processor=TextProcessor(text)
    print(text_processor.sentences)
    print(text_processor.words_no_filter)
    print(text_processor.words_all_filters)
    # import pdb; pdb.set_trace()
    # sentences_len=[len(i) for i in text_processor.sentences]
    # sort_res=sorted(enumerate(sentences_len),key=itemgetter(1))
    # text_processor.sentences[156]
    # a=1