from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tools
from config import Config
import json


def load_llm():
    llm = Llama(
        model_path=Config.MODEL_PATH,
        chat_format="functionary-v2",
        tokenizer=LlamaHFTokenizer.from_pretrained("meetkai/functionary-small-v2.4-GGUF"),
        n_gpu_layers=0,
        n_batch=4000,
        n_ctx=4000
    )
    return llm


tools_provided=tools.get_tools()
llm=load_llm()
messages=[]
sub_messages=[]

def apiRequestUrl(methodName, queryParams,chain_id):
    base_url=Config.APIBASEURL+str(chain_id)
    return f"{base_url}{methodName}?{'&'.join([f'{key}={value}' for key, value in queryParams.items()])}"

def checkAllowance(tokenAddress, walletAddress,chain_id):
    url = apiRequestUrl("/approve/allowance", {"tokenAddress": tokenAddress, "walletAddress": walletAddress},chain_id)
    response = requests.get(url, headers=Config.HEADERS)
    data = response.json()
    return data

def approvetransaction(token_address, chain_id, amount=None):
    # Assuming you have defined apiRequestUrl() function to construct the URL
    url = apiRequestUrl("/approve/transaction", {"tokenAddress": token_address, "amount": amount } if amount else {"tokenAddress": token_address },chain_id)
    response = requests.get(url, headers=Config.HEADERS)
    transaction = response.json()
    return transaction


def buildTxForSwap(swapParams,chain_id):
    url = apiRequestUrl("/swap", swapParams, chain_id)
    swapTransaction = requests.get(url,  headers=Config.HEADERS).json()
    return swapTransaction

def get_response(message,chain_id):
    global tools_provided,llm,messages,sub_messages
    prompt=[{"role": "system", "content": "Don't make assumptions about the value of the arguments for the function thy should always be supplied by the user and do not alter the value of the arguments . Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous .and you only need the value of token1 we dont need the value of token2"}]
    prompt.extend(message)
    result = llm.create_chat_completion(
      messages = prompt,
      tools=tools_provided,
      tool_choice="auto"
    )
    if "tool_calls" in result["choices"][0]["message"].keys():
        func=result["choices"][0]["message"]["tool_calls"][0]['function']
        if func["name"]=="swap_agent":
            args=json.loads(func["arguments"])
            tok1=args["token1"]
            tok2=args["token2"]
            value=args["value"]
            res,role=tools.swap_coins(tok1,tok2,value,chain_id)
            messages.append({"role":"role","content":res})
            return res,role
    messages.append({"role":"assistant","content":result["choices"][0]["message"]['content']})
    sub_messages.append({"role":"assistant","content":result["choices"][0]["message"]['content']})
    return result["choices"][0]["message"]['content'],"assistant"

def get_status(flag):
    global messages,sub_messages
    if flag=="cancel":
        response = "you have cancelled the swap lets start again what do you want to do?"
        sub_messages=[]
        messages.append({"role":"assistant","content":response})
        sub_messages.append({"role":"assistant","content":response})
        return response
    elif flag=="success":
        response = "you have successfully swapped the coins do you want to do another swap?"
        sub_messages=[]
        messages.append({"role":"assistant","content":response})
        sub_messages.append({"role":"assistant","content":response})
        return response
    elif flag=="fail":
        response = "swap has failed lets start again"
        sub_messages=[]
        messages.append({"role":"assistant","content":response})
        sub_messages.append({"role":"assistant","content":response})
        return response



app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def generate_response():
    global messages,sub_messages
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            messages.append(prompt)
            sub_messages.append(prompt)
            chainid=data['chain_id']
            response,role = get_response(sub_messages,chainid)
            return jsonify({"role":role,"content":response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/tx_status', methods=['POST'])
def generate_tx_status():
    try:
        data = request.get_json()
        if 'flag' in data:
            prompt = data['flag']
            response = get_status(prompt)
            return jsonify({"role":"assistant","content":response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

@app.route('/messages', methods=['GET'])
def get_messages():
    global messages
    try:
        return jsonify({"messages":messages})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
@app.route('/allowance', methods=['POST'])
def check_allowance_api():
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            walletAddress=data['walletAddress']
            chain_id=data["chain_id"]
            res=checkAllowance(token,walletAddress,chain_id)
            return jsonify({"response":res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
@app.route('/approve', methods=['POST'])
def approve_api():
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            chain_id = data['chain_id']
            amount = data['amount']
            res=approvetransaction(token,chain_id,amount)
            return jsonify({"response":res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
@app.route('/swap', methods=['POST'])
def transaction_payload():   
    try:
        data = request.get_json()
        if 'src' in data:  
            token1=data['src']
            token2=data['dst']
            walletAddress=data['walletAddress']
            amount=data['amount']
            slippage=data['slippage']
            chain_id=data['chain_id']
            #private_key=data['privatekey']
            swapParams = {
                        "src": token1,
                        "dst": token2,
                        "amount": amount,
                        "from": walletAddress,
                        "slippage": slippage,
                        "disableEstimate": False,
                        "allowPartialFill": False,
                    }
            swapTransaction=buildTxForSwap(swapParams,chain_id)
            return swapTransaction
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    