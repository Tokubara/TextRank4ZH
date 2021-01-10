本项目来自[TextRank4ZH](https://github.com/letiantian/TextRank4ZH)的预处理方法, 计算速度, 内存, 效果, 可扩展性, 代码重用角度都要好得多.

### 文件说明

- `PageRank`抽象类, 要求继承它的子类实现`build_matrix`, 提供矩阵构造方法. 此类实现了幂法进行了平稳分布的计算(`analyze`), 概率的排序, 以及返回得分最高的`num`个items(`get_top_items`).
- `TextRank4Keyword`类, 继承了`PageRank`, `build_matrix`用窗内共现次数构造(默认为5, 也就是考虑一个词的前后各2个词).
- `TextRank4Sentence`类, 继承了`PageRank`, `build_matrix`用句的相似度构造.
- `TextProcessor`类, 进行文本处理以及保存文本处理的结果. 避免让`TextRank4Keyword`和`TextRank4Sentence`存储文本. 后两者不存储文本, 只存储矩阵和状态到词/句的映射关系. 预处理包括jieba分词, 去除含有中文以外字符的内容, 去除stopword, 去除不相关词性的词.

### 对比TextRank4ZH的优点

- 实现了`PageRank`抽象类, 计算速度优于`TextRank4ZH`调用的`networkx`包(估计是因为没有多余的处理).
- 代码重用, 解除耦合, 可扩展性好得多. 解除耦合体现在`TextRank4Keyword`和`TextRank4Sentence`完全不处理文本处理的逻辑. 重用体现在, 如果有用`PageRank`算法的其它场景, 只需要继承`PageRank`类添加一个矩阵构造方法. 如果用其它句相似度方法, 只需要继承`TextRank4Sentence`实现新的相似度计算方法`sentence_similarity`.
- 能用`generator`的地方尽量用`generator`, 节省内存与时间.

### 运行方式
进入到src/中, main.py中修改text_path为目的文件路径, 执行`python main.py`.
或者通过命令行参数, `python main.py <target_file_path>`

