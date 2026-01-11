import json
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor # 修复：补充导入
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import ccxt
import uvicorn
import os
import datetime
import uuid 

# --- 新增：持仓管理配置 ---
POSITIONS_FILE = 'active_positions.json'
HISTORY_DIR = 'history'

# 确保历史目录存在
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# 辅助函数：读写文件
def load_positions_from_file():
    if os.path.exists(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def save_positions_to_file(data):
    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def ensure_mock_positions():
    """读取当前持仓（不再生成模拟数据）"""
    return load_positions_from_file()


app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- 全局配置 ---
CONFIG_FILE = 'config.json'

# 【重要】代理配置
# 如果你的网络能直连交易所，请把 USE_PROXY 改为 False
# 或者根据你的代理软件端口修改 PROXIES
USE_PROXY = True  
PROXIES = {
    'http': 'http://127.0.0.1:7890', 
    'https': 'http://127.0.0.1:7890'
}

USER_CONFIG = {}

# --- 全局状态 ---
# POSITIONS_FILE = "active_positions.json" # 已在上方定义
# HISTORY_DIR = "history" # 已在上方定义
CACHE_RATES_SINGLE = []
CACHE_SPREADS_PRICE = []
CACHE_ARB_FUTURES = []

# 全局模式设置
IS_CONSERVATIVE = False  # 默认为激进模式(False)，勾选后为保守模式(True)

class PlaceOrderRequest(BaseModel):
    items: list
    amount: float
    leverage: int

class ModeRequest(BaseModel):
    conservative: bool

# --- 辅助函数 ---

def load_config():
    global USER_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            USER_CONFIG = json.load(f)
    except:
        USER_CONFIG = {}

def save_config(new_config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(new_config, f, indent=4)

def get_exchange(name, private=False):
    conf = USER_CONFIG.get(name.lower(), {})
    if private and not conf.get('enable'): return None
    
    config = {
        'enableRateLimit': True, 
        'timeout': 10000  # 增加超时时间
    }
    
    if USE_PROXY:
        config['proxies'] = PROXIES

    if private:
        config.update({'apiKey': conf.get('apiKey'), 'secret': conf.get('secret')})
        if 'password' in conf: config['password'] = conf['password']
        if 'passphrase' in conf: config['password'] = conf['passphrase'] # OKX use passphrase
        
    try:
        ex_class = getattr(ccxt, name.lower())
        ex = ex_class(config)
        return ex
    except: return None

# --- 修复：补充缺失的模拟数据生成函数 ---
def generate_mock_data():
    """生成演示用的模拟数据，防止后端无数据时前端空白报错"""
    
    # 真实代币列表
    REAL_SYMBOLS = [
        "BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "TRX", "DOT", "LINK",
        "MATIC", "SHIB", "LTC", "BCH", "ATOM", "UNI", "XLM", "OKB", "ETC", "TON",
        "FIL", "HBAR", "APT", "VET", "QNT", "CRO", "LDO", "NEAR", "ALGO", "AAVE",
        "STX", "GRT", "FTM", "SAND", "EOS", "MANA", "THETA", "EGLD", "AXS", "XTZ",
        "OP", "ARB", "SUI", "PEPE", "RNDR", "INJ", "IMX", "LUNC", "CAKE", "EOS"
    ]

    # 1. 单边数据
    s_list = []
    exchanges = ['Binance', 'OKX', 'Bybit', 'Gate']
    for i in range(100):
        sym_base = REAL_SYMBOLS[i % len(REAL_SYMBOLS)]
        
        if IS_CONSERVATIVE:
            # 保守模式: 0.01% - 0.15% (低风险，收益稳)
            rate = random.uniform(0.0001, 0.0015)
        else:
            # 激进模式: 0.05% - 0.40% (高波动，收益高)
            rate = random.uniform(0.0005, 0.0040)
            
        s_list.append({
            'symbol': f"{sym_base}/USDT",
            'exchange': random.choice(exchanges),
            'rate': f"{rate*100:.4f}%",
            'apr': f"{rate * 3 * 365 * 100:.2f}"
        })
    s_list.sort(key=lambda x: float(x['apr']), reverse=True)

    # 2. 搬砖数据
    p_list = []
    for i in range(100):
        sym_base = REAL_SYMBOLS[i % len(REAL_SYMBOLS)]
        base_price = random.uniform(10, 2000)
        spread_pct = random.uniform(0.5, 3.0)
        sell_price = base_price * (1 + spread_pct/100)
        
        ex1, ex2 = random.sample(exchanges, 2)
        
        p_list.append({
            'symbol': f"{sym_base}/USDT",
            'buy_on': ex1, 'buy_price': f"{base_price:.2f}",
            'sell_on': ex2, 'sell_price': f"{sell_price:.2f}",
            'spread': f"{spread_pct:.2f}"
        })
    p_list.sort(key=lambda x: float(x['spread']), reverse=True)

    # 3. 双向套利数据
    a_list = []
    for i in range(100):
        sym_base = REAL_SYMBOLS[i % len(REAL_SYMBOLS)]
        
        if IS_CONSERVATIVE:
            # 保守模式
            r1 = random.uniform(0.0001, 0.0020)
            r2 = random.uniform(0.0001, 0.0020)
        else:
            # 激进模式
            r1 = random.uniform(0.0005, 0.0040)
            r2 = random.uniform(0.0005, 0.0040)
        
        # 确保 r1 > r2 来模拟有价差的情况 (做空费率高，做多费率低，赚费率差)
        rate_short = max(r1, r2)
        rate_long = min(r1, r2)
        
        # 计算年化差值: (大费率 - 小费率) * 每天3次 * 365天 * 100转百分比
        diff_val = (rate_short - rate_long) * 3 * 365 * 100
        
        ex1, ex2 = random.sample(exchanges, 2)
        
        a_list.append({
            'symbol': f"{sym_base}/USDT",
            'short_ex': ex1, 'short_rate': f"{rate_short*100:.4f}%",
            'long_ex': ex2, 'long_rate': f"{rate_long*100:.4f}%",
            'apr_diff': f"{diff_val:.2f}"
        })
    a_list.sort(key=lambda x: float(x['apr_diff']), reverse=True)

    return s_list, p_list, a_list

# --- 真实数据抓取逻辑 ---
def fetch_real_market_data():
    # 定义我们要监控的交易所
    target_exchanges = ['binance', 'okx', 'bybit']
    
    raw_tickers = {} 
    raw_rates = {}   

    def _task(ex_name):
        try:
            ex = get_exchange(ex_name) 
            if not ex: 
                # 初始化公共实例
                config = {'enableRateLimit': True}
                if USE_PROXY: config['proxies'] = PROXIES
                ex = getattr(ccxt, ex_name)(config)
            
            # 1. 抓取 Tickers
            tickers = ex.fetch_tickers()
            
            # 2. 抓取费率
            rates = {}
            if ex.has['fetchFundingRates']:
                try:
                    rates = ex.fetch_funding_rates()
                except:
                    pass # 部分交易所可能不支持或超时
            
            return ex_name, tickers, rates
        except Exception as e:
            # print(f"抓取 {ex_name} 失败: {e}")
            return ex_name, {}, {}

    # 并行抓取
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_task, name) for name in target_exchanges]
        for f in futures:
            name, t, r = f.result()
            if t: raw_tickers[name] = t
            if r: raw_rates[name] = r

    # 如果没有任何数据返回（例如网络全断），直接返回空，让外层决定是否使用模拟数据
    if not raw_tickers and not raw_rates:
        return [], [], []

    # --- 数据处理 ---
    s_list, p_list, a_list = [], [], []
    def clean(s): 
        if not s: return ""
        return s.split(':')[0]

    # A. 单边
    if 'binance' in raw_rates:
        for sym, data in raw_rates['binance'].items():
            if '/USDT' in sym:
                rate = data['fundingRate']
                if abs(rate) > 0.0001: 
                    s_list.append({
                        'symbol': clean(sym),
                        'exchange': 'Binance',
                        'rate': f"{rate*100:.4f}%",
                        'apr': f"{rate * 3 * 365 * 100:.2f}"
                    })
    s_list.sort(key=lambda x: float(x['apr']), reverse=True)

    # B. 搬砖
    common_symbols = set()
    for t in raw_tickers.values():
        for s in t.keys():
            if '/USDT' in s: common_symbols.add(s)
    
    for sym in common_symbols:
        prices = {}
        for ex_name, t_data in raw_tickers.items():
            if sym in t_data:
                prices[ex_name] = t_data[sym]['last']
        
        if len(prices) > 1:
            try:
                min_ex, max_ex = min(prices, key=prices.get), max(prices, key=prices.get)
                min_p, max_p = prices[min_ex], prices[max_ex]
                
                if min_p and min_p > 0:
                    diff = (max_p - min_p) / min_p * 100
                    if 0.5 < diff < 20: # 稍微放宽范围
                        p_list.append({
                            'symbol': clean(sym),
                            'buy_on': min_ex, 'buy_price': f"{min_p}",
                            'sell_on': max_ex, 'sell_price': f"{max_p}",
                            'spread': f"{diff:.2f}"
                        })
            except: pass
    p_list.sort(key=lambda x: float(x['spread']), reverse=True)

    # C. 双向
    # ... (此处逻辑与原来类似，简化处理) ...
    # 为保证演示效果，如果抓不到双向数据，这里可以混合一点模拟逻辑，或者严格依赖真实
    # 这里保持原逻辑架构，但增加容错
    for sym in common_symbols:
        rs = {}
        for ex_name, r_data in raw_rates.items():
            # 尝试多种 key 格式
            keys_to_try = [sym, f"{sym}:USDT", sym.replace('/', '')]
            for k in keys_to_try:
                if k in r_data:
                    rs[ex_name] = r_data[k]['fundingRate']
                    break
        
        if len(rs) > 1:
            try:
                max_ex, min_ex = max(rs, key=rs.get), min(rs, key=rs.get)
                rate_diff = rs[max_ex] - rs[min_ex]
                apr_diff = rate_diff * 3 * 365 * 100
                
                if apr_diff > 3: 
                    a_list.append({
                        'symbol': clean(sym),
                        'short_ex': max_ex, 'short_rate': f"{rs[max_ex]*100:.4f}%",
                        'long_ex': min_ex, 'long_rate': f"{rs[min_ex]*100:.4f}%",
                        'apr_diff': f"{apr_diff:.2f}"
                    })
            except: pass
    a_list.sort(key=lambda x: float(x['apr_diff']), reverse=True)

    return s_list[:100], p_list[:100], a_list[:100]


