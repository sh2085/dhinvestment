from signal_result import SignalResult

class MarketSignalEvaluator:
    def __init__(self, ticker: str, vix: float, fgi: int, rsi: float):
        self.ticker = ticker
        self.vix = vix
        self.fgi = fgi
        self.rsi = rsi

    def _fgi_level(self):
        if self.fgi <= 25:
            return "극단 공포"
        elif self.fgi <= 45:
            return "공포"
        elif self.fgi <= 55:
            return "중립"
        elif self.fgi <= 75:
            return "탐욕"
        else:
            return "극단 탐욕"

    def _vix_range(self):
        if self.vix <= 20:
            return "≤ 20"
        elif self.vix <= 30:
            return "20–30"
        elif self.vix <= 40:
            return "30–40"
        else:
            return "≥ 40"

    def evaluate(self) -> SignalResult:
        fgi_level = self._fgi_level()
        vix_range = self._vix_range()

        signal = "관망"
        risk_ratio = 0.5
        safe_ratio = 0.5

        if self.rsi <= 30 and fgi_level in ["공포", "극단 공포"]:
            if vix_range == "≥ 40" and fgi_level == "극단 공포":
                signal = "강력 매수"
                risk_ratio = 0.7
            else:
                signal = "매수"
                risk_ratio = 0.65 if vix_range == "30–40" else 0.7 if vix_range == "20–30" else 0.75
        elif self.rsi > 70 and fgi_level in ["탐욕", "극단 탐욕"]:
            if vix_range == "≥ 40":
                signal = "강력 매도"
                risk_ratio = 0.3
            elif vix_range in ["30–40", "20–30"]:
                signal = "매도"
                risk_ratio = 0.4
            elif vix_range == "≤ 20":
                signal = "매도 검토"
                risk_ratio = 0.5

        safe_ratio = round(1 - risk_ratio, 2)
        return SignalResult(self.ticker, round(self.rsi, 2), signal, round(risk_ratio, 2), safe_ratio)