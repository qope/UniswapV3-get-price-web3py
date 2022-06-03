from web3 import Web3, HTTPProvider
import json, os, time, numpy

RPC_URL = "https://polygon-rpc.com" # Polygon network RPC address

# You can find these three addresses below at https://docs.uniswap.org/protocol/reference/deployments.
# These addresses are common to all chains.
FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984" 
QUOTER_ADDRESS = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6" 
SWAP_ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564" 

DAI_ADDRESS = "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063" # DAI address in polygon network
WETH_ADDRESS ="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"# WETH address in polygon network


with open("abis/UniswapV3Factory.json", "r") as f:
    factory_abi = json.loads(f.read())
with open("abis/UniswapV3Pool.json", "r") as f:
    pool_abi = json.loads(f.read())
with open("abis/Quoter.json", "r") as f:
    quoter_abi = json.loads(f.read())
with open("abis/SwapRouter.json", "r") as f:
    swap_router_abi =json.loads(f.read())
with open("abis/IERC20.json", "r") as f:
    ierc20_abi =json.loads(f.read())

w3 = Web3(HTTPProvider(RPC_URL))
factory = w3.eth.contract(address = FACTORY_ADDRESS , abi = factory_abi)
quoter = w3.eth.contract(address = QUOTER_ADDRESS , abi = quoter_abi)
router = w3.eth.contract(address = SWAP_ROUTER_ADDRESS , abi = swap_router_abi)
dai = w3.eth.contract(address = DAI_ADDRESS, abi = ierc20_abi)

# pool fee is one of  500 (0.05%), 3000 (0.30%), 100000 (1%).
pool_fee = 500

# amount you want to swap
amount = w3.toWei("0.01", "ether")

# estimate output amount
sqrtPriceLimitX96 = 0 # this value is ignored if it is set to 0.
estimated_amount_out = quoter.functions.quoteExactInputSingle(DAI_ADDRESS, WETH_ADDRESS, pool_fee , amount, sqrtPriceLimitX96).call()

input("You will get {} WETH. Are you OK?".format(w3.fromWei(estimated_amount_out, "ether")))

# approve Dai
my_address = os.getenv("ADDRESS")
my_private_key = os.getenv("PRIVATE_KEY")
nonce = w3.eth.get_transaction_count(my_address)
tx_approve = dai.functions.approve(SWAP_ROUTER_ADDRESS, amount).buildTransaction(\
    {'chainId': 137, \
     'type': 2, \
     'gas': 10**6, \
    'maxFeePerGas': w3.toWei('100', 'gwei'),\
    'nonce': nonce, })
signed_tx_approve = w3.eth.account.sign_transaction(tx_approve, private_key = my_private_key)
result = w3.eth.send_raw_transaction(signed_tx_approve.rawTransaction)
print(result.hex())

# swap dai to weth
deadline = int(time.time() + 60*10) # We set deadline after 10 min.
amountOutMinimum = int(estimated_amount_out*0.99) # We set slippage as 1%.
sqrtPriceLimitX96 = 0 # this value is ignored if it is set to 0.
params = [DAI_ADDRESS, WETH_ADDRESS, pool_fee, my_address, deadline, amount, amountOutMinimum, sqrtPriceLimitX96]
tx_swap = router.functions.exactInputSingle(params).buildTransaction(\
    {'chainId': 137, \
     'type': 2, \
     'gas': 10**6, \
    'maxFeePerGas': w3.toWei('100', 'gwei'),\
    'nonce': nonce + 1, })
signed_tx_swap = w3.eth.account.sign_transaction(tx_swap, private_key = my_private_key)
result = w3.eth.send_raw_transaction(signed_tx_swap.rawTransaction)
print(result.hex())