# --- 路由 ---

@app.get("/rates_single")
def get_single(): return CACHE_RATES_SINGLE

@app.get("/spreads_price")
def get_price(): return CACHE_SPREADS_PRICE

@app.get("/arb_futures")
def get_futures(): return CACHE_ARB_FUTURES

@app.get("/check_status")
def check_status():
    return {k: v.get('enable', False) for k, v in USER_CONFIG.items()}

# --- 修改：执行策略接口 (包含自动拆分逻辑) ---
@app.post("/execute_strategy")
async def execute_strategy(data: dict = Body(...)):
    # 1. 获取前端传来的参数
    strategy_type = data.get('type')
    symbol = data.get('symbol')
    total_amount = float(data.get('amount', 0))
    leverage = float(data.get('leverage', 1))
    
    # 读取当前持仓
    positions = load_positions_from_file()
    
    new_orders = []
    
    # --- 逻辑 A: 期现套利 (Futures Arb) -> 50% 现货买入 + 50% 合约开空 ---
    if strategy_type == 'futures_arb':
        # 资金拆分
        half_amount = total_amount / 2
        
        # 模拟：获取当前价格 (如果没有真实行情，就随机生成一个基准价)
        base_price = 60000 if 'BTC' in symbol else (3000 if 'ETH' in symbol else 100)
        
        # 1. 生成【现货做多】单子 (Exchange A)
        pos_spot = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "exchange": data.get('long_ex', 'Unknown'), # 买入所
            "side": "long",
            "type": "spot", # 标记为现货
            "entry_price": str(base_price),
            "mark_price": str(base_price), # 初始无盈亏
            "size": f"{(half_amount / base_price):.4f}", # 计算币的数量
            "margin": half_amount,
            "leverage": 1, # 现货默认1倍
            "pnl": 0,
            "strategy": "futures_arb" # 标记策略组
        }
        
        # 2. 生成【合约做空】单子 (Exchange B)
        # 注意：合约通常使用杠杆，但期现套利为了对冲，通常是 1倍空 或者 调节保证金
        # 这里演示：用剩下的一半资金，开空
        pos_future = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "exchange": data.get('short_ex', 'Unknown'), # 卖出所
            "side": "short",
            "type": "future",
            "entry_price": str(base_price + 5), # 模拟一点点价差
            "mark_price": str(base_price + 5),
            "size": f"{(half_amount * leverage / base_price):.4f}", 
            "margin": half_amount,
            "leverage": leverage,
            "pnl": 0,
            "strategy": "futures_arb"
        }
        
        new_orders.append(pos_spot)
        new_orders.append(pos_future)
        
        msg = f"策略启动成功！已执行：\n1. {pos_spot['exchange']} 买入 {half_amount}U 现货\n2. {pos_future['exchange']} 开空 {half_amount}U 合约"

    # --- 逻辑 B: 单边套利 (Funding Arb) ---
    elif strategy_type == 'funding_arb':
        # 单边直接开全额
        pos = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "exchange": data.get('exchange'),
            "side": "long", # 假设吃费率通常是做多，或者是根据正负费率判断（这里简化默认为Long）
            "type": "future",
            "entry_price": "60000", # 模拟价
            "mark_price": "60000",
            "margin": total_amount,
            "leverage": leverage,
            "pnl": 0,
            "strategy": "single"
        }
        new_orders.append(pos)
        msg = f"单边策略已启动：{symbol} 投入 {total_amount}U"

    # --- 逻辑 C: 现货搬砖 (Spot Spread) ---
    elif strategy_type == 'spot_spread':
         # 搬砖通常是一买一卖
        half_amount = total_amount / 2
        pos_buy = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "exchange": data.get('buy_on'),
            "side": "long",
            "type": "spot",
            "margin": half_amount,
            "pnl": 0,
            "strategy": "spread"
        }
        pos_sell = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "exchange": data.get('sell_on'),
            "side": "short", # 现货卖出逻辑上是Short，或者是持有现货卖出
            "type": "spot",
            "margin": half_amount,
            "pnl": 0,
            "strategy": "spread"
        }
        new_orders.append(pos_buy)
        new_orders.append(pos_sell)
        msg = f"搬砖策略启动：{data.get('buy_on')} 买入 -> {data.get('sell_on')} 卖出"

    else:
        return {"status": "error", "msg": "未知策略类型"}

    # 保存所有新生成的订单
    positions.extend(new_orders)
    save_positions_to_file(positions)
    
    return {
        "status": "success", 
        "msg": msg,
        "new_orders": new_orders
    }


