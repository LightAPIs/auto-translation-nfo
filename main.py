# -*- coding: utf-8 -*-
import os
import argparse
import time
import shutil
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


def backup_file(in_path):
    backup_status = False
    dir_path = os.path.join(os.getcwd(), "backup")
    if (not os.path.exists(dir_path)):
        os.makedirs(dir_path)
    if os.path.exists(in_path):
        try:
            shutil.copy(in_path, dir_path)
            backup_status = True
        except IOError as e:
            backup_status = False
            print("存在权限问题，复制文件失败！ %s" % e)

    return backup_status


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


def detect_walk(dir_path, elements, log, backup, tag):
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
    xlog.debug("处理元素节点: " + str(elements))
    xlog.debug("日志级别: " + log)
    xlog.debug("自动备份: " + str(backup))
    xlog.debug("替换标签: " + str(tag))
    xlog.debug("************************************************")

    if len(elements) > 0:
        config = Config()
        engine_type = config.engine_type()
        has_engine = False
        engine = False
        if engine_type == "baidu":
            baidu_app_id = config.baidu_app_id()
            baidu_key = config.baidu_key()
            baidu_from = config.baidu_from()
            baidu_to = config.baidu_to()
            if baidu_app_id and baidu_key:
                has_engine = True
                engine = Baidu(baidu_app_id, baidu_key, baidu_from, baidu_to)
        elif engine_type == "caiyun":
            caiyun_token = config.caiyun_token()
            caiyun_trans_type = config.caiyun_trans_type()
            if caiyun_token:
                has_engine = True
                engine = Caiyun(caiyun_token, caiyun_trans_type)

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
                        if backup:
                            if backup_file(file):
                                xlog.info("备份 " + file)
                            else:
                                xlog.error("备份失败: " + file)
                        xlog.info("读取 " + file)
                        tree = read_nfo(file)
                        mod = False

                        for ele in elements:
                            ele_name = ele.strip()
                            ele_list = find_nodes(tree, ele_name)
                            if len(ele_list) > 0:
                                ele_text = str(ele_list[0].text)
                                if ele_text != "None":
                                    xlog.info("原 " + ele_name + ": " +
                                              ele_text)
                                    time.sleep(1)
                                    trans_ele = engine.translate(ele_text)
                                    change_node_text(ele_list[0], trans_ele)
                                    xlog.info("新 " + ele_name + ": " +
                                              trans_ele)
                                    mod = True

                        if tag:
                            genre_list = find_nodes(tree, "genre")
                            if len(genre_list) > 0:
                                for genre in genre_list:
                                    is_del = False
                                    for del_tag in tag_data["delete"]:
                                        if del_tag == str(genre.text):
                                            remove_node(tree.getroot(), genre)
                                            xlog.info("删除风格: '" + del_tag +
                                                      "'")
                                            is_del = True
                                            mod = True
                                            break

                                    if not is_del:
                                        for rep_tag in tag_data["replace"]:
                                            if rep_tag["original"] == str(
                                                    genre.text):
                                                change_node_text(
                                                    genre, rep_tag["result"])
                                                xlog.info("替换风格: '" +
                                                          rep_tag["original"] +
                                                          "' ==> '" +
                                                          rep_tag["result"] +
                                                          "'")
                                                mod = True
                                                break

                            tag_list = find_nodes(tree, "tag")
                            if len(tag_list) > 0:
                                for t in tag_list:
                                    is_del = False
                                    for del_tag in tag_data["delete"]:
                                        if del_tag == str(t.text):
                                            remove_node(tree.getroot(), t)
                                            xlog.info("删除标签: '" + del_tag +
                                                      "'")
                                            is_del = True
                                            mod = True
                                            break

                                    if not is_del:
                                        for rep_tag in tag_data["replace"]:
                                            if rep_tag["original"] == str(
                                                    t.text):
                                                change_node_text(
                                                    t, rep_tag["result"])
                                                xlog.info("替换标签: '" +
                                                          rep_tag["original"] +
                                                          "' ==> '" +
                                                          rep_tag["result"] +
                                                          "'")
                                                mod = True
                                                break

                            studio_list = find_nodes(tree, "studio")
                            if len(studio_list) > 0:
                                for studio in studio_list:
                                    is_del = False
                                    for del_tag in tag_data["delete"]:
                                        if del_tag == str(studio.text):
                                            remove_node(tree.getroot(), studio)
                                            xlog.info("删除工作室: '" + del_tag +
                                                      "'")
                                            is_del = True
                                            mod = True
                                            break

                                    if not is_del:
                                        for rep_tag in tag_data["replace"]:
                                            if rep_tag["original"] == str(
                                                    studio.text):
                                                change_node_text(
                                                    studio, rep_tag["result"])
                                                xlog.info("替换工作室: '" +
                                                          rep_tag["original"] +
                                                          "' ==> '" +
                                                          rep_tag["result"] +
                                                          "'")
                                                mod = True
                                                break

                            maker_list = find_nodes(tree, "maker")
                            if len(maker_list) > 0:
                                for maker in maker_list:
                                    is_del = False
                                    for del_tag in tag_data["delete"]:
                                        if del_tag == str(maker.text):
                                            remove_node(tree.getroot(), maker)
                                            xlog.info("删除制造商: '" + del_tag +
                                                      "'")
                                            is_del = True
                                            mod = True
                                            break

                                    if not is_del:
                                        for rep_tag in tag_data["replace"]:
                                            if rep_tag["original"] == str(
                                                    maker.text):
                                                change_node_text(
                                                    maker, rep_tag["result"])
                                                xlog.info("替换制造商: '" +
                                                          rep_tag["original"] +
                                                          "' ==> '" +
                                                          rep_tag["result"] +
                                                          "'")
                                                mod = True
                                                break

                            # 处理重复元素
                            genre_list = find_nodes(tree, "genre")
                            if len(genre_list) > 0:
                                record_genre = []
                                for genre in genre_list:
                                    genre_text = str(genre.text)
                                    if record_genre.count(genre_text) > 0:
                                        xlog.info("删除重复风格: '" + genre_text +
                                                  "'")
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
                                        xlog.info("删除重复工作室: '" + studio_text +
                                                  "'")
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
                                        xlog.info("删除重复制造商: '" + studio_text +
                                                  "'")
                                        remove_node(tree.getroot(), maker)
                                        mod = True
                                    else:
                                        record_maker.append(maker_text)

                        if mod:
                            xlog.info("重新写入 " + file)
                            xlog.info("------------------------"
                                      "------------------------")
                            write_nfo(tree, file)

            xlog.debug("所有操作处理完成。")
        else:
            xlog.error("没有设置翻译引擎！")
    else:
        xlog.error("没有指定所需要翻译的元素节点！")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="自动翻译 nfo 文件")
    ap.add_argument("-i", "--input", required=True, help="输入工作目录的路径")
    ap.add_argument("-e",
                    "--elements",
                    default="",
                    required=True,
                    help="需要翻译的元素节点，多个时以|分隔")
    ap.add_argument(
        "-l",
        "--log",
        choices=["error", "all", "none"],
        default="all",
        required=False,
        help="打印日志级别",
    )
    ap.add_argument("-b",
                    "--backup",
                    action="store_true",
                    required=False,
                    help="翻译前备份原文件")
    ap.add_argument("-t",
                    "--tag",
                    action="store_true",
                    required=False,
                    help="启用替换标签功能")

    args = vars(ap.parse_args())
    dir_path = args["input"]
    elements = args["elements"].split("|")
    log = args["log"]
    backup = args["backup"]
    tag = args["tag"]
    if os.path.isdir(dir_path):
        if not dir_empty(dir_path):
            detect_walk(dir_path, elements, log, backup, tag)
