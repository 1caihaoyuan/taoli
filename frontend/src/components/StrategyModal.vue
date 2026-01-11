<template>
  <Transition name="fade">
    <div
      v-if="show && selectedItem"
      class="fixed inset-0 z-[100] bg-black/20 backdrop-blur-sm flex items-center justify-center p-4"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-md bg-black/60 backdrop-blur-2xl border border-purple/30 rounded-3xl p-6 relative overflow-hidden shadow-2xl">
        <div class="absolute top-0 right-0 w-32 h-32 bg-purple/20 blur-[50px] rounded-full pointer-events-none"></div>

        <div>
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="text-2xl font-black text-white italic">{{ cleanSymbol(selectedItem.symbol) }}</h2>

              <div v-if="type === 'single'" class="mt-1">
                <span class="text-xs font-bold text-purple bg-purple/10 px-2 py-0.5 rounded border border-purple/20">
                  {{ selectedItem.exchange }}
                </span>
              </div>
              
              <div v-else-if="type === 'futures'" class="mt-1 flex items-center gap-2 text-xs font-bold">
                <span class="text-red bg-red/10 px-2 py-0.5 rounded border border-red/20">
                  卖: {{ selectedItem.short_ex }}
                </span>
                <span class="text-muted">/</span>
                <span class="text-green bg-green/10 px-2 py-0.5 rounded border border-green/20">
                  买: {{ selectedItem.long_ex }}
                </span>
              </div>
              
              <div v-else-if="type === 'spread'" class="mt-1 flex items-center gap-2 text-xs font-bold">
                <span class="text-blue bg-blue/10 px-2 py-0.5 rounded border border-blue/20">
                  买: {{ selectedItem.buy_on }}
                </span>
                <span class="text-muted">➔</span>
                <span class="text-blue bg-blue/10 px-2 py-0.5 rounded border border-blue/20">
                  卖: {{ selectedItem.sell_on }}
                </span>
              </div>
            </div>

            <div class="text-right">
              <div class="text-[10px] text-muted uppercase">
                {{ type === 'spread' ? '价差利润' : (type === 'single' ? '当前费率' : '年化差值') }}
              </div>
              <div class="text-lg font-mono font-bold" :class="type === 'spread' ? 'text-blue' : 'text-green'">
                {{ getDisplayValue() }}
              </div>
            </div>
          </div>

          <!-- 策略表单 -->
          <div class="space-y-5">
            <div>
              <label class="text-[10px] text-muted uppercase font-bold tracking-widest mb-1 block">
                投入本金 (保证金)
              </label>
              <div class="flex items-center gap-2">
                <button
                  @click="form.amount = Math.max(0, form.amount - 100)"
                  class="w-12 h-11 rounded-xl bg-[#111]/80 border border-border text-muted hover:text-white hover:border-purple hover:bg-white/10 transition flex items-center justify-center text-lg font-bold"
                >
                  −
                </button>
                <div class="relative flex-1">
                  <input
                    type="number"
                    v-model="form.amount"
                    class="w-full h-11 bg-black/50 border border-border rounded-xl px-4 text-white font-mono font-bold text-center focus:border-purple focus:outline-none transition"
                  >
                  <span class="absolute right-4 top-3.5 text-muted text-[10px] font-bold pointer-events-none">USDT</span>
                </div>
                <button
                  @click="form.amount = Number(form.amount) + 100"
                  class="w-12 h-11 rounded-xl bg-[#111]/80 border border-border text-muted hover:text-white hover:border-purple hover:bg-white/10 transition flex items-center justify-center text-lg font-bold"
                >
                  +
                </button>
              </div>
            </div>

            <!-- 杠杆倍数 (搬砖策略只要1倍，不需要显示滑块) -->
            <div v-if="type !== 'spread'">
              <div class="flex justify-between mb-2">
                <label class="text-[10px] text-muted uppercase font-bold tracking-widest">杠杆倍数</label>
                <span class="text-xs font-bold text-purple">{{ form.leverage }}x</span>
              </div>
              <input
                type="range"
                v-model="form.leverage"
                min="1"
                max="10"
                step="1"
                class="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer slider"
              >
            </div>

            <!-- 搬砖策略提示 -->
            <div v-if="type === 'spread'" class="bg-blue/5 p-4 rounded-xl border border-blue/20 space-y-3">
              <div class="flex items-center gap-2 text-blue text-xs font-bold">
                <span class="bg-blue/20 p-1 rounded">💡</span>
                <span>搬砖操作流程</span>
              </div>
              <div class="space-y-2">
                <div class="flex items-start gap-3 text-[10px] text-muted">
                  <span class="bg-zinc-800 text-white w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 font-bold">1</span>
                  <span>在 <span class="text-white">{{ selectedItem?.buy_on }}</span> 购买 {{ cleanSymbol(selectedItem?.symbol) }}</span>
                </div>
                <div class="flex items-start gap-3 text-[10px] text-muted">
                  <span class="bg-zinc-800 text-white w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 font-bold">2</span>
                  <span>提币至 <span class="text-white">{{ selectedItem?.sell_on }}</span> (注意选择正确链)</span>
                </div>
                <div class="flex items-start gap-3 text-[10px] text-muted">
                  <span class="bg-zinc-800 text-white w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 font-bold">3</span>
                  <span>到账后卖出，完成套利</span>
                </div>
              </div>
            </div>

            <div class="bg-black/40 p-4 rounded-xl border border-white/5 space-y-2">
              <div class="flex justify-between text-xs">
                <span class="text-muted">总仓位价值</span>
                <span class="font-mono text-white">{{ (form.amount * form.leverage).toFixed(0) }} USDT</span>
              </div>
              <div class="flex justify-between text-xs items-center">
                <span class="text-muted">{{ type === 'spread' ? '预估单次收益' : '预估日收益' }}</span>
                <span class="font-mono text-green font-bold text-sm">+{{ dailyYield }} USDT</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-2">
              <button
                @click="$emit('close')"
                class="py-3 rounded-xl border border-border text-muted text-xs font-bold hover:bg-white/10 transition"
              >
                取消
              </button>
              <button
                @click="handleExecute"
                class="py-3 rounded-xl bg-gradient-to-r from-purple to-blue text-black font-black text-xs uppercase tracking-widest hover:opacity-90 hover:scale-[1.02] transition shadow-[0_0_20px_rgba(191,90,242,0.3)]"
              >
                {{ type === 'single' ? '启动单边策略' : (type === 'spread' ? '启动搬砖策略' : '启动双向策略') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { cleanSymbol, calculateDailyYield } from '../utils/helpers';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  selectedItem: {
    type: Object,
    default: null
  },
  type: {
    type: String,
    default: 'single' // 'single', 'spread', 'futures'
  }
});

const emit = defineEmits(['close', 'execute']);

const form = ref({
  amount: 1000,
  leverage: 1
});

// 重置表单
watch(() => props.show, (newVal) => {
  if (newVal) {
    form.value = { amount: 1000, leverage: 1 };
  }
});

const getDisplayValue = () => {
  if (!props.selectedItem) return '';
  if (props.type === 'spread') return props.selectedItem.spread + '%';
  if (props.type === 'single') return props.selectedItem.rate;
  return props.selectedItem.apr_diff + '%';
};

const dailyYield = computed(() => {
  if (!props.selectedItem) return '0.00';
  return calculateDailyYield(
    props.type,
    props.selectedItem,
    form.value.amount,
    form.value.leverage
  );
});

const handleExecute = () => {
  emit('execute', {
    item: props.selectedItem,
    type: props.type,
    amount: form.value.amount,
    leverage: form.value.leverage
  });
};
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #bf5af2;
  margin-top: -6px;
  cursor: pointer;
  border: 2px solid #000;
}

.slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  cursor: pointer;
  background: #333;
  border-radius: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
