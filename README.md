进入到src/中, main.py中修改text_path为目的文件路径, 执行`python main.py`.
或者通过命令行参数, `python main.py <target_file_path>`

```
pandoc -s --pdf-engine=xelatex -o report.pdf 报告.md
```

