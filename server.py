'''
Author: yourui
Date: 2023-03-31
Copyright (c) 2023 by yourui. All rights reserved.
'''
import gradio as gr
import openai
import logging
import os
import re
from urllib.parse import quote

from utils import *

openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_map = read_json_map("mermaid_fomat_prompt.json")
html_content = read_html_file("mermaid.html")

# 自定义日志格式，包括时间戳
log_format = '%(asctime)s - %(levelname)s - %(message)s'

# 配置日志记录器
logging.basicConfig(format=log_format, level=logging.INFO)


def show_mermaid(text):
    mermaid_code = text
    template = html_content.replace('${MERMAID_CODE}', mermaid_code)
    encoded_html = quote(template)
    res = f'<iframe src="data:text/html;charset=utf-8,{encoded_html}" style="width: 100%; height: 500px; border: none;"></iframe>'
    return res


system_propmot = '你是chatgpt,你需要使用mermaid.js库帮助我进行一些工作'
user_propmot = '请根据下面的描述按照你的理解扩充内容,生成mermaid的代码,输出前请务必使用mermaid的语法修改错误\n----描述开始:\n'
user_propmot_2 = '\n----描述结束\n请不要写任何解释, 其他文字或者Note,只需回复Mermiad图的文本即可,请把所有的中文符号都转成英文符号, 你需要使用的格式是:\n'


def show_outputs(text, mermaid_format, use_input_text=False):
    if not use_input_text:
        prompt = user_propmot + text + user_propmot_2 + mermaid_format + \
            "\n有一个关于该格式的例子如下:\n" + prompt_map[mermaid_format]
        logging.info("prompt:\n" + prompt)
        response = openai.ChatCompletion.create(
            engine="bgioaigpt",
            messages=[{"role": "system", "content": system_propmot},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        resp_content = response.choices[0].message.content
        logging.info("raw resp text:\n" + resp_content)

        mermaid_content = resp_content
        # handle
        mermaid_content = remove_mermaid_markers(mermaid_content)
        mermaid_content = replace_chinese_punctuation(mermaid_content)
        markdown_text = resp_content
    else:
        # handle
        mermaid_content = text
        markdown_text = "```mermaid\n" + text + "\n```"

    # after handle
    logging.info("print:\n" + mermaid_content)
    mermaid_html = show_mermaid(mermaid_content)
    markdown_text = markdown_text
    return mermaid_html, markdown_text


def direct_show_btn_click(text):
    return show_outputs(text, mermaid_format="NONE", use_input_text=True)


def generate_btn_click(text, format):
    return show_outputs(text, mermaid_format=format, use_input_text=False)


with gr.Blocks() as iface:
    with gr.Tab(elem_id="flow_chart_assistant", label="Flow Chart"):
        gr.Markdown("你可以输入描述让chatgpt为你作图, 也可以直接贴上Mermaid的代码作图")
        with gr.Row():
            with gr.Column():
                txt = gr.Textbox(value="graph LR\n\tA --- B\n\tB-->C[fa:fa-ban forbidden]\n\tB-->D(fa:fa-spinner);", label="talk or show your code")
                # txt = gr.Textbox(value="停车场收费系统的数据结构", label="talk or show your code")
                with gr.Row():
                    generate_btn = gr.Button(value="问问GPT吧")
                    direct_show_btn = gr.Button(
                        value="显示流程图", label="直接贴Mermaid代码使用")
                format = gr.Radio(["Flowcharts", "Sequence diagrams", "Class diagrams", "State diagrams",
                                  "Entity Relationship Diagrams"], value="Flowchart", label="Mermaid format")
            with gr.Column():
                html = gr.HTML()
                markdown = gr.Markdown()
        with gr.Accordion("See Details"):
            gr.Markdown(get_geoip(), elem_id="status_display", open="True")
        generate_btn.click(generate_btn_click, inputs=[
                           txt, format], outputs=[html, markdown])
        direct_show_btn.click(direct_show_btn_click, inputs=[
                              txt], outputs=[html, markdown])
    with gr.Tab(elem_id="test_assistant", label="Test"):
        gr.Markdown("test")
        with gr.Accordion("See Details"):
            gr.Markdown(get_geoip(), elem_id="status_display", open="True")

if __name__ == "__main__":
    iface.launch(inbrowser=True)
