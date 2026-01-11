<template>
  <Transition name="fade">
    <div
      v-if="show"
      class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-lg bg-black/80 backdrop-blur-xl border border-border rounded-2xl p-6 space-y-4 shadow-2xl flex flex-col max-h-[85vh]">
        <h2 class="text-lg font-bold text-white uppercase tracking-widest shrink-0">API 配置</h2>

        <div class="flex flex-col gap-3 overflow-y-auto pr-2 min-h-[200px] flex-1 no-scrollbar">
          <div
            v-for="ex in exchanges"
            :key="ex"
            class="p-3 bg-black/50 rounded-lg border border-white/5 shrink-0"
          >
            <div class="text-[10px] font-bold text-muted uppercase mb-1">{{ ex }}</div>
            <div>
              <input
                v-model="configs[ex].key"
                placeholder="输入 API Key"
                class="input-dark mb-2"
              >
              <input
                v-model="configs[ex].secret"
                type="password"
                placeholder="输入 Secret"
                class="input-dark"
              >
              <input
                v-if="ex === 'okx'"
                v-model="configs[ex].pass"
                placeholder="输入 Passphrase (口令)"
                class="input-dark mt-2"
              >
            </div>
          </div>
        </div>

        <button
          @click="handleSave"
          class="w-full bg-white text-black font-bold py-3 rounded-xl uppercase hover:bg-gray-200 shrink-0"
        >
          保存设置
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'save']);

const exchanges = ['binance', 'okx', 'bybit', 'bitget', 'gate', 'kucoin'];

const configs = ref({});

// 初始化配置
exchanges.forEach(ex => {
  configs.value[ex] = { key: '', secret: '', pass: '' };
});

const handleSave = () => {
  emit('save', configs.value);
};
</script>

<style scoped>
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
