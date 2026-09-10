import os
import re
import json
import requests

# 복사해두신 상품 URL
TARGET_URL = "https://emart.ssg.com/item/itemView.ssg?itemId=1000646184325"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.ssg.com/"
}

def get_rice_price():
    try:
        # 1. URL에서 상품 ID(itemId) 추출
        item_id_match = re.search(r'itemId=(\d+)', TARGET_URL)
        if not item_id_match:
            return "URL에서 상품 ID(itemId)를 찾을 수 없습니다."
        
        item_id = item_id_match.group(1)

        # 2. SSG 가격 API 직접 호출
        api_url = f"https://www.ssg.com/item/ajaxItemPayInfo.ssg?itemId={item_id}"
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        
        # 3. JSON 데이터 파싱
        data = response.json()
        
        # 4. 가격 정보 가져오기 (할인가가 있으면 할인가, 없으면 판매가)
        price = data.get("itemPayInfo", {}).get("ssgPayAmt") or data.get("itemPayInfo", {}).get("sellprc")
        
        if price:
            # 숫자에 천 단위 쉼표 추가 (예: 35000 -> 35,000)
            formatted_price = f"{int(price):,}"
            return formatted_price
        else:
            return "가격 데이터를 수신하지 못했습니다."

    except Exception as e:
        return f"오류 발생: {str(e)}"

def send_telegram_msg(message):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    
    if not bot_token or not chat_id:
        print("토큰 또는 CHAT_ID가 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    price = get_rice_price()
    msg = f"🌾 [이마트몰] 한눈에 반한 쌀 10kg\n💰 오늘 가격: {price}원\n🔗 바로가기: {TARGET_URL}"
    send_telegram_msg(msg)
