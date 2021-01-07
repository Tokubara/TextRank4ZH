#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import codecs
import jieba.posseg as pseg
import codecs
import os
from operator import attrgetter
import itertools
# from TextProcessor import TextProcessor

# from . import util
import util

class TextProcessor(object):
    sentence_delimiters = {'?', '.', '!', ';', '？', '！', '。', '；', '……', '…', '\n'} # 未考虑引号
    allow_speech_tags = {'an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng'}
    def __init__(self, text, stop_words_file = None, lower=False,
                 allow_speech_tags = None, 
                 delimiters = None):
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
        self.allow_speech_tags = allow_speech_tags or TextProcessor.allow_speech_tags
        self.delimiters = delimiters or TextProcessor.sentence_delimiters
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
def get_default_stop_words_file():
    d = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(d, 'stopwords.txt')

class WordSegmentation(object):
    """ 将一句话或者一个句列表分词, 可选属性为停用词, 词性词表, 有两个函数, segment将一句话(str)分为词(有一些选项, 停用词, 过滤词性), segment_sentences, 接受一个sentences列表, 批量转换, 两个函数的参数完全一样, 仅仅是批量转换的关系 """
    
    def __init__(self, stop_words_file = None, allow_speech_tags = TextProcessor.allow_speech_tags):
        """
        Keyword arguments:
        stop_words_file    -- 保存停止词的文件路径，utf8编码，每行一个停止词。若不是str类型，则使用默认的停止词
        allow_speech_tags  -- 词性列表，用于过滤
        """     
        
        # allow_speech_tags = [util.as_text(item) for item in allow_speech_tags]

        self.default_speech_tag_filter = allow_speech_tags
        self.stop_words = set()
        self.stop_words_file = get_default_stop_words_file() # 如果为空, 那么就是默认的
        if type(stop_words_file) is str:
            self.stop_words_file = stop_words_file
        for word in codecs.open(self.stop_words_file, 'r', 'utf-8', 'ignore'):
            self.stop_words.add(word.strip())
    
    def segment(self, text, lower = False):
        # use_stop_words = True, use_speech_tags_filter = False (旧参数)
        """对一段文本进行分词(jieba.posseg.cut)，是一个generator函数, 得到的是, 去除特殊符号后的分词的map对象, 去除停用词的map对象, 去除词性不对的词的map对象
        """
        # text = util.as_text(text) # 只是一句话
        words_result = pseg.cut(text) # 得到的是一个generator

        words_result = list(filter(lambda x:TextProcessor.is_all_chinese(x.word),words_result)) # 去除含有中文以外字符,去除空格,去除为空的
        yield map(attrgetter("word"),words_result)
        words_result = list(filter(lambda x: x.word not in self.stop_words, words_result))
        yield map(attrgetter("word"),words_result)
        words_result = list(filter(lambda x:x.flag in self.default_speech_tag_filter, words_result))
        yield map(attrgetter("word"),words_result)
        
    def segment_sentences(self, sentences, lower=False, need=(0,1,2)):
        """将列表sequences中的每个元素/句子转换为由单词构成的列表。
        返回一个list, 每个元素是嵌套generator, 第一层是每个句子, 第二层是词, 展开长这样: [['从', '施剑翘', '杀', '孙传芳', '案', '看', ...], ['解题'], ['民国时期', '是', '司法', '史', '一个', '特殊', ...], ['有', '如下', '原因'], ['中国', '有着', '几千年', '的', '宗法', '礼教', ...], ['到', '清末', '民初', '司法', '领域', '发生', ...], ...]
        """
        gen_list=[self.segment(sentence) for sentence in sentences]
        res_list=[None,None,None]
        res_list[0]=(next(i) for i in gen_list)
        res_list[1]=(next(i) for i in gen_list)
        res_list[2]=(next(i) for i in gen_list)
        return res_list
        
class SentenceSegmentation(object):
    """ 分句 """
    
    def __init__(self, delimiters=TextProcessor.sentence_delimiters,min_sentence_len=4):
        """
        Keyword arguments:
        delimiters -- 可迭代对象，用来拆分句子
        """
        # self.delimiters = set([util.as_text(item) for item in delimiters])
        self.min_sentence_len=min_sentence_len
        self.delimiters=delimiters
    def segment(self, text):
        '''返回的是句子的generator'''
        res = [text]
        # util.debug(res)
        # util.debug(self.delimiters)

        for sep in self.delimiters:
            text, res = res, []
            for seq in text:
                res += seq.split(sep)
        return filter(lambda x:len(x)>0, map(lambda x:x.strip(),res)) # 去除空白, 我总感觉这里还需要filter
        
class Segmentation(object):
    
    def __init__(self, stop_words_file = None, 
                    allow_speech_tags = TextProcessor.allow_speech_tags,
                    delimiters = TextProcessor.sentence_delimiters, min_sentence_len=4):
        """
        Keyword arguments:
        stop_words_file -- 停止词文件
        delimiters      -- 用来拆分句子的符号集合
        """
        self.ws = WordSegmentation(stop_words_file=stop_words_file, allow_speech_tags=allow_speech_tags)
        self.ss = SentenceSegmentation(delimiters=delimiters,min_sentence_len=min_sentence_len)
        
    def segment(self, text, lower = False):
        '''
        返回util.AttrDict, 包括: 
        sentences:句列表,即根据delimiters分隔的
        words_no_filter:分好词的嵌套列表
        words_no_stop_words:去除了停词
        words_all_filters:去除了停词和词性不在allow_speech_tags中的词
        '''
        # text = util.as_text(text)
        sentences = self.ss.segment(text) # 一个filter
        sentences_list=list(sentences)
        words_res=self.ws.segment_sentences(sentences_list)
        # 以上3个列表的属性完全一样, 区别只在是否去停词, 和词性
        # TODO: 这里不一定需要返回list, 如果不需要的话, 尽量返回generator
        return util.AttrDict(
                    sentences           = sentences_list, 
                    words_no_filter     = [list(i) for i in words_res[0]], 
                    words_no_stop_words = [list(i) for i in words_res[1]], 
                    words_all_filters   = [list(i) for i in words_res[2]]
                )
    
        

# if __name__ == '__main__':
#     testclass=Segmentation()
#     res=testclass.segment("她是这个世界上最为美丽的女子,没有之一,清水出芙蓉.但我不喜欢她,不是不喜欢长得漂亮的,是不喜欢自以为是的")
#     print(res.sentences)
#     print(res.words_no_filter)
#     print(res.words_no_stop_words)
#     print(res.words_all_filters) 
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