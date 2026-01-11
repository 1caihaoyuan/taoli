<template>
  <section class="fade-in">
    <div class="mb-2 text-[10px] text-muted uppercase tracking-widest flex items-center gap-2">
      <span class="bg-purple/10 text-purple px-2 py-0.5 rounded">提示</span>
      点击列表开启期现套利策略
    </div>

    <div class="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead>
          <tr class="bg-black text-muted uppercase text-[10px] border-b border-border">
            <th class="p-4 sticky-col bg-black w-[25%]">交易对</th>
            <th class="p-4 w-[25%]">做空 (卖)</th>
            <th class="p-4 w-[25%]">做多 (买)</th>
            <th class="p-4 text-right w-[25%]">年化差值</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50">
          <tr
            v-for="(item, idx) in paginatedData"
            :key="idx"
            @click="$emit('openStrategy', item, 'futures')"
            class="hover:bg-purple/5 cursor-pointer transition-colors group"
          >
            <td class="p-4 sticky-col bg-black font-mono font-bold group-hover:text-purple transition-colors">
              {{ cleanSymbol(item.symbol) }}
            </td>
            <td class="p-4 text-xs font-bold text-red">
              {{ item.short_ex }}
              <span class="opacity-50 font-normal block">{{ item.short_rate }}</span>
            </td>
            <td class="p-4 text-xs font-bold text-green">
              {{ item.long_ex }}
              <span class="opacity-50 font-normal block">{{ item.long_rate }}</span>
            </td>
            <td class="p-4 text-right font-bold font-mono text-purple flex justify-end items-center gap-2">
              {{ item.apr_diff }}%
              <span class="text-[10px] px-2 py-1 rounded border border-white/10 text-muted uppercase group-hover:bg-purple group-hover:text-black group-hover:border-purple transition">
                建仓
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
import { cleanSymbol } from '../utils/helpers';

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

defineEmits(['openStrategy']);

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
</style>
