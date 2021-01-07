#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
# from . import util
import util
# from .Segmentation import Segmentation
from Segmentation import Segmentation
import codecs

class TextProcessor(object):
    
    def __init__(self, text, stop_words_file = None, lower=False,
                 allow_speech_tags = util.allow_speech_tags, 
                 delimiters = util.sentence_delimiters):
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
                # self.text = util.as_text(text)        
        result = self.seg.segment(text=text, lower=lower)
        self.sentences = result.sentences
        self.words_no_filter = result.words_no_filter
        self.words_no_stop_words = result.words_no_stop_words
        self.words_all_filters   = result.words_all_filters
        
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