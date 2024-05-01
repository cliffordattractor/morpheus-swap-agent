import requests
import logging
from config import Config
from web3 import Web3
import time



def search_tokens(query, chain_id, limit=1, ignore_listed="false"):
    endpoint = f"/v1.2/{chain_id}/search"
    params = {
        "query": query,
        "limit": limit,
        "ignore_listed": ignore_listed
    }
    response = requests.get(Config.INCH_URL + endpoint, params=params, headers=Config.HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to search tokens. Status code: {response.status_code}")
        return None

def validate_swap(token1,token2,chainid):

    native=Config.NATIVE_TOKENS
    if native[str(chainid)].lower()==token1.lower():
        t1=[{'symbol':native[str(chainid)],'address':'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'}]
    else:
        t1=search_tokens(token1,chainid)
        time.sleep(2)
    if native[str(chainid)].lower()==token2.lower():
        t2=[{'symbol':native[str(chainid)],'address':'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'}]
    else:
        t2=search_tokens(token2,chainid)
        time.sleep(2)
    if not t1 or not t2:
        return 0,"","","",""
    
    return 1,t1[0]['address'],t1[0]['symbol'],t2[0]['address'],t2[0]['symbol']

def get_quote(token1,token2,amount_in_wei,chain_id):
    endpoint = f"/v6.0/{chain_id}/quote"
    params = {
    "src": token1,
    "dst": token2,
    "amount": int(amount_in_wei)
    }
    response = requests.get(Config.QUOTE_URL + endpoint, params=params, headers=Config.HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to search tokens. Status code: {response.status_code}")
        return None
    
def swap_coins(token1,token2,amount,chain_id):
    """Swap two cryto coins with each other"""
    flag,t1_a,t1_id,t2_a,t2_id=validate_swap(token1,token2,chain_id)
    if flag==0:
        return "please restart the conversation and use coins supported on the selected chain","assistant"
    else:
        time.sleep(2)
        web3 = Web3(Web3.HTTPProvider(Config.WEB3RPCURL[str(chain_id)]))
        amount_in_wei=web3.to_wei(amount,'ether')
        result=get_quote(t1_a,t2_a,amount_in_wei,chain_id)
        if result:
            price=result["dstAmount"]
            t2_quote=web3.from_wei(int(price),'ether')
        else:
            return "please try again with coins in the same network","assistant"
        return {
            "src":t1_id,
            "dst":t2_id,
            "src_address":t1_a,
            "dst_address":t2_a,
            "amount":amount,
            "quote":float(t2_quote)
        },"swap"


def get_tools():
    """Return a list of tools for the agent."""
    return [
        {
           "type": "function",
        "function": {
            "name": "swap_agent",
            "description": "swap two crypto currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "token1": {
                        "type": "string",
                        "description": "name of the crypto currency to off load or to sell"
                    },
                    "token2": {
                        "type": "string",
                        "description": "name of the crypto currency to buy"
                    },
                      "value": {
                        "type": "string",
                        "description": "Value or amount of the crypto currency to offload"
                    }
                },
                "required": ["token1","token2","value"]
            }
        }
    }     
    ]
