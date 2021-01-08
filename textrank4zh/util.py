class AttrDict(dict):
    __slot__=()
    __getattr__=dict.__getitem__
    __setattr__=dict.__setitem__
