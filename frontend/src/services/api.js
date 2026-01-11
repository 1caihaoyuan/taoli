const API_BASE = 'http://127.0.0.1:8000';

export const apiService = {
  // 获取单边套利数据
  async getRatesSingle() {
    try {
      const res = await fetch(`${API_BASE}/rates_single`);
      if (!res.ok) return [];
      return await res.json();
    } catch (e) {
      console.error('获取单边数据失败:', e);
      return [];
    }
  },

  // 获取搬砖数据
  async getSpreadsPrice() {
    try {
      const res = await fetch(`${API_BASE}/spreads_price`);
      if (!res.ok) return [];
      return await res.json();
    } catch (e) {
      console.error('获取搬砖数据失败:', e);
      return [];
    }
  },

  // 获取双向套利数据
  async getArbFutures() {
    try {
      const res = await fetch(`${API_BASE}/arb_futures`);
      if (!res.ok) return [];
      return await res.json();
    } catch (e) {
      console.error('获取双向数据失败:', e);
      return [];
    }
  },

  // 获取持仓数据
  async getPositions() {
    try {
      const res = await fetch(`${API_BASE}/positions`);
      if (!res.ok) return [];
      return await res.json();
    } catch (e) {
      console.error('获取持仓数据失败:', e);
      return [];
    }
  },

  // 检查API连接状态
  async checkStatus() {
    try {
      const res = await fetch(`${API_BASE}/check_status`);
      if (!res.ok) return {};
      return await res.json();
    } catch (e) {
      console.error('检查状态失败:', e);
      return {};
    }
  },

  // 执行策略
  async executeStrategy(data) {
    try {
      const res = await fetch(`${API_BASE}/execute_strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('执行策略失败:', e);
      return { status: 'error', msg: '无法连接后端' };
    }
  },

  // 更新API配置
  async updateConfig(data) {
    try {
      const res = await fetch(`${API_BASE}/update_config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('更新配置失败:', e);
      return { status: 'error', msg: '保存失败：后端未运行？' };
    }
  },

  // 平仓
  async closePosition(data) {
    try {
      const res = await fetch(`${API_BASE}/close_position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('平仓失败:', e);
      return { status: 'error', msg: '网络请求失败' };
    }
  },

  // 获取历史订单
  async getHistoryOrders() {
    try {
      const res = await fetch(`${API_BASE}/history_orders`);
      if (!res.ok) return [];
      return await res.json();
    } catch (e) {
      console.error('获取历史订单失败:', e);
      return [];
    }
  },

  // 锁定/解锁历史订单
  async lockHistoryOrder(data) {
    try {
      const res = await fetch(`${API_BASE}/lock_history_order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('锁定订单失败:', e);
      return { status: 'error', msg: '网络请求失败' };
    }
  },

  // 删除历史订单
  async deleteHistoryOrder(data) {
    try {
      const res = await fetch(`${API_BASE}/delete_history_order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('删除订单失败:', e);
      return { status: 'error', msg: '网络请求失败' };
    }
  },

  // 设置数据模式
  async setMode(data) {
    try {
      const res = await fetch(`${API_BASE}/set_mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (e) {
      console.error('设置模式失败:', e);
      return { status: 'error', msg: '网络请求失败' };
    }
  }
};
