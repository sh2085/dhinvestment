class SignalResult:
    def __init__(self, ticker, rsi, signal, risk_ratio, safe_ratio):
        self.ticker = ticker
        self.rsi = rsi
        self.signal = signal
        self.risk_asset_ratio = risk_ratio
        self.safe_asset_ratio = safe_ratio
        self.should_buy = signal in ["매수", "강력 매수"]
        self.should_sell = signal in ["매도", "강력 매도", "매도 검토"]

    def to_dict(self):
        return {
            "ticker": self.ticker,
            "rsi": self.rsi,
            "signal": self.signal,
            "risk_asset_ratio": self.risk_asset_ratio,
            "safe_asset_ratio": self.safe_asset_ratio,
            "should_buy": self.should_buy,
            "should_sell": self.should_sell
        }

    def __str__(self):
        buy_sell_flag = "🔼 Buy" if self.should_buy else "🔽 Sell" if self.should_sell else "⏸️ Hold"
        return f"[{self.ticker}] RSI: {self.rsi} → {self.signal} ({buy_sell_flag})"