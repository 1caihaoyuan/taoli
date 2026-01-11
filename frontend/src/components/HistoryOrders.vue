<template>
  <section class="fade-in">
    <div class="mb-4 flex justify-between items-center">
      <div class="text-xs text-muted">
        共 <span class="text-white font-bold">{{ data.length }}</span> 条历史记录
      </div>
    </div>

    <div class="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="bg-black text-muted uppercase text-[10px] border-b border-border">
            <th class="p-4 w-[12%]">交易对</th>
            <th class="p-4 w-[8%]">交易所</th>
            <th class="p-4 text-center w-[8%]">方向</th>
            <th class="p-4 w-[10%]">策略</th>
            <th class="p-4 w-[10%]">开仓价格</th>
            <th class="p-4 w-[12%]">平仓时间</th>
            <th class="p-4 text-right w-[10%]">最终盈亏</th>
            <th class="p-4 text-right w-[10%]">保证金</th>
            <th class="p-4 text-center w-[12%]">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50">
          <tr v-for="(item, idx) in data" :key="idx" class="hover:bg-white/5">
            <td class="p-4 font-mono font-bold">
              {{ cleanSymbol(item.symbol) }}
            </td>
            <td class="p-4 text-xs text-muted">{{ item.exchange }}</td>
            <td class="p-4 text-center">
              <span
                :class="item.side === 'long' ? 'text-green bg-green/10' : 'text-red bg-red/10'"
                class="px-2 py-0.5 rounded text-[10px] font-black uppercase"
              >
                {{ item.side === 'long' ? '做多' : '做空' }}
              </span>
            </td>
            <td class="p-4 text-xs">
              <span 
                :class="getStrategyColor(item.strategy)"
                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
              >
                {{ getStrategyName(item.strategy) }}
              </span>
            </td>
            <td class="p-4 font-mono text-xs text-muted">
              {{ item.entry_price || '-' }}
            </td>
            <td class="p-4 text-xs text-muted">
              {{ formatTime(item.close_time) }}
            </td>
            <td 
              class="p-4 text-right font-mono font-bold"
              :class="getPnlColor(item.final_pnl)"
            >
              {{ formatPnl(item.final_pnl) }} U
            </td>
            <td class="p-4 text-right font-mono text-xs text-muted">
              {{ item.margin || '-' }} U
            </td>
            <td class="p-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <!-- 锁定/解锁按钮 -->
                <button
                  @click="handleLock(item)"
                  :class="item.locked ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30' : 'bg-white/5 text-muted border-white/10'"
                  class="px-2 py-1 rounded text-[10px] border hover:opacity-80 transition flex items-center gap-1"
                  :title="item.locked ? '点击解锁' : '点击锁定'"
                >
                  <span v-if="item.locked">🔒</span>
                  <span v-else>🔓</span>
                </button>
                
                <!-- 删除按钮 -->
                <button
                  @click="handleDelete(item)"
                  :disabled="item.locked"
                  :class="item.locked ? 'opacity-30 cursor-not-allowed' : 'hover:bg-red/20'"
                  class="bg-red/10 text-red px-2 py-1 rounded text-[10px] border border-red/30 transition"
                  :title="item.locked ? '已锁定，无法删除' : '删除订单'"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="data.length === 0">
            <td colspan="9" class="p-8 text-center text-muted">暂无历史订单。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { cleanSymbol } from '../utils/helpers';

defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['lock', 'delete']);

const getStrategyName = (strategy) => {
  const names = {
    'futures_arb': '期现套利',
    'single': '单边',
    'spread': '搬砖',
    'funding_arb': '单边套利'
  };
  return names[strategy] || strategy || '未知';
};

const getStrategyColor = (strategy) => {
  const colors = {
    'futures_arb': 'bg-purple/10 text-purple',
    'single': 'bg-green/10 text-green',
    'spread': 'bg-blue/10 text-blue',
    'funding_arb': 'bg-green/10 text-green'
  };
  return colors[strategy] || 'bg-muted/10 text-muted';
};

const getPnlColor = (pnl) => {
  const value = parseFloat(pnl) || 0;
  if (value > 0) return 'text-green';
  if (value < 0) return 'text-red';
  return 'text-muted';
};

const formatPnl = (pnl) => {
  const value = parseFloat(pnl) || 0;
  return value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2);
};

const formatTime = (timeStr) => {
  if (!timeStr) return '-';
  // 格式：2026-01-11 04:15:30 -> 01-11 04:15
  try {
    const parts = timeStr.split(' ');
    if (parts.length === 2) {
      const date = parts[0].substring(5); // 去掉年份
      const time = parts[1].substring(0, 5); // 只保留时:分
      return `${date} ${time}`;
    }
    return timeStr;
  } catch {
    return timeStr;
  }
};

// 锁定/解锁订单
const handleLock = (item) => {
  emit('lock', item);
};

// 删除订单
const handleDelete = (item) => {
  if (item.locked) {
    return; // 已锁定的订单不能删除
  }
  emit('delete', item);
};
</script>
