from dotenv import load_dotenv
import os

# .env 파일 읽어오기
load_dotenv()

# 변수 불러오기
upbit_access_key = os.getenv("UPBIT_ACCESS_KEY")
upbit_secret_key = os.getenv("UPBIT_SECRET_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

def GPT_trading():
    # 1.업비트 차트 데이터 가져오기(30일 일봉)

    import pyupbit

    df = pyupbit.get_ohlcv("KRW-BTC", count = 30, interval="day")

    # 2.GPT에 데이터 제공하고 답변 받기

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You are a Bitcoin investment expert.\nYou can accurately calculate buy and sell timings using chart data.\nresponse in json format\n\nResponse Example:\n{\"decision\": \"buy\"}\n{\"decision\": \"sell\"}\n{\"decision\": \"hold\"}"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": df.to_json()
            }
        ]
        }
    ],
    response_format={
        "type": "json_object"
    },
    )
    result = response.choices[0].message.content

    # 3. 자동 매매 실행하기

    import json
    result = json.loads(result)

    # 업비트 로그인
    upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key)

    if result["decision"] == "buy" :
        my_krw = upbit.get_balance("KRW")
        if my_krw*0.9995 > 5000 :
            print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995))
            print("buy")
        else :
            print("Fail : less than KRW 5000")
    elif result["decision"] == "sell" :
        my_btc = upbit.get_balance("KRW-BTC")
        current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
        if my_btc*current_price > 5000 :
            print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
            print("Sell")
        else :
            print("Fail : less than KRW-BTC 5000")
    elif result["decision"] == "hold" :
        print("Hold")


while True :
    import time
    time.sleep(10)
    GPT_trading()