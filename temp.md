# 调用deepseek的方法
from langchain_openai import ChatOpenAI
llm_deepseek=ChatOpenAI(
    temperature=0,
    model="deepseek-chat",  
    base_url="https://api.deepseek.com",
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    max_tokens=8192
)

pim-engine/src/converters/pim_to_psm_gemini.py  参考这个文件写个pim-engine/src/converters/pim_to_psm_deepseek.py

参考test_simple_pim_conversion写个关于pim_to_psm_deepseek.py的单元测试

# 成功验证
单元测试通过