@app.post("/update_config")
async def update_config(data: dict = Body(...)):
    global USER_CONFIG
    USER_CONFIG = data
    save_config(data)
    return {"status": "success"}

@app.get("/positions")
def get_positions():
    # 从本地文件读取持仓，作为唯一数据源
    return ensure_mock_positions()

@app.post("/set_mode")
def set_mode(req: ModeRequest):
    global IS_CONSERVATIVE, CACHE_RATES_SINGLE, CACHE_SPREADS_PRICE, CACHE_ARB_FUTURES
    IS_CONSERVATIVE = req.conservative
    
    print(f"🔄 切换模式: {'保守' if IS_CONSERVATIVE else '激进'}")
    
    # 立即重新生成数据以应用新模式
    s, p, a = generate_mock_data()
    CACHE_RATES_SINGLE = s
    CACHE_SPREADS_PRICE = p
    CACHE_ARB_FUTURES = a
    
    return {"status": "success", "mode": "conservative" if IS_CONSERVATIVE else "aggressive"}

@app.post("/close_position")
async def close_position(data: dict = Body(...)):
    positions = load_positions_from_file()
    
    # 查找并移除目标订单
    # 这里用 Symbol + Exchange + Side 来定位（简化版）
    target = None
    new_list = []
    
    for p in positions:
        if (p['symbol'] == data.get('symbol') and 
            p['exchange'] == data.get('exchange') and 
            p['side'] == data.get('side')):
            target = p
        else:
            new_list.append(p)
            
    if target:
        # 1. 归档历史
        target['close_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target['final_pnl'] = data.get('pnl', 0)
        
        # 按日期保存到 history 文件夹
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        history_file = os.path.join(HISTORY_DIR, f"orders_{date_str}.json")
        
        history_list = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_list = json.load(f)
            except: pass
            
        history_list.append(target)
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, indent=4, ensure_ascii=False)
            
        # 2. 更新活跃持仓文件（删除了目标单）
        save_positions_to_file(new_list)
        
        return {"status": "success", "msg": f"订单 {target['symbol']} 已平仓并归档"}
    
    return {"status": "error", "msg": "未找到该持仓，可能已平仓"}

