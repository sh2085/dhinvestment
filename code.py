import requests
import json
import kis_auth as ka
import kis_ovrseastk as kb
import yaml
import pandas as pd
import sys


#config = yaml.load("config.yaml")
#토큰 발급 kis_auth import
ka.auth(svr='vps')

# rt_data = kb.get_overseas_price_quot_price_detail(excd="NAS", itm_no="APLD")
# print(rt_data)    # 해외주식 현재가상세

import yfinance as yf
import pandas as pd
import numpy as np
import threading
import requests
from queue import Queue

# ✅ RSI 계산 함수
def compute_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ✅ 멀티스레딩 작업자 함수
def worker(ticker_queue, all_data, result_list, lock, threshold_rsi=30):
    while not ticker_queue.empty():
        ticker = ticker_queue.get()
        try:
            print(f"📦 Processing: {ticker}")

            if ticker not in all_data.columns.get_level_values(0):
                print(f"⚠️ {ticker}: 데이터 없음")
                continue

            df = all_data[ticker].dropna()
            if 'Close' not in df.columns or df['Close'].isnull().all():
                print(f"⚠️ {ticker}: 종가 없음")
                continue

            close_prices = df['Close'].dropna()
            if len(close_prices) < 15:
                print(f"⚠️ {ticker}: 종가 수 부족")
                continue

            rsi_series = compute_rsi(close_prices).dropna()
            if rsi_series.empty:
                continue

            latest_rsi = float(rsi_series.iloc[-1])
            print(f"{ticker} RSI = {latest_rsi}\n")
            if latest_rsi <= threshold_rsi or latest_rsi >= 70:
                with lock:
                    result_list.append((ticker, round(latest_rsi, 2)))
        except Exception as e:
            with lock:
                print(f"❌ [{ticker}] 처리 중 오류 발생: {e}")
        finally:
            ticker_queue.task_done()


# ✅ 실행 예시
def main():
    # ▶️ 예제용 일부 NASDAQ 종목 (실제는 전체 NASDAQ 리스트 필요)
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "GOOGL", "META", "AMZN"]

    all_data = yf.download(
        tickers=tickers,
        period='1mo',
        interval='1d',
        group_by='ticker',
        auto_adjust=False,
        progress=False,
        threads=True  # yfinance 내부 병렬화
    )

    ticker_queue = Queue()
    for ticker in tickers:
        ticker_queue.put(ticker)

    results = []
    lock = threading.Lock()

    threads = []
    for _ in range(5):  # 동시에 5개 티커 처리
        t = threading.Thread(target=worker, args=(ticker_queue, all_data, results, lock))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # ✅ 필터링 결과 출력 및 주문 예시
    for ticker, rsi in results:
        print(f"{ticker} | RSI: {rsi}")
        if rsi <= 30:
            rt_data = kb.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no=ticker, qty=1, ord_dvsn="01")
            # 주문 예시 (지정가 100달러로 임의 설정)


if __name__ == "__main__":
    main()
