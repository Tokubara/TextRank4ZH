from TextProcessor import TextProcessor
from PageRank import PageRank
import numpy as np
import codecs


class TextRank4Keyword(PageRank):
    def build_matrix(self, text_processor):
        '''text_processor是TextProcessor的实例'''
        self.matrix = self.build_word_cooccurence_matrix(len(text_processor.num2word[2]),text_processor.doc_list_in_num[2])
        self.num2item = text_processor.num2word[2]
    def analyze(self, text_processor):
        text_processor.get_word2num()
        self.build_matrix(text_processor)
        super().analyze()
    @staticmethod
    def build_word_cooccurence_matrix(n,doc_list_in_num,window=2):
        '''
        n:总的状态数(词数),doc_list_in_num:文档的数表示
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
    text_processor.get_word2num()
    textclass.analyze(text_processor)
    import pprint
    pprint.pprint(list(textclass.get_top_items(10)))
