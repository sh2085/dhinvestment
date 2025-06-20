# 나무증권 HTS API 연동 자동매매 프로그램 구현

# 1. 나무증권 API 설정

# 환경 설정
import requests
import json
import time
import pandas as pd
from datetime import datetime

# API 인증 정보
APP_KEY = "발급받은_APP_KEY"
APP_SECRET = "발급받은_APP_SECRET"
ACCESS_TOKEN = ""  # 초기화


### 2. API 인증 처리

def get_access_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("인증 실패: " + response.text)

ACCESS_TOKEN = get_access_token()

### 3. 계좌 정보 조회
def get_account_balance():
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "VTTC8434R"  # 잔고조회 TR 코드
    }
    
    params = {
        "CANO": "계좌번호앞8자리",
        "ACNT_PRDT_CD": "계좌번호뒤2자리",
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()


### 4. VIX 기반 자산배분 엔진
def calculate_allocations(vix_level):
    # 예시: VIX가 20 이하이면 주식 80%, 채권 20%, 20~30이면 주식 60%, 채권 40%, 30 초과면 주식 40%, 채권 60%
    if vix_level <= 20:
        return {"stock": 0.8, "bond": 0.2}
    elif vix_level <= 30:
        return {"stock": 0.6, "bond": 0.4}
    else:
        return {"stock": 0.4, "bond": 0.6}
   
def hedge_with_put_options():
    if get_vix() > 30:
        url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "VTTC0802U"
        }
        
        # SPY 풋옵션 매수
        order_data = {
            "CANO": "계좌번호앞8자리",
            "ACNT_PRDT_CD": "계좌번호뒤2자리",
            "PDNO": "SPY풋옵션코드",
            "ORD_DVSN": "01",
            "ORD_QTY": "1",
            "ORD_UNPR": "0",
        }
        response = requests.post(url, headers=headers, data=json.dumps(order_data))

### 8. 메인 실행 루프

def main():
    # 매일 오전 9시 실행
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            # 1. VIX 지수 확인
            vix = get_vix()
            
            # 2. 목표 자산배분 계산
            target_alloc = calculate_allocations(vix)
            
            # 3. 포트폴리오 리밸런싱
            rebalance_portfolio(target_alloc)
            
            # 4. 헤징 실행
            hedge_with_put_options()
            
            # 5. 다음 실행 전 대기
            time.sleep(86400)  # 24시간 대기
        time.sleep(60)  # 1분마다 시간 확인


# type: ignore # ### 실행 방법
# 1. **나무증권 개발자 포털**에서 API 키 발급
# 2. `APP_KEY`와 `APP_SECRET` 업데이트
# 3. 계좌 정보 설정:
#    ```python
#    CANO = "계좌번호앞8자리"
#    ACNT_PRDT_CD = "계좌번호뒤2자리"
#    ```
# 4. 포트폴리오 구성 종목 설정:
#    ```python
#    PORTFOLIO = ["005930", "000660", "035420"]  # 원하는 종목으로 변경
#    ```
# 5. 의존성 설치:
#    ```bash
#    pip install requests pandas
#    ```
# 6. 프로그램 실행:
#    ```bash
#    python auto_trading.py
#    ```

# ### 주의사항
# 1. **모의투자 테스트 필수**: 실제 거래 전 모의계좌에서 충분히 테스트
# 2. **리밸런싱 주기**: 분기별(3개월)로 최적화 수행 권장
# 3. **예외 처리**: 네트워크 오류, 주문 실패 등에 대한 예외 처리 추가 필요
# 4. **로그 시스템**: 모든 거래 내역 기록하는 로깅 시스템 구현

# > 이 프로그램은 VIX 기반 동적 자산배분 전략을 나무증권 API로 구현한 것으로, 시장 변동성에 유연하게 대응하는 포트폴리오 관리가 가능합니다. 실제 운용 전 백테스팅과 모의투자를 필수적으로 진행하세요.