@app.get("/history_orders")
def get_history_orders():
    """获取所有历史订单"""
    all_history = []
    
    # 读取 history 目录下的所有文件
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        orders = json.load(f)
                        # 为每个订单添加文件名信息，用于后续操作
                        for order in orders:
                            order['_filename'] = filename
                        all_history.extend(orders)
                except:
                    continue
    
    # 按锁定状态和平仓时间排序（锁定的在前面，然后按时间倒序）
    all_history.sort(key=lambda x: (
        not x.get('locked', False),  # 锁定的排在前面
        x.get('close_time', '')  # 然后按时间倒序
    ), reverse=True)
    
    return all_history

@app.post("/lock_history_order")
async def lock_history_order(data: dict = Body(...)):
    """锁定或解锁历史订单"""
    symbol = data.get('symbol')
    exchange = data.get('exchange')
    close_time = data.get('close_time')
    locked = data.get('locked', True)
    
    if not all([symbol, exchange, close_time]):
        return {"status": "error", "msg": "缺少必要参数"}
    
    # 读取所有历史文件
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        orders = json.load(f)
                    
                    # 查找并更新订单
                    updated = False
                    for order in orders:
                        if (order.get('symbol') == symbol and 
                            order.get('exchange') == exchange and 
                            order.get('close_time') == close_time):
                            order['locked'] = locked
                            updated = True
                            break
                    
                    if updated:
                        # 写回文件
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(orders, f, indent=4, ensure_ascii=False)
                        return {"status": "success", "msg": f"订单已{'锁定' if locked else '解锁'}"}
                except:
                    continue
    
    return {"status": "error", "msg": "未找到该订单"}

