# -*- coding: utf-8 -*-
import os
import argparse
import re
from xml.etree.ElementTree import ElementTree, Element

from log import Logger
from config import Config
from translation import Caiyun


def read_nfo(in_path):
    """读取解析 nfo 文件

    Args:
        in_path (String): 文件路径

    Returns:
        ElementTree: 结构树
    """
    tree = ElementTree()
    tree.parse(in_path)
    return tree


def write_nfo(tree, out_path):
    """将树节点写入到文件中

    Args:
        tree (ElementTree): 树节点
        out_path (String): 文件路径
    """
    tree.write(out_path, encoding="utf-8", xml_declaration=True)


def find_nodes(tree, path):
    """寻找子节点

    Args:
        tree (ElementTree): 树节点
        path (String): 节点路径名

    Returns:
        List: 节点列表
    """
    return tree.findall(path)


def change_node_text(node, text, is_add=False, is_delete=False):
    if is_add:
        node.text += text
    elif is_delete:
        node.text = ""
    else:
        node.text = text


def add_child_node(node, ele):
    node.append(ele)


def create_node(tag, property_map, content):
    ele = Element(tag, property_map)
    ele.text = content
    return ele


def get_num(matched):
    return matched.group("value")


def extract_title(content):
    num = re.sub(r"^(?P<value>[\w-]+)\s*.*$", get_num, content)
    title = re.sub(r"^[\w-]+\s*", "", content)
    return {"num": num, "title": title}


def dir_empty(dir_path):
    """[判定目录是否为空]

    Args:
        dir_path ([String]): [目录路径]

    Returns:
        [boolean]: [为空时返回 True]
    """
    dirStatus = False
    if not os.listdir(dir_path):
        dirStatus = True
    return dirStatus


def detect_walk(dir_path, hyphen, log, no_add):
    level = "ERROR"
    if log == "all":
        level = "DEBUG"
    elif log == "none":
        level = "CRITICAL"
    else:
        level = "ERROR"
    xlog = Logger(level, "log")
    config = Config()
    caiyun_token = config.caiyun_token()
    if caiyun_token:
        xlog.debug("彩云小译访问令牌：" + caiyun_token)
        caiyun = Caiyun(caiyun_token)

        for root, _dirs, files in os.walk(dir_path):
            for filename in files:
                file = root + "\\" + filename
                file_ext = os.path.splitext(file)[1]
                if file_ext in [".nfo"]:
                    print("处理 " + file)
                    xlog.info("读取 " + file)
                    tree = read_nfo(file)

                    trans = False
                    originaltitle_list = find_nodes(tree, "originaltitle")
                    # 始终跳过存在 originaltitle 节点的元素
                    if len(originaltitle_list) > 0:
                        xlog.info("跳过 " + file)
                        break
                    else:
                        xlog.info("翻译 " + file)
                        trans = True

                    title_list = find_nodes(tree, "title")
                    if len(title_list) > 0:
                        title_text = str(title_list[0].text)
                        if title_text != "None":
                            xlog.info("原标题: " + title_text)
                            extract_list = extract_title(title_text)
                            ex_num = extract_list["num"]
                            ex_title = extract_list["title"]
                            if hyphen:
                                ex_title = re.sub(r"-", " ", ex_title)
                            if caiyun_token:
                                trans_title = caiyun.translate(
                                    ex_title, "ja2zh")
                                new_title = ex_num + " " + trans_title
                                change_node_text(title_list[0], new_title)
                                xlog.info("新标题: " + new_title)

                                if not no_add:
                                    tree_root = tree.getroot()
                                    original_node = create_node(
                                        "originaltitle", {},
                                        ex_num + " " + ex_title)
                                    add_child_node(tree_root, original_node)
                                    xlog.info("注入原始标题节点")

                    plot_list = find_nodes(tree, "plot")
                    if len(plot_list) > 0:
                        plot_text = str(plot_list[0].text)
                        if plot_text != "None":
                            xlog.info("原情节: " + plot_text)
                            if caiyun_token:
                                trans_plot = caiyun.translate(
                                    plot_text, "ja2zh")
                                change_node_text(plot_list[0], trans_plot)
                                xlog.info("新情节: " + trans_plot)

                    if trans:
                        xlog.info("重新写入 " + file)
                        write_nfo(tree, file)
    else:
        print("无 token")
        xlog.error("没有找到彩支小译访问令牌")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Auto translate nfo file.")
    ap.add_argument("-i", "--input", required=True, help="输入工作目录的路径")
    ap.add_argument("-y",
                    "--hyphen",
                    action="store_true",
                    required=False,
                    help="将连字符替换为空格")
    ap.add_argument(
        "-l",
        "--log",
        choices=["error", "all", "none"],
        default="error",
        required=False,
        help="打印日志",
    )
    ap.add_argument("-n",
                    "--noadd",
                    action="store_true",
                    required=False,
                    help="不要添加原始标题节点")

    args = vars(ap.parse_args())
    dir_path = args["input"]
    hyphen = args["hyphen"]
    log = args["log"]
    no_add = args["noadd"]
    if os.path.isdir(dir_path):
        if not dir_empty(dir_path):
            detect_walk(dir_path, hyphen, log, no_add)
