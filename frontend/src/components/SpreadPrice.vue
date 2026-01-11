<template>
  <section class="fade-in">
    <div class="mb-4 bg-[#111] p-3 rounded-xl border border-border text-xs text-muted flex flex-wrap gap-4">
      <div class="flex items-center gap-2">
        <span>单笔本金</span>
        <input
          type="number"
          v-model="capital"
          @input="$emit('update:capital', Number(capital))"
          class="input-dark"
        >
      </div>
      <div class="flex items-center gap-2">
        <span>提币损耗(%)</span>
        <input
          type="number"
          v-model="fee"
          @input="$emit('update:fee', Number(fee))"
          class="input-dark !w-16"
        >
      </div>
    </div>

    <div class="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-black text-muted uppercase text-[10px] tracking-widest font-bold border-b border-border">
          <tr>
            <th class="p-4 sticky-col bg-black w-[25%]">交易对</th>
            <th class="p-4 w-[25%]">搬砖路径</th>
            <th class="p-4 text-right w-[20%]">价差率</th>
            <th class="p-4 text-right text-blue w-[30%]">预估利润</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50">
          <tr
            v-for="(item, idx) in paginatedData"
            :key="idx"
            @click="$emit('openStrategy', item, 'spread')"
            class="hover:bg-blue/5 cursor-pointer transition-colors group"
          >
            <td class="p-4 sticky-col bg-black font-mono font-bold group-hover:text-blue transition-colors">
              {{ cleanSymbol(item.symbol) }}
            </td>
            <td class="p-4 text-xs">
              <div class="flex items-center gap-1 font-bold text-muted group-hover:text-white">
                {{ item.buy_on }} <span class="text-blue">➔</span> {{ item.sell_on }}
              </div>
            </td>
            <td class="p-4 text-right text-blue/60 font-mono">{{ item.spread }}%</td>
            <td class="p-4 text-right font-bold font-mono text-blue flex justify-end items-center gap-2">
              +{{ calculateProfit(item) }} U
              <span class="text-[10px] px-2 py-1 rounded border border-white/10 text-muted uppercase group-hover:bg-blue group-hover:text-black group-hover:border-blue transition">
                执行
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center items-center gap-4 mt-6">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1"
        class="px-3 py-1 rounded bg-surface border border-border text-xs hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        上一页
      </button>
      
      <span class="text-xs text-muted">
        第 <span class="text-white font-bold">{{ currentPage }}</span> / {{ totalPages }} 页
      </span>
      
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages"
        class="px-3 py-1 rounded bg-surface border border-border text-xs hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        下一页
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { cleanSymbol, calculateSpreadProfit } from '../utils/helpers';

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  initialCapital: {
    type: Number,
    default: 1000
  },
  initialFee: {
    type: Number,
    default: 0.02
  }
});

const emit = defineEmits(['openStrategy', 'update:capital', 'update:fee']);

const capital = ref(props.initialCapital);
const fee = ref(props.initialFee);

// 监听props变化
watch(() => props.initialCapital, (val) => capital.value = val);
watch(() => props.initialFee, (val) => fee.value = val);

const calculateProfit = (item) => {
  return calculateSpreadProfit(item, capital.value, fee.value);
};

// Pagination
const currentPage = ref(1);
const itemsPerPage = 20;

const totalPages = computed(() => Math.max(1, Math.ceil(props.data.length / itemsPerPage)));

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return props.data.slice(start, end);
});

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

watch(() => props.data.length, () => {
  if (currentPage.value > totalPages.value) currentPage.value = 1;
});
</script>

<style scoped>
.sticky-col {
  position: sticky;
  left: 0;
  background-color: #0a0a0a;
  z-index: 10;
  border-right: 1px solid #1f1f1f;
}

.input-dark {
  background: #111;
  border: 1px solid #333;
  color: white;
  padding: 10px;
  width: 100%;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
}

.input-dark:focus {
  border-color: #bf5af2;
  outline: none;
}
</style>
