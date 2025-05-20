# services/exchange_rate.py
import requests
import pandas as pd
from typing import Dict, Optional

class ExchangeRateService:
    def __init__(self):
        self.base_url = "http://download.finance.yahoo.com/d/quotes.csv"
        # 常用货币代码
        self.currencies = {
            'CNY': 'Chinese Yuan',     # 人民币
            'EUR': 'Euro',             # 欧元
            'GBP': 'British Pound',    # 英镑
            'JPY': 'Japanese Yen',     # 日元
            'CAD': 'Canadian Dollar',  # 加元
            'AUD': 'Australian Dollar',# 澳元
            'INR': 'Indian Rupee'      # 印度卢比
        }

    def get_exchange_rate(self, currency_code: str) -> Optional[float]:
        """
        获取指定货币兑美元的实时汇率
        返回值表示1美元等于多少目标货币
        """
        try:
            # 构造Yahoo Finance API请求
            pair = f"USD{currency_code}=X"
            params = {
                'e': '.csv',
                'f': 'sl1d1t1',  # symbol, last price, date, time
                's': pair
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # 解析CSV响应
            data = response.text.strip().split(',')
            if len(data) >= 2:
                rate = float(data[1])  # 第二个字段是汇率
                return rate
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching rate for {currency_code}: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing rate for {currency_code}: {e}")
            return None

    def get_all_rates(self) -> Dict[str, float]:
        """
        获取所有支持货币的实时汇率
        """
        rates = {}
        for code in self.currencies.keys():
            rate = self.get_exchange_rate(code)
            if rate is not None:
                rates[code] = rate
        return rates

if __name__ == "__main__":
    # 测试代码
    exchange_service = ExchangeRateService()
    
    print("实时汇率测试 (1 USD = ?)")
    print("-" * 40)
    
    # 测试单一货币
    cny_rate = exchange_service.get_exchange_rate('CNY')
    if cny_rate:
        print(f"1 USD = {cny_rate:.4f} CNY")
    
    # 测试所有货币
    all_rates = exchange_service.get_all_rates()
    for code, rate in all_rates.items():
        print(f"1 USD = {rate:.4f} {code} ({exchange_service.currencies[code]})")



        
        
        
        