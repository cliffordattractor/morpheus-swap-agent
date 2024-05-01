import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Configuration object
class Config:
    # Model configuration
    MODEL_NAME = "meetkai/functionary-small-v2.4-GGUF"
    MODEL_REVISION = "functionary-small-v2.4.Q4_0.gguf"
    MODEL_PATH = "model/"+MODEL_REVISION
    DOWNLOAD_DIR = "model"
    # API endpoints
    INCH_URL = "https://api.1inch.dev/token"
    QUOTE_URL = "https://api.1inch.dev/swap"
    APIBASEURL = f"https://api.1inch.dev/swap/v6.0/"
    HEADERS = { "Authorization": "Bearer WvQuxaMYpPvDiiOL5RHWUm7OzOd20nt4", "accept": "application/json" }
    WEB3RPCURL = {"56":"https://bsc-dataseed.binance.org","42161":"https://arb1.arbitrum.io/rpc","137":"https://polygon-rpc.com","1":"https://cloudflare-eth.com","10":"https://mainnet.optimism.io"}
    NATIVE_TOKENS={"137":"MATIC","56":"BNB","1":"ETH","42161":"ETH","10":"ETH"}
    