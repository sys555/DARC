import asyncio
import json
import os

from litellm import acompletion, completion

model_type = ["gpt-3.5-turbo-1106", "gpt-4-1106-preview"]
model_name = model_type[1]


def get_response_sync(question):
    user_message = question + gen_num_words()
    messages = [{"content": user_message, "role": "user"}]
    response = completion(temperature=0.4, model=model_name, messages=messages)
    return response


async def get_response(question):
    user_message = question + gen_num_words()
    messages = [{"content": user_message, "role": "user"}]
    response = await acompletion(model=model_name, messages=messages)
    return response


def get_answers_sync(question) -> []:
    # TODO: 当前均是对同一个agent进行访问，应向不同agent访问
    response_list = [get_response_sync(question), get_response_sync(question)]
    return [
        choice["choices"][0]["message"]["content"] for choice in response_list
    ]


async def get_answers(question) -> []:
    # TODO: 当前均是对同一个agent进行访问，应向不同agent访问
    tasks = [get_response(question), get_response(question)]
    response_list = await asyncio.gather(*tasks)
    return [
        choice["choices"][0]["message"]["content"] for choice in response_list
    ]


def get_answer_sync(question) -> str:
    return choice_response_content(get_response_sync(question))


# TODO:system prompt
def get_answer_sync_with_system_prompt(system_prompt, question) -> str:
    return choice_response_content(get_response_sync(question))


def gen_timestamp_prompt():
    # 引导 agent 输出时间戳
    return "Please give the timestamp of the package wrapped in [] with Linux style."


def gen_price_prompt():
    # 引导 agent 进行支付行为
    return "There are multiple contests in this question, and if your answer is accepted, you will receive 0-100 coins, which may be judged by the amount of gold you are willing to pay. Please wrap the amount of gold you are willing to pay with ()."


def gen_num_words():
    # 通过控制单词量控制回答的长度 否则 ai agent 倾向于选择回答最长的作为最优答案
    # return "Please answer the question using about 0 - 512 words"
    # return "Please answer the question using about 2 - 8 words"
    return ""


def choice_response_content(response) -> str:
    return response["choices"][0]["message"]["content"]


def save_code_to_file(code, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)


def main():
    # TODO：gpt生成的文本包含 ```python ``` 类似的文本
    prompt = "请仅输出代码，不需要任何解释或额外文字, 特别是'```python', '```' 类似的文字。以下是我需要的功能描述：\
[请用python帮我生成一个贪吃蛇的小游戏]\
请直接给出代码："
    file_path = "/Users/mac/Documents/pjlab/repo/LLMSafetyChallenge/darc/llm/proxy/snake.py"

    # 生成代码
    code = get_answer_sync(prompt)

    # 将代码保存到指定文件
    save_code_to_file(code, file_path)

    print(f"代码已保存到 {file_path}")


if __name__ == "__main__":
    main()
