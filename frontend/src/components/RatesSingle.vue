<template>
  <section class="fade-in">
    <div class="mb-2 text-[10px] text-muted uppercase tracking-widest flex items-center gap-2">
      <span class="bg-blue/10 text-blue px-2 py-0.5 rounded">提示</span>
      点击列表任意行即可创建策略
    </div>
    
    <div class="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-black text-muted uppercase text-[10px] tracking-widest font-bold border-b border-border">
          <tr>
            <th class="p-4 sticky-col bg-black w-[30%]">交易对</th>
            <th class="p-4 w-[20%]">费率 (8h)</th>
            <th class="p-4 w-[25%]">年化收益</th>
            <th class="p-4 text-right w-[25%]">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50">
          <tr
            v-for="(item, idx) in paginatedData"
            :key="idx"
            @click="$emit('openStrategy', item, 'single')"
            class="hover:bg-purple/5 cursor-pointer transition-colors group"
          >
            <td class="p-4 sticky-col bg-black font-mono font-bold group-hover:text-purple transition-colors">
              {{ cleanSymbol(item.symbol) }}
              <div class="mt-1 text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-muted inline-block uppercase">
                {{ item.exchange }}
              </div>
            </td>
            <td class="p-4 font-mono text-green">{{ item.rate }}</td>
            <td class="p-4 font-mono font-bold text-green">{{ item.apr }}%</td>
            <td class="p-4 text-right">
              <span class="text-[10px] px-2 py-1 rounded border border-white/10 uppercase group-hover:bg-purple group-hover:text-black group-hover:border-purple transition">
                创建策略 ➔
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
