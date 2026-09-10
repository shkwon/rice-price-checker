import os
import re
import requests

TARGET_URL = "https://emart.ssg.com/item/itemView.ssg?itemId=1000646184325"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://emart.ssg.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_rice_price():
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        html = res.text

        # 1. 페이지 내 자바스크립트 변수에서 가격(sellprc, itemAmt, ssgPayAmt) 패턴 추출
        patterns = [
            r'"sellprc"\s*:\s*"?(\d+)"?',
            r'"itemAmt"\s*:\s*"?(\d+)"?',
            r'"ssgPayAmt"\s*:\s*"?(\d+)"?',
            r'itemAmt\s*=\s*"?(\d+)"?'
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                price_val = int(match.group(1))
                # 정상적인 가격 범위(10,000원 이상)인지 검증
                if price_val > 10000:
                    return f"{price_val:,}"

        # 2. Meta 태그(og:price:amount) 확인
        og_price = re.search(r'property="og:price:amount"\s+content="(\d+)"', html)
        if og_price:
            return f"{int(og_price.group(1)):,}"

        return "가격 메타데이터를 찾을 수 없습니다."

    except Exception as e:
        return f"요청 오류: {str(e)}"

def send_telegram_msg(message):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    
    if not bot_token or not chat_id:
        print("BOT_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    price = get_rice_price()
    msg = f"🌾 [이마트몰] 한눈에반한쌀 (특) 10kg\n💰 오늘 가격: {price}원\n🔗 바로가기: {TARGET_URL}"
    send_telegram_msg(msg)
