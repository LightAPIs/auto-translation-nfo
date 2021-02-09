# -*- coding: utf-8 -*-
import os
import argparse
import re
import time
from xml.etree.ElementTree import ElementTree, Element

from log import Logger
from config import Config
from tag import Tag
from translation.caiyun import Caiyun
from translation.baidu import Baidu


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


def remove_node(parent_node, del_node):
    parent_node.remove(del_node)


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


def detect_walk(dir_path, hyphen, log, no_add, tag):
    level = "ERROR"
    if log == "all":
        level = "DEBUG"
    elif log == "none":
        level = "CRITICAL"
    else:
        level = "ERROR"
    xlog = Logger(level, "log")

    xlog.debug("************************************************")
    xlog.debug("工作目录: " + dir_path)
    xlog.debug("替换连字符: " + str(hyphen))
    xlog.debug("日志级别: " + log)
    xlog.debug("禁止添加原始标题节点: " + str(no_add))
    xlog.debug("替换标签: " + str(tag))
    xlog.debug("************************************************")

    config = Config()
    engine_type = config.engine_type()
    has_engine = False
    engine = False
    if engine_type == "baidu":
        baidu_app_id = config.baidu_app_id()
        baidu_key = config.baidu_key()
        if baidu_app_id and baidu_key:
            has_engine = True
            engine = Baidu(baidu_app_id, baidu_key)
    elif engine_type == "caiyun":
        caiyun_token = config.caiyun_token()
        if caiyun_token:
            has_engine = True
            engine = Caiyun(caiyun_token)

    tag = Tag()
    tag_data = tag.handler()

    if has_engine:
        xlog.debug("翻译引擎: " + engine_type)

        for root, _dirs, files in os.walk(dir_path):
            for filename in files:
                file = root + "\\" + filename
                file_ext = os.path.splitext(file)[1]
                if file_ext in [".nfo"]:
                    xlog.info(
                        "++++++++++++++++++++++++++++++++++++++++++++++++")
                    xlog.info("读取 " + file)
                    tree = read_nfo(file)
                    mod = False
                    trans = False
                    originaltitle_list = find_nodes(tree, "originaltitle")
                    # 始终跳过存在 originaltitle 节点的元素
                    if len(originaltitle_list) > 0:
                        xlog.info("跳过翻译 " + file)
                        trans = False
                    else:
                        xlog.info("处理翻译 " + file)
                        trans = True

                    if trans:
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

                                time.sleep(1)
                                trans_title = engine.translate(ex_title)
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
                                mod = True

                        plot_list = find_nodes(tree, "plot")
                        if len(plot_list) > 0:
                            plot_text = str(plot_list[0].text)
                            if plot_text != "None":
                                xlog.info("原情节: " + plot_text)
                                time.sleep(1)
                                trans_plot = engine.translate(plot_text)
                                change_node_text(plot_list[0], trans_plot)
                                xlog.info("新情节: " + trans_plot)
                                mod = True

                    if tag:
                        genre_list = find_nodes(tree, "genre")
                        if len(genre_list) > 0:
                            for genre in genre_list:
                                is_del = False
                                for del_tag in tag_data["delete"]:
                                    if del_tag == str(genre.text):
                                        remove_node(tree.getroot(), genre)
                                        xlog.info("删除风格: '" + del_tag + "'")
                                        is_del = True
                                        mod = True

                                if not is_del:
                                    for rep_tag in tag_data["replace"]:
                                        if rep_tag["original"] == str(
                                                genre.text):
                                            change_node_text(
                                                genre, rep_tag["result"])
                                            xlog.info("替换风格: '" +
                                                      rep_tag["original"] +
                                                      "' ==> '" +
                                                      rep_tag["result"] + "'")
                                            mod = True

                        tag_list = find_nodes(tree, "tag")
                        if len(tag_list) > 0:
                            for t in tag_list:
                                is_del = False
                                for del_tag in tag_data["delete"]:
                                    if del_tag == str(t.text):
                                        remove_node(tree.getroot(), t)
                                        xlog.info("删除标签: '" + del_tag + "'")
                                        is_del = True
                                        mod = True

                                if not is_del:
                                    for rep_tag in tag_data["replace"]:
                                        if rep_tag["original"] == str(t.text):
                                            change_node_text(
                                                t, rep_tag["result"])
                                            xlog.info("替换标签: '" +
                                                      rep_tag["original"] +
                                                      "' ==> '" +
                                                      rep_tag["result"] + "'")
                                            mod = True

                        studio_list = find_nodes(tree, "studio")
                        if len(studio_list) > 0:
                            for studio in studio_list:
                                is_del = False
                                for del_tag in tag_data["delete"]:
                                    if del_tag == str(studio.text):
                                        remove_node(tree.getroot(), studio)
                                        xlog.info("删除工作室: '" + del_tag + "'")
                                        is_del = True
                                        mod = True

                                if not is_del:
                                    for rep_tag in tag_data["replace"]:
                                        if rep_tag["original"] == str(
                                                studio.text):
                                            change_node_text(
                                                studio, rep_tag["result"])
                                            xlog.info("替换工作室: '" +
                                                      rep_tag["original"] +
                                                      "' ==> '" +
                                                      rep_tag["result"] + "'")
                                            mod = True

                        maker_list = find_nodes(tree, "maker")
                        if len(maker_list) > 0:
                            for maker in maker_list:
                                is_del = False
                                for del_tag in tag_data["delete"]:
                                    if del_tag == str(maker.text):
                                        remove_node(tree.getroot(), maker)
                                        xlog.info("删除制造商: '" + del_tag + "'")
                                        is_del = True
                                        mod = True

                                if not is_del:
                                    for rep_tag in tag_data["replace"]:
                                        if rep_tag["original"] == str(
                                                maker.text):
                                            change_node_text(
                                                maker, rep_tag["result"])
                                            xlog.info("替换制造商: '" +
                                                      rep_tag["original"] +
                                                      "' ==> '" +
                                                      rep_tag["result"] + "'")
                                            mod = True

                        # 处理重复元素
                        genre_list = find_nodes(tree, "genre")
                        if len(genre_list) > 0:
                            record_genre = []
                            for genre in genre_list:
                                genre_text = str(genre.text)
                                if record_genre.count(genre_text) > 0:
                                    xlog.info("删除重复风格: '" + genre_text + "'")
                                    remove_node(tree.getroot(), genre)
                                    mod = True
                                else:
                                    record_genre.append(genre_text)

                        tag_list = find_nodes(tree, "tag")
                        if len(tag_list) > 0:
                            record_tag = []
                            for t in tag_list:
                                t_text = str(t.text)
                                if record_tag.count(t_text) > 0:
                                    xlog.info("删除重复标签: '" + t_text + "'")
                                    remove_node(tree.getroot(), t)
                                    mod = True
                                else:
                                    record_tag.append(t_text)

                        studio_list = find_nodes(tree, "studio")
                        if len(studio_list) > 0:
                            record_studio = []
                            for studio in studio_list:
                                studio_text = str(studio.text)
                                if record_studio.count(studio_text) > 0:
                                    xlog.info("删除重复工作室: '" + studio_text + "'")
                                    remove_node(tree.getroot(), studio)
                                    mod = True
                                else:
                                    record_studio.append(studio_text)

                        maker_list = find_nodes(tree, "maker")
                        if len(maker_list) > 0:
                            record_maker = []
                            for maker in maker_list:
                                maker_text = str(maker.text)
                                if record_maker.count(maker_text) > 0:
                                    xlog.info("删除重复制造商: '" + studio_text + "'")
                                    remove_node(tree.getroot(), maker)
                                    mod = True
                                else:
                                    record_maker.append(maker_text)

                    if mod:
                        xlog.info("重新写入 " + file)
                        xlog.info(
                            "------------------------------------------------")
                        write_nfo(tree, file)

        xlog.debug("所有操作处理完成。")
    else:
        xlog.error("没有设置翻译引擎")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="自动翻译 nfo 文件")
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
        default="all",
        required=False,
        help="打印日志",
    )
    ap.add_argument("-n",
                    "--noadd",
                    action="store_true",
                    required=False,
                    help="禁止添加原始标题节点")

    ap.add_argument("-t",
                    "--tag",
                    action="store_true",
                    required=False,
                    help="清洗标签")

    args = vars(ap.parse_args())
    dir_path = args["input"]
    hyphen = args["hyphen"]
    log = args["log"]
    no_add = args["noadd"]
    tag = args["tag"]
    if os.path.isdir(dir_path):
        if not dir_empty(dir_path):
            detect_walk(dir_path, hyphen, log, no_add, tag)
