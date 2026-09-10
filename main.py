import os
import requests
from bs4 import BeautifulSoup

# 이마트몰/SSG 한눈에반한쌀 10kg 검색 결과 및 상품 페이지 URL
TARGET_URL = "https://emart.ssg.com/item/itemView.ssg?itemId=1000646184325"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_rice_price():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # SSG/이마트몰 가격 태그 추출
        price_element = soup.select_one(".ssg_price")
        if price_element:
            return price_element.text.strip()
        
        # 대체 가격 태그 확인
        price_element_alt = soup.select_one(".cdtl_price .ssg_tx")
        if price_element_alt:
            return price_element_alt.text.strip()
            
        return "가격 태그를 찾을 수 없습니다."
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
    msg = f"🌾 [이마트몰] 한눈에반한쌀 10kg\n💰 오늘 가격: {price}원\n🔗 바로가기: {TARGET_URL}"
    send_telegram_msg(msg)
