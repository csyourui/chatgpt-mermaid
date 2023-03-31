'''
Author: yourui
Date: 2023-03-31
Copyright (c) 2023 by yourui. All rights reserved.
'''
# utils.py
import re
import requests
import logging 
import json

def remove_mermaid_markers(text):
    pattern = r'(^|\n)```(.*?)\n|\n```($|\n)'
    return re.sub(pattern, '', text, flags=re.MULTILINE)

# replace_chinese_punctuation 替换中文符号为英文符号
def replace_chinese_punctuation(text):
    punctuation_mapping = {
        "，": ",",
        "；": ";",
        "。": ".",
        "？": "?",
        "！": "!",
        "：": ":",
        "“": "\"",
        "”": "\"",
        "‘": "'",
        "’": "'",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "［": "[",
        "］": "]",
        "｛": "{",
        "｝": "}",
        "—": "-",
    }

    translation_table = str.maketrans(punctuation_mapping)
    return text.translate(translation_table)


# 读取JSON文件
def read_json_map(filename):
    with open(filename) as f:
        data = json.load(f)
    prompt_map = {}
    for item in data:
        prompt_map[item['type']] = item['prompt']
    return prompt_map


def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content




def get_geoip():
    response = requests.get('https://ipapi.co/json/', timeout=5)
    try:
        data = response.json()
    except:
        data = {
            "error": True,
            "reason" : "连接ipapi失败"
        }
    if "error" in data.keys():
        logging.warning(f"无法获取IP地址信息。\n{data}")
        if data['reason'] == "RateLimited":
            return f"获取IP地理位置失败，因为达到了检测IP的速率限制。聊天功能可能仍然可用，但请注意，如果您的IP地址在不受支持的地区，您可能会遇到问题。"
        else:
            return f"获取IP地理位置失败。原因：{data['reason']}。你仍然可以使用聊天功能。"
    else:
        ip = data['ip']
        text = f"**您的ip地址{ip}**"
        logging.info(text)
        return text