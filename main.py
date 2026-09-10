import os
import re
import json
import requests
from bs4 import BeautifulSoup

# 이마트몰 한눈에반한쌀 10kg 실제 주소
TARGET_URL = "https://emart.ssg.com/item/itemView.ssg?itemId=1000646184325"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://emart.ssg.com/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_rice_price():
    item_id = "1000646184325"
    
    # [방법 1] 이마트몰 가격 정보 API 직접 조회
    try:
        api_url = f"https://emart.ssg.com/item/ajaxItemPayInfo.ssg?itemId={item_id}"
        res = requests.get(api_url, headers=HEADERS, timeout=10)
        data = res.json()
        
        # API에서 할인 가격 또는 정상 가격 추출
        pay_info = data.get("itemPayInfo", {})
        price = pay_info.get("ssgPayAmt") or pay_info.get("sellprc") or pay_info.get("itemAmt")
        
        if price and str(price).isdigit():
            return f"{int(price):,}"
    except Exception as e:
        print(f"API 방식 실패: {e}")

    # [방법 2] 상품 페이지 HTML 직접 크롤링 (대체 방식)
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 주 가격 셀렉터들 확인
        selectors = [
            ".ssg_price", 
            ".cdtl_price .ssg_tx", 
            "em.ssg_price", 
            "span.price",
            ".item_price .ssg_tx"
        ]
        
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                # 숫자만 추출
                raw_price = re.sub(r'[^0-9]', '', elem.text)
                if raw_price:
                    return f"{int(raw_price):,}"
    except Exception as e:
        print(f"HTML 방식 실패: {e}")

    return "가격 정보를 읽어오지 못했습니다."

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
    msg = f"🌾 [이마트몰] 한눈에반한쌀 (특) 10kg\n💰 오늘 가격: {price}원\n🔗 바로가기: {TARGET_URL}"
    send_telegram_msg(msg)
