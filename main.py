# import requests
# import chainlit as cl


# @cl.on_chat_start
# async def on_chat_start():
#     await cl.Message(content = "Welcome TO Crypto Agent")
    
# @cl.on_message
# async def on_message(message:cl.Message):
#     user_input = message.content.strip().upper()
    
#     if user_input == "TOP 10":
#         url = "https://api.binance.com/api/v3/ticker/price"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         top_10 = "\n".join([f"{c[symb]}"])
        
# def get_crypto():
#     url = "https://api.binance.com/api/v3/ticker/price"
#     try:
#         response = requests.get(url)
#         data = response.json()
        
#         print("\n Top 10 Crypto Coins Prices On Binance : \n")
#         for coin in data[:10]:
#             print(f"{coin['symbol']} : {coin["price"]} USDT")
#     except requests.exceptions.RequestException as e:
#         print("Error Fetching Top 10 coin prices",e )
        
# def show_specific_coin_price(symbol):
#     url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             print(f"\n Current Price of {symbol.upper()} : {data["price"]} USDT")
#         else:
#             print("Invalid coin symbol onn Binance")
#     except requests.exceptions.RequestException as e:
#         print("Error Fetching Specific coin",e)     
        
# def main():
#     print("Live Crypto Price Agent Using Binance Api ")
    
#     get_crypto()
    
#     while True:
#         user_input = input("Enter A Coin Symbol (e.g BTCUSDT) or type 'exit'to quit:").strip()
#         if user_input.lower() == 'exit':
#             print("Exiting Program . Stay Updated With crypto")
#             break
#         if user_input:
#             show_specific_coin_price(user_input)
#         else:
#             print('Please enter a valid coin symbol')
            
# if __name__ == "__main__":
#     main()




from agents import Agent , Runner ,AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig
from dotenv import load_dotenv
import chainlit as cl
from tools import get_crypto
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Gemini APi Key is not defined")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client=client,
)

config = RunConfig(
    model = model,
    model_provider=client,
    tracing_disabled=True
)

agent = Agent(
    name = "Crypto Price Agent",
    instructions= "You are a helpful Agent that gives real time cryptocurrency prices",
    tools = [get_crypto]
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history" , [])
    await cl.Message(content= " Welcome to Crypto Price Agent!").send()
    


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    print("User input history:", history)

    try:
        result = Runner.run_sync(
            agent,
            input=history,
            run_config=config
        )
        final = result.final_output
    except Exception as e:
        final = f"Error occurred: {str(e)}"
        
    await cl.Message(content=final).send()
    history.append({"role": "assistant", "content": final})
    cl.user_session.set("history", history)
