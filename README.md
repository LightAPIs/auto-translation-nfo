# Auto translation nfo

## 配置方法

1. 前往 [Releases](https://github.com/LightAPIs/auto-translation-nfo/releases) 下载压缩包文件
2. 解压得到 `main.exe` 和 `config.ini` 两个文件
3. 编辑 `config.ini` 添加相应的访问令牌和翻译语种，具体见文件内部说明(目前支持彩云小译及百度翻译)

## 使用方法

该工具为 CLI 工具，需在控制台中运行或者可以编写一个批处理来运行。

支持的指令：
```bash
main.exe [-h] -i INPUT -e ELEMENTS [-l {error,all,none}] [-b] [-t]
```

### 指令详情

- `-i INPUT`: 必需，输入工作目录的路径
- `-e ELEMENTS`: 必需，需要翻译的元素节点，多个时以 `|` 分隔
- `-l {error, all, none}`: 打印日志的级别，默认为 `all`；指定为 `none` 时不打印日志
- `-b`: 启用备份文件的功能

### 批处理示例

```bat
@echo off
echo 处理 temp 文件夹；翻译 title 和 plot 节点，同时备份原文件
main.exe -i "d:\temp" -e "title|plot" -b
echo 运行完成，按下任意键退出
pause>NUL
exit
```
