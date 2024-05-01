from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
import tools
from config import Config
import json


def load_llm():
    llm = Llama.from_pretrained(
        repo_id=Config.MODEL_NAME,
        filename=Config.MODEL_REVISION,
        chat_format="functionary-v2",
        tokenizer=LlamaHFTokenizer.from_pretrained("meetkai/functionary-small-v2.4-GGUF"),
        n_gpu_layers=0
    )
    return llm


tools_provided=tools.get_tools()
llm=load_llm()


def get_response(message):
    global tools_provided,llm
    result = llm.create_chat_completion(
      messages = message,
      tools=tools_provided,
      tool_choice="auto",
        temperature=0.1
        )
    if "tool_calls" in result["choices"][0]["message"].keys():
        func=result["choices"][0]["message"]["tool_calls"][0]['function']
        if func["name"]=="swap_agent":
            #Then the swap function goes here
            args=json.loads(func["arguments"])
            res=tools.swap_coins(args["token1"],args["token2"])
            return {"role":"assistant","content":res["response"]},"1"
    
    return result["choices"][0]["message"],"0"

if __name__ == '__main__':
    message=[]
    while True:
        text = input("enter your query?")
        print(text)
        c={"role":"user",
            "content":str(text)}
        message.append(c)
        res,flag=get_response(message)
        message.append({"role":res["role"],"content":res["content"]})
        if flag=="1":
            message=[]
        print(res)


    


