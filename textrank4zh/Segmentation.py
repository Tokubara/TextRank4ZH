#-*- encoding:utf-8 -*-
"""
@author:   letian
@homepage: http://www.letiantian.me
@github:   https://github.com/someus/
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import jieba.posseg as pseg
import codecs
import os
from operator import attrgetter

# from . import util
import util

def get_default_stop_words_file():
    d = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(d, 'stopwords.txt')

class WordSegmentation(object):
    """ 将一句话或者一个句列表分词, 可选属性为停用词, 词性词表, 有两个函数, segment将一句话(str)分为词(有一些选项, 停用词, 过滤词性), segment_sentences, 接受一个sentences列表, 批量转换, 两个函数的参数完全一样, 仅仅是批量转换的关系 """
    
    def __init__(self, stop_words_file = None, allow_speech_tags = util.allow_speech_tags):
        """
        Keyword arguments:
        stop_words_file    -- 保存停止词的文件路径，utf8编码，每行一个停止词。若不是str类型，则使用默认的停止词
        allow_speech_tags  -- 词性列表，用于过滤
        """     
        
        allow_speech_tags = [util.as_text(item) for item in allow_speech_tags]

        self.default_speech_tag_filter = allow_speech_tags
        self.stop_words = set()
        self.stop_words_file = get_default_stop_words_file() # 如果为空, 那么就是默认的
        if type(stop_words_file) is str:
            self.stop_words_file = stop_words_file
        for word in codecs.open(self.stop_words_file, 'r', 'utf-8', 'ignore'):
            self.stop_words.add(word.strip())
    
    def segment(self, text, lower = False, use_stop_words = True, use_speech_tags_filter = False):
        """对一段文本进行分词(jieba.posseg.cut)，返回list类型的分词结果, 做了这些处理: 去除特殊符号(词性为x的词), 去空, 去停用词

        Keyword arguments:
        lower                  -- 是否将单词小写（针对英文）
        use_stop_words         -- 若为True，则利用停止词集合来过滤（去掉停止词）
        use_speech_tags_filter -- 是否基于词性进行过滤。若为True，则使用self.default_speech_tag_filter过滤。否则，不过滤。    
        """
        text = util.as_text(text) # 只是一句话
        words_result = pseg.cut(text) # 得到的是一个generator
        # 这里得先做, 否则不会保留分词信息
        if use_speech_tags_filter == True:
            # jieba_result = [w for w in jieba_result if w.flag in self.default_speech_tag_filter]
            words_result = filter(lambda x:x.flag in self.default_speech_tag_filter, words_result)
        # else:
            # jieba_result = [w for w in jieba_result]

        # 去除特殊符号
        # 含有中文以外的词都去掉
        words_result = filter(lambda x:len(x)>0 and util.is_all_chinese(x),map(lambda x: x.word.strip(),words_result)) # 去除含有中文以外字符,去除空格,去除为空的
        if use_stop_words:
            words_result = filter(lambda x: x not in self.stop_words, words_result)
        # word_list = [w.word.strip() for w in jieba_result if w.flag!='x']
        # word_list = [word for word in word_list if len(word)>0]
        
        # if lower:
        #     word_list = [word.lower() for word in word_list]

        # if use_stop_words:
        #     word_list = [word.strip() for word in word_list if word.strip() not in self.stop_words]

        return list(words_result)
        
    def segment_sentences(self, sentences, lower=True, use_stop_words=True, use_speech_tags_filter=False):
        """将列表sequences中的每个元素/句子转换为由单词构成的列表。大概长这样: [['从', '施剑翘', '杀', '孙传芳', '案', '看', ...], ['解题'], ['民国时期', '是', '司法', '史', '一个', '特殊', ...], ['有', '如下', '原因'], ['中国', '有着', '几千年', '的', '宗法', '礼教', ...], ['到', '清末', '民初', '司法', '领域', '发生', ...], ...]
        
        sequences -- 列表，每个元素是一个句子（字符串类型）
        """
        
        res = []
        for sentence in sentences: # 这里本来可以写成一个listcomp
            res.append(self.segment(text=sentence, 
                                    lower=lower, 
                                    use_stop_words=use_stop_words, 
                                    use_speech_tags_filter=use_speech_tags_filter))
        return res
        
class SentenceSegmentation(object):
    """ 分句 """
    
    def __init__(self, delimiters=util.sentence_delimiters,min_sentence_len=4):
        """
        Keyword arguments:
        delimiters -- 可迭代对象，用来拆分句子
        """
        self.delimiters = set([util.as_text(item) for item in delimiters])
        self.min_sentence_len=min_sentence_len
    
    def segment(self, text):
        res = [util.as_text(text)] # 初始只有一个元素
        
        util.debug(res)
        util.debug(self.delimiters)

        for sep in self.delimiters:
            text, res = res, []
            for seq in text:
                res += seq.split(sep)
        res = [s.strip() for s in res if len(s.strip()) > self.min_sentence_len] # 去除空白, 我总感觉这里还需要filter
        return res 
        
class Segmentation(object):
    
    def __init__(self, stop_words_file = None, 
                    allow_speech_tags = util.allow_speech_tags,
                    delimiters = util.sentence_delimiters, min_sentence_len=4):
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
        text = util.as_text(text)
        sentences = self.ss.segment(text) # 根据delim分好词
        words_no_filter = self.ws.segment_sentences(sentences=sentences,
                                                    lower = lower, 
                                                    use_stop_words = False,
                                                    use_speech_tags_filter = False)
        words_no_stop_words = self.ws.segment_sentences(sentences=sentences, 
                                                    lower = lower, 
                                                    use_stop_words = True,
                                                    use_speech_tags_filter = False)

        words_all_filters = self.ws.segment_sentences(sentences=sentences, 
                                                    lower = lower, 
                                                    use_stop_words = True,
                                                    use_speech_tags_filter = True)
        # 以上3个列表的属性完全一样, 区别只在是否去停词, 和词性
        return util.AttrDict(
                    sentences           = sentences, 
                    words_no_filter     = words_no_filter, 
                    words_no_stop_words = words_no_stop_words, 
                    words_all_filters   = words_all_filters
                )
    
        

if __name__ == '__main__':
    pass