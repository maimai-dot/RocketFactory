# test_env.py
import os
from dotenv import load_dotenv
load_dotenv()

def test_llm():
    from crewai import LLM
    model = os.getenv("TEST_MODEL", "deepseek/deepseek-chat")
    llm = LLM(
        model=model,
        base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1"),
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    )
    response = llm.call("回复：成功")
    print("✅ LLM 连通性正常")
    print(response[:50])

if __name__ == "__main__":
    test_llm()