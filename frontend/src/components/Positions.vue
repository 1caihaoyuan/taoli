<template>
  <section class="fade-in">
    <div class="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="bg-black text-muted uppercase text-[10px] border-b border-border">
            <th class="p-4 sticky-col bg-black w-[35%]">交易对</th>
            <th class="p-4 text-center w-[20%]">方向</th>
            <th class="p-4 w-[25%]">未实现盈亏</th>
            <th class="p-4 text-right w-[20%]">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50">
          <tr v-for="(item, idx) in data" :key="idx">
            <td class="p-4 sticky-col bg-black font-mono font-bold">
              {{ cleanSymbol(item.symbol) }}
              <div class="text-[9px] text-muted">{{ item.exchange }}</div>
            </td>
            <td class="p-4 text-center">
              <span
                :class="item.side === 'long' ? 'text-green bg-green/10' : 'text-red bg-red/10'"
                class="px-2 py-0.5 rounded text-[10px] font-black uppercase"
              >
                {{ item.side === 'long' ? '做多' : '做空' }}
              </span>
            </td>
            <td
              class="p-4 font-mono font-bold"
              :class="item.pnl >= 0 ? 'text-green' : 'text-red'"
            >
              {{ item.pnl }} U
            </td>
            <td class="p-4 text-right">
              <button
                @click="$emit('closePosition', item)"
                class="bg-red/10 text-red px-3 py-1 rounded text-[10px] border border-red/30 hover:bg-red/20"
              >
                平仓
              </button>
            </td>
          </tr>
          <tr v-if="data.length === 0">
            <td colspan="4" class="p-8 text-center text-muted">当前无持仓。</td>
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

defineEmits(['closePosition']);
</script>

<style scoped>
.sticky-col {
  position: sticky;
  left: 0;
  background-color: #0a0a0a;
  z-index: 10;
  border-right: 1px solid #1f1f1f;
}
</style>
