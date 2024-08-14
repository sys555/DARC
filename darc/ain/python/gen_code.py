from darc.agent.llm.proxy.query import get_answer_sync

with(open('./output.txt', 'r', encoding='utf-8')) as file:
    prompt = file.read()
    
prompt = f"""
    请分析以下 讨论结果，并根据讨论结果给出产品的实现代码: 
    {prompt}
"""
print(get_answer_sync(question=prompt))