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




if __name__ == '__main__':
    pass