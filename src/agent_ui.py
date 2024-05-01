from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
import tools
from config import Config
import gradio as gr
import json


def load_llm():
    llm = Llama.from_pretrained(
        repo_id=Config.MODEL_NAME,
        filename=Config.MODEL_REVISION,
        chat_format="functionary-v2",
        tokenizer=LlamaHFTokenizer.from_pretrained("meetkai/functionary-small-v2.4-GGUF"),
        n_gpu_layers=0,
    )
    return llm


tools_provided=tools.get_tools()
llm=load_llm()

def get_response(message):
    global tools_provided,llm
    result = llm.create_chat_completion(
      messages = message,
      tools=tools_provided,
      tool_choice="auto"
    )
    if "tool_calls" in result["choices"][0]["message"].keys():
        func=result["choices"][0]["message"]["tool_calls"][0]['function']
        if func["name"]=="swap_agent":
            #Then the swap function goes here
            args=json.loads(func["arguments"])
            tok1=args["token1"]
            tok2=args["token2"]
            res=tools.swap_coins(tok1,tok2)
            return {"role":"assistant","content":res},"1"
    
    return result["choices"][0]["message"],"0"

if __name__ == '__main__':
    messages=[{"role": "system", "content": "Don't make assumptions about the value of the arguments for the function thy should always be supplied by the user and do not alter the value of the arguments . Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous .and you only need the value of token1 we dont need the value of token2"}]
    def respond(message, chat_history):
        global messages
        c={"role":"user",
            "content":str(message)}
        messages.append(c)
        res,flag=get_response(messages)
        messages.append({"role":res["role"],"content":res["content"]})
        if flag=="1":
            messages=messages[:1]
        chat_history.append((message, res["content"]))
        return "", chat_history
    with gr.Blocks() as demo:
        with gr.Tab("chat"):
          chatbot = gr.Chatbot(height=240) #just to fit the notebook
          msg = gr.Textbox(label="Prompt")
          btn = gr.Button("Submit")
          clear = gr.ClearButton(components=[msg, chatbot], value="Clear console")
    
        btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot]) #Press enter to submit
    gr.close_all()
    demo.launch(share=True)


    


