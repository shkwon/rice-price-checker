import os
import re
import requests
from playwright.sync_api import sync_playwright

TARGET_URL = "https://emart.ssg.com/item/itemView.ssg?itemId=1000646184325"

def get_rice_price():
    try:
        with sync_playwright() as p:
            # 가상 크롬 브라우저 실행
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 페이지 접속 후 화면 로딩 대기
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            
            # 가격 요소가 화면에 뜰 때까지 대기 및 추출
            selectors = [".ssg_price", "em.ssg_price", ".cdtl_price .ssg_tx", ".item_price"]
            price_text = ""
            
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, timeout=4000)
                    price_text = page.locator(selector).first.inner_text()
                    if price_text:
                        break
                except:
                    continue
            
            browser.close()

            # 숫자만 추출 후 천 단위 쉼표 추가
            raw_price = re.sub(r'[^0-9]', '', price_text)
            if raw_price:
                return f"{int(raw_price):,}"
            
            return "가격을 찾을 수 없습니다."

    except Exception as e:
        return f"오류 발생: {str(e)}"

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
