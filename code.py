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

rt_data = kb.get_overseas_price_quot_price_detail(excd="NAS", itm_no="AAPL")
print(rt_data)    # 해외주식 현재가상세