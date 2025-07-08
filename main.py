
from auto_trader_finta import AutoTrader

# 필수 정보 입력
APP_KEY = "PSIwXKUFbVdw1qjrQKCV1wvpJsFUXh638Mm8"
APP_SECRET = "ExVYTSLvJEVZ2jAZUGB3MAOHmLkzn85C7RXk/KiuRRbqkEKZFCwjo7ChGyxZe7cK7PlYR6MYldysHLpA4ut8vxhskywUsms4/82MhYshgsPcGK80qAP4V5nKzdwlOw0wgWrBCdveG6SpVa6PmlNFGhkVMTblN/byu1HEM0XV8aB7POmnRP0="
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
ACCOUNT_NO = "43088913"

# 체크리스트로 선정된 종목들 (예시)
selected_stocks = ["AAPL", "MSFT", "NVDA", "AMZN"]

# 객체 생성 후 실행
bot = AutoTrader(APP_KEY, APP_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ACCOUNT_NO, selected_stocks)
bot.run()
