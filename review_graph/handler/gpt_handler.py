from langchain_openai import ChatOpenAI

class GPTHandler:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4-turbo", temperature=0)

    def invoke(self, messages, max_tokens=4096):
        return self.llm.invoke(messages, config={"max_tokens": max_tokens}).content.strip()