import { ref, onMounted, onUnmounted } from 'vue';
import { apiService } from '../services/api';

export function useApi() {
  const ratesSingleData = ref([]);
  const spreadsPriceData = ref([]);
  const arbFuturesData = ref([]);
  const positionsData = ref([]);
  const isApiConnected = ref(false);
  const isLoading = ref(true);

  let intervalId = null;

  // 获取所有数据
  const fetchAllData = async () => {
    try {
      const [rates, spreads, futures, positions, status] = await Promise.all([
        apiService.getRatesSingle(),
        apiService.getSpreadsPrice(),
        apiService.getArbFutures(),
        apiService.getPositions(),
        apiService.checkStatus()
      ]);

      if (rates.length) ratesSingleData.value = rates;
      if (spreads.length) spreadsPriceData.value = spreads;
      if (futures.length) arbFuturesData.value = futures;
      positionsData.value = positions;

      // 检查是否有任何交易所已启用
      isApiConnected.value = Object.values(status).some(v => v === true);
      isLoading.value = false;
    } catch (error) {
      console.error('获取数据失败:', error);
      isLoading.value = false;
    }
  };

  // 启动定时刷新
  const startPolling = (interval = 8000) => {
    fetchAllData();
    intervalId = setInterval(fetchAllData, interval);
  };

  // 停止定时刷新
  const stopPolling = () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };

  // 组件挂载时自动启动
  onMounted(() => {
    startPolling();
  });

  // 组件卸载时清理
  onUnmounted(() => {
    stopPolling();
  });

  return {
    ratesSingleData,
    spreadsPriceData,
    arbFuturesData,
    positionsData,
    isApiConnected,
    isLoading,
    fetchAllData,
    startPolling,
    stopPolling
  };
}
