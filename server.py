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
from template.diagrams import *
from utils import *

openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

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


system_prompt = 'You are an AI assistant that helps help me with some work, you need to use the mermaid.js library'
user_prompt = 'Write a mermaid code for diagrams with the following instructions,\n'
user_prompt_suffix = '\nDo not write any explanations, other text, or notes, just reply to the text of the Mermead diagram. Use English punctuation. You need to return :\n'


def show_outputs(text, mermaid_format, use_input_text=False):
    if not use_input_text:
        prompt = user_prompt + text + user_prompt_suffix + mermaid_format + \
            "\nan example is following:\n" + mermaid_samples[mermaid_format].strip("\n")
        logging.info("prompt:\n" + prompt)
        response = openai.ChatCompletion.create(
            engine="bgioaigpt",
            messages=[{"role": "system", "content": system_prompt},
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
        mermaid_content = replace_chinese_punctuation_with_english(mermaid_content)
        markdown_text = replace_chinese_punctuation_with_english(resp_content)
    else:
        # handle
        mermaid_content = text
        markdown_text = "```mermaid\n" + text.strip("\n") + "\n```"

    # after handle
    logging.info("print:\n" + mermaid_content)
    mermaid_html = show_mermaid(mermaid_content)
    markdown_text = markdown_text
    return mermaid_html, markdown_text

def sample_btn_click(format):
    #text show to
    html, markdown = show_outputs(mermaid_samples[format], mermaid_format=format, use_input_text=True)
    return mermaid_samples[format].strip("\n"), html, markdown

def direct_show_btn_click(text):
    return show_outputs(text, mermaid_format="NONE", use_input_text=True)


def generate_btn_click(text, format):
    return show_outputs(text, mermaid_format=format, use_input_text=False)


with gr.Blocks() as iface:
    with gr.Tab(elem_id="flow_chart_assistant", label="Flow Chart"):
        gr.Markdown("你可以输入描述让chatgpt为你作图, 也可以直接贴上Mermaid的代码作图")
        with gr.Row():
            with gr.Column():
                txt = gr.Code(value="把大象放进冰箱要几步", label="mermaid")
                # txt = gr.Textbox(value="停车场收费系统的数据结构", label="talk or show your code")
                with gr.Row():
                    sample_btn = gr.Button(value="样例流程图")
                    generate_btn = gr.Button(value="问问GPT吧")
                    direct_show_btn = gr.Button(
                        value="显示流程图", label="直接贴Mermaid代码使用")
                format = gr.Radio(list(mermaid_samples.keys()), value="Flowchart", label="Mermaid format")
            with gr.Column():
                html = gr.HTML(value = "mermaid fig")
                markdown = gr.Markdown(value = "mermaid code")
        with gr.Accordion("See Details"):
            gr.Markdown(get_geoip(), elem_id="status_display", open="True")

        sample_btn.click(sample_btn_click, inputs=[format], outputs=[txt, html, markdown])
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
