<template>
  <div id="app" class="z-10">
    <Header
      :activeTab="activeTab"
      :isApiConnected="isApiConnected"
      @update:activeTab="handleTabChange"
      @openApiModal="showApiModal = true"
      @modeChanged="handleModeChange"
    />

    <main>
      <!-- Tab 1: 单边套利 -->
      <RatesSingle
        v-if="activeTab === 1"
        :data="ratesSingleData"
        @openStrategy="openStrategyModal"
      />

      <!-- Tab 2: 现货搬砖 -->
      <SpreadPrice
        v-if="activeTab === 2"
        :data="spreadsPriceData"
        :initialCapital="spreadCapital"
        :initialFee="spreadFee"
        @update:capital="spreadCapital = $event"
        @update:fee="spreadFee = $event"
        @openStrategy="openStrategyModal"
      />

      <!-- Tab 3: 双向套利 -->
      <FuturesArb
        v-if="activeTab === 3"
        :data="arbFuturesData"
        @openStrategy="openStrategyModal"
      />

      <!-- Tab 4: 持仓管理 -->
      <Positions
        v-if="activeTab === 4"
        :data="positionsData"
        @closePosition="handleClosePosition"
      />

      <!-- Tab 5: 历史订单 -->
      <HistoryOrders
        v-if="activeTab === 5"
        :data="historyOrdersData"
        @lock="handleLockOrder"
        @delete="handleDeleteOrder"
      />
    </main>

    <!-- API配置弹窗 -->
    <ApiModal
      :show="showApiModal"
      @close="showApiModal = false"
      @save="handleSaveApi"
    />

    <!-- 策略执行弹窗 -->
    <StrategyModal
      :show="showStrategyModal"
      :selectedItem="selectedStrategyItem"
      :type="strategyType"
      @close="showStrategyModal = false"
      @execute="handleExecuteStrategy"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApi } from './composables/useApi';
import { apiService } from './services/api';

import Header from './components/Header.vue';
import RatesSingle from './components/RatesSingle.vue';
import SpreadPrice from './components/SpreadPrice.vue';
import FuturesArb from './components/FuturesArb.vue';
import Positions from './components/Positions.vue';
import HistoryOrders from './components/HistoryOrders.vue';
import ApiModal from './components/ApiModal.vue';
import StrategyModal from './components/StrategyModal.vue';

// 使用API组合函数
const {
  ratesSingleData,
  spreadsPriceData,
  arbFuturesData,
  positionsData,
  isApiConnected,
  fetchAllData
} = useApi();

// 状态管理
const activeTab = ref(1);
const showApiModal = ref(false);
const showStrategyModal = ref(false);
const selectedStrategyItem = ref(null);
const strategyType = ref('single');
const historyOrdersData = ref([]);

// 搬砖配置
const spreadCapital = ref(1000);
const spreadFee = ref(0.02);

// 获取历史订单
const fetchHistoryOrders = async () => {
  const data = await apiService.getHistoryOrders();
  historyOrdersData.value = data;
};

// 监听Tab切换，当切换到历史订单时加载数据
const handleTabChange = async (newTab) => {
  activeTab.value = newTab;
  if (newTab === 5) {
    await fetchHistoryOrders();
  }
};

// 监听模式切换，刷新数据
const handleModeChange = async () => {
  await fetchAllData();
};


// 打开策略弹窗
const openStrategyModal = (item, type) => {
  selectedStrategyItem.value = item;
  strategyType.value = type;
  showStrategyModal.value = true;
};

// 保存API配置
const handleSaveApi = async (configs) => {
  const payload = {};
  
  Object.keys(configs).forEach(ex => {
    const conf = configs[ex];
    const hasKey = !!(conf.key && conf.key.trim() !== '');
    payload[ex] = {
      apiKey: conf.key,
      secret: conf.secret,
      enable: hasKey
    };
    if (ex === 'okx') {
      payload[ex].password = conf.pass;
    }
  });

  const result = await apiService.updateConfig(payload);
  if (result.status === 'success' || !result.status) {
    alert('配置已保存！');
    showApiModal.value = false;
    await fetchAllData();
  } else {
    alert(result.msg || '保存失败');
  }
};

// 执行策略
const handleExecuteStrategy = async (data) => {
  if (!isApiConnected.value) {
    alert('⚠️ 请先连接交易所 API！\n请点击右上角 API 设置按钮进行配置。');
    showStrategyModal.value = false;
    showApiModal.value = true;
    return;
  }

  const { item, type, amount, leverage } = data;

  let typeName = '单边';
  if (type === 'futures') typeName = '双向对冲';
  if (type === 'spread') typeName = '现货搬砖';

  if (!confirm(`确定要对 ${item.symbol} 启动【${typeName}】策略吗？`)) return;

  const payload = {
    symbol: item.symbol,
    amount: amount,
    leverage: leverage,
    type: type === 'spread' ? 'spot_spread' : (type === 'single' ? 'funding_arb' : 'futures_arb')
  };

  if (type === 'spread') {
    payload.buy_on = item.buy_on;
    payload.sell_on = item.sell_on;
  } else if (type === 'single') {
    payload.exchange = item.exchange;
  } else {
    payload.short_ex = item.short_ex;
    payload.long_ex = item.long_ex;
  }

  const result = await apiService.executeStrategy(payload);
  if (result.status === 'success') {
    alert(result.msg || '策略已启动');
    showStrategyModal.value = false;
    await fetchAllData();
  } else {
    alert('错误: ' + (result.msg || '执行失败'));
  }
};

// 平仓
const handleClosePosition = async (position) => {
  if (!confirm(`确定平仓 ${position.symbol} (${position.exchange})?`)) return;

  const result = await apiService.closePosition(position);
  if (result.status === 'success') {
    alert('平仓成功！');
    await fetchAllData();
    // 如果当前在历史订单Tab，也刷新历史订单
    if (activeTab.value === 5) {
      await fetchHistoryOrders();
    }
  } else {
    alert('平仓失败: ' + (result.msg || '未知错误'));
  }
};

// 锁定/解锁历史订单
const handleLockOrder = async (order) => {
  const newLockState = !order.locked;
  const action = newLockState ? '锁定' : '解锁';
  
  if (!confirm(`确定要${action}该订单吗？`)) return;
  
  const result = await apiService.lockHistoryOrder({
    symbol: order.symbol,
    exchange: order.exchange,
    close_time: order.close_time,
    locked: newLockState
  });
  
  if (result.status === 'success') {
    alert(result.msg || `${action}成功`);
    await fetchHistoryOrders();
  } else {
    alert(`${action}失败: ` + (result.msg || '未知错误'));
  }
};

// 删除历史订单
const handleDeleteOrder = async (order) => {
  if (order.locked) {
    alert('该订单已锁定，请先解锁后再删除');
    return;
  }
  
  if (!confirm(`确定要删除该订单吗？\n${order.symbol} (${order.exchange})`)) return;
  
  const result = await apiService.deleteHistoryOrder({
    symbol: order.symbol,
    exchange: order.exchange,
    close_time: order.close_time
  });
  
  if (result.status === 'success') {
    alert('删除成功！');
    await fetchHistoryOrders();
  } else {
    alert('删除失败: ' + (result.msg || '未知错误'));
  }
};
</script>
