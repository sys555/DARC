from darc.agent.llm.proxy.query import get_answer_sync

# Read the prompt from output.txt
with open('./output.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()

# Prepare the prompt
prompt = f"""
请分析以下讨论结果，并根据讨论结果给出产品的实现python代码: 
{prompt}
"""

# Get the answer
answer = get_answer_sync(question=prompt)

# Write the answer to flame.py
with open("./flame.py", "w", encoding='utf-8') as file:
    file.write(answer)