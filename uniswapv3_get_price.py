from web3 import Web3, HTTPProvider
import json, os, time

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
pool_address = factory.functions.getPool(DAI_ADDRESS, WETH_ADDRESS, 500).call() # DAI-WETH 0.05% pool address
pool = w3.eth.contract(address = pool_address , abi = pool_abi)

print("token0:", pool.functions.token0().call())
print("token1:", pool.functions.token1().call())

slot0 = pool.functions.slot0().call()
sqrtPriceX96 = slot0[0]
tick = slot0[1]
print("sqrtPriceX96:", sqrtPriceX96)
print("tick:", tick)

price = sqrtPriceX96**2 / 2**192

# In Uniswap V2, price is reserve[1]/reserve[0].
# Or token1Price in Uniswap SDK and subgraph.
print("price:", price)

# Equivalently, you can calculate from the tick. 
# The value is slightly different due to the error of approximation
# algorithm of log in the Uniswap contract.
price_from_tick = (1.0001)**tick
print("price from tick:", price_from_tick)