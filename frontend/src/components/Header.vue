<template>
  <header class="flex flex-col md:flex-row md:justify-between md:items-end border-b border-border pb-4 mb-6 gap-4">
    <div>
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-white tracking-tight flex items-center gap-2 uppercase">
          <span class="w-2 h-2 bg-purple rounded-full shadow-[0_0_10px_#bf5af2]"></span>
          Alpha Terminal
        </h1>

        <!-- 模式切换开关 -->
        <label class="flex items-center gap-2 cursor-pointer group bg-zinc-900/50 border border-white/5 py-1 px-2.5 rounded-full hover:border-purple/30 transition select-none">
          <div class="relative">
            <input type="checkbox" v-model="isConservative" class="sr-only peer">
            <div class="w-8 h-4 bg-zinc-700 rounded-full peer-checked:bg-purple peer-focus:outline-none transition-colors"></div>
            <div class="absolute left-1 top-1 w-2 h-2 bg-white rounded-full transition-transform peer-checked:translate-x-4"></div>
          </div>
          <span class="text-[10px] font-bold uppercase transition-colors" :class="isConservative ? 'text-purple' : 'text-muted group-hover:text-white'">
            {{ isConservative ? '保守稳定' : '极速激进' }}
          </span>
        </label>
      </div>
      <p class="text-[10px] text-muted mt-1 uppercase tracking-widest font-mono">加密货币套利与策略引擎</p>
    </div>
    
    <div class="flex items-center gap-4 w-full md:w-auto justify-between">
      <nav class="flex gap-4 overflow-x-auto no-scrollbar flex-1 md:flex-none">
        <button
          v-for="(tab, index) in tabs"
          :key="index"
          @click="$emit('update:activeTab', index + 1)"
          :class="[
            activeTab === index + 1 ? ['tab-active', tab.color] : 'tab-inactive',
            'pb-2 text-xs font-bold uppercase transition whitespace-nowrap'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
      
      <button
        @click="$emit('openApiModal')"
        class="bg-zinc-900 border border-border px-3 py-2 rounded-lg text-[10px] font-bold hover:bg-zinc-800 transition uppercase tracking-tighter flex items-center gap-2"
      >
        <span :class="isApiConnected ? 'text-green' : 'text-red'">●</span>
        API 设置
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, watch } from 'vue';
import { apiService } from '../services/api';

defineProps({
  activeTab: {
    type: Number,
    required: true
  },
  isApiConnected: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:activeTab', 'openApiModal', 'modeChanged']);

const isConservative = ref(false);

watch(isConservative, async (val) => {
  await apiService.setMode({ conservative: val });
  emit('modeChanged');
});

const tabs = [
  { name: '期现套利', color: 'text-green' },
  { name: '现货搬砖', color: 'text-blue' },
  { name: '期期套利', color: 'text-purple' },
  { name: '我的持仓', color: 'text-orange' },
  { name: '历史订单', color: 'text-yellow-500' }
];
</script>

<style scoped>
.tab-active {
  color: white;
  border-bottom: 2px solid currentColor;
}

.tab-inactive {
  color: #666;
  border-bottom: 2px solid transparent;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
