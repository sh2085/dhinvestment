import kis_ovrseastk as kb
class OrderManager:
    def __init__(self, exchange="NASD"):
        self.exchange = exchange

    def place_order(self, direction: str, ticker: str, qty: int = 1, order_type: str = "01"):
        """
        direction: 'buy' or 'sell'
        """
        try:
            print(f"{ticker} {direction}!")
            # rt_data = kb.get_overseas_order(
            #     ord_dv=direction,
            #     excg_cd=self.exchange,
            #     itm_no=ticker,
            #     qty=qty,
            #     ord_dvsn=order_type
            # )
            # if rt_data.get("rt_cd") != "0":
            #     print(f"❗️{direction.upper()} 실패 - {ticker}: {rt_data.get('msg1')}")
            # else:
            #     print(f"✅ {direction.upper()} 성공 - {ticker}")
            # return rt_data
        except Exception as e:
            print(f"🚨 주문 예외 발생 ({direction.upper()} - {ticker}): {e}")
            return None