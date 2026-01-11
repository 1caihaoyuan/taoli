import ccxt
import pandas as pd
from datetime import datetime

# --- 如果你在国内，可能需要配置代理 ---
# 如果运行后卡住不动或报错，请尝试将下面这一行的 # 号去掉，并修改端口号（通常是 7890 或 1087）
PROXIES = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'} 
# ------------------------------------

def fetch_arbitrage_opportunities():
    print("🚀 正在连接交易所获取数据，请稍候...")
    
    try:
        # 初始化交易所
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'proxies': PROXIES, 
            'options': {'defaultType': 'future'}
        })

        # 获取数据
        rates = exchange.fetch_funding_rates()
        data_list = []
        
        for symbol, data in rates.items():
            funding_rate = data['fundingRate']
            if funding_rate is None: continue
            
            # 计算年化
            predicted_apr = funding_rate * 3 * 365 * 100
            
            if '/USDT' in symbol:
                data_list.append({
                    'Symbol': symbol,
                    'Rate': f"{funding_rate * 100:.4f}%",
                    'APR': round(predicted_apr, 2),
                    'Action': 'Short+Buy' if funding_rate > 0 else 'Long+Sell',
                    'raw_apr': abs(predicted_apr)
                })

        # 整理表格
        if data_list:
            df = pd.DataFrame(data_list)
            df = df.sort_values(by='raw_apr', ascending=False).drop(columns=['raw_apr'])
            return df.head(10) # 只看前10名
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("💡 提示：如果是 Network Error，通常是因为没开梯子或没配置代理。")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_arbitrage_opportunities()
    if not df.empty:
        print("\n💰 === 实时套利机会榜单 === 💰")
        print(df.to_markdown(index=False))
    else:
        print("未获取到数据。")