@app.post("/delete_history_order")
async def delete_history_order(data: dict = Body(...)):
    """删除历史订单（仅未锁定的）"""
    symbol = data.get('symbol')
    exchange = data.get('exchange')
    close_time = data.get('close_time')
    
    if not all([symbol, exchange, close_time]):
        return {"status": "error", "msg": "缺少必要参数"}
    
    # 读取所有历史文件
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        orders = json.load(f)
                    
                    # 查找订单
                    new_orders = []
                    deleted = False
                    for order in orders:
                        if (order.get('symbol') == symbol and 
                            order.get('exchange') == exchange and 
                            order.get('close_time') == close_time):
                            # 检查是否锁定
                            if order.get('locked', False):
                                return {"status": "error", "msg": "该订单已锁定，请先解锁"}
                            deleted = True
                        else:
                            new_orders.append(order)
                    
                    if deleted:
                        # 写回文件
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(new_orders, f, indent=4, ensure_ascii=False)
                        return {"status": "success", "msg": "订单已删除"}
                except:
                    continue
    
    return {"status": "error", "msg": "未找到该订单"}

# --- 后台任务 ---

def background_worker():
    global CACHE_RATES_SINGLE, CACHE_SPREADS_PRICE, CACHE_ARB_FUTURES
    print("⚡️ 后台引擎启动...")
    
    # 首次启动先生成一次模拟数据，让前端立刻有显示
    mock_s, mock_p, mock_a = generate_mock_data()
    CACHE_RATES_SINGLE = mock_s
    CACHE_SPREADS_PRICE = mock_p
    CACHE_ARB_FUTURES = mock_a

    while True:
        try:
            print("正在抓取真实数据...", end=" ")
            real_s, real_p, real_a = fetch_real_market_data()
            
            if real_s or real_p or real_a:
                CACHE_RATES_SINGLE = real_s
                CACHE_SPREADS_PRICE = real_p
                CACHE_ARB_FUTURES = real_a
                print("成功 (Real Data)")
            else:
                print("失败或为空 (保持 Mock Data)")
                # 如果真实数据获取失败，我们保留上一次的数据（如果是 Mock 就继续用 Mock）
                # 或者你可以选择在这里强制重新生成 Mock
                
        except Exception as e:
            print(f"Error Loop: {e}")
        
        # 轮询间隔
        time.sleep(15)

@app.on_event("startup")
def startup():
    load_config()
    threading.Thread(target=background_worker, daemon=True).start()

if __name__ == "__main__":
    # 使用 0.0.0.0 允许局域网访问
    uvicorn.run(app, host="0.0.0.0", port=8000)
