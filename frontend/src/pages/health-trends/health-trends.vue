<template>
  <view class="health-page">
    <text class="page-title">健康趋势</text>

    <view class="chart-tabs">
      <view v-for="m in metrics" :key="m.key" :class="['tab', activeMetric === m.key ? 'tab-active' : '']" @tap="activeMetric = m.key">
        <text>{{ m.icon }} {{ m.label }}</text>
      </view>
    </view>

    <view class="chart-area" v-if="chartData">
      <view class="baseline-info" v-if="currentBaseline">
        <text>基线: {{ currentBaseline.baseline_value }} ± {{ currentBaseline.std_deviation }}</text>
        <text :class="currentBaseline.is_established ? 'est-yes' : 'est-no'">
          {{ currentBaseline.is_established ? '✅ 基线已建立' : '⏳ 基线建立中(需7天数据)' }}
        </text>
      </view>
      <view class="baseline-info" v-else>
        <text>暂无基线数据，持续打卡即可建立</text>
      </view>

      <!-- Simple text chart (ucharts would be used in production) -->
      <view class="data-table">
        <view class="table-row table-header">
          <text class="col-date">日期</text>
          <text class="col-score">分数</text>
          <text class="col-status">状态</text>
        </view>
        <view class="table-row" v-for="(date, idx) in dates" :key="idx">
          <text class="col-date">{{ date.substring(5) }}</text>
          <text class="col-score">{{ actualScores[idx] }}</text>
          <text :class="['col-status', getStatusClass(idx)]">{{ getStatusText(idx) }}</text>
        </view>
      </view>
    </view>

    <view class="empty" v-else>
      <text>暂无数据，开始打卡吧</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { usePetStore } from '../../stores/pet'
import * as baselinesApi from '../../api/baselines'

const petStore = usePetStore()
const activeMetric = ref('diet')
const chartData = ref<any>(null)
const baselines = ref<any[]>([])

const metrics = [
  { key: 'diet', label: '饮食', icon: '🍽️' },
  { key: 'water', label: '饮水', icon: '💧' },
  { key: 'stool', label: '排便', icon: '🚽' },
  { key: 'spirit', label: '精神', icon: '😸' },
]

const currentBaseline = computed(() => baselines.value.find(b => b.metric_type === activeMetric.value))
const dates = computed(() => chartData.value?.[activeMetric.value]?.dates || [])
const actualScores = computed(() => chartData.value?.[activeMetric.value]?.actual || [])

function getStatusClass(idx: number): string {
  const metric = chartData.value?.[activeMetric.value]
  if (!metric?.baseline_value) return ''
  const actual = metric.actual[idx]
  const upper = metric.baseline_upper
  const lower = metric.baseline_lower
  if (actual > upper || actual < lower) return 'status-warn'
  return 'status-ok'
}

function getStatusText(idx: number): string {
  const cls = getStatusClass(idx)
  return cls === 'status-warn' ? '偏离' : '正常'
}

onShow(async () => {
  if (!petStore.currentPetId) return
  try {
    const [chart, bl] = await Promise.all([
      baselinesApi.getBaselineChart(petStore.currentPetId),
      baselinesApi.getBaselines(petStore.currentPetId),
    ])
    chartData.value = chart
    baselines.value = bl
  } catch {}
})
</script>

<style scoped>
.health-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.page-title { font-size: 36rpx; font-weight: bold; text-align: center; margin-bottom: 24rpx; }
.chart-tabs { display: flex; gap: 12rpx; margin-bottom: 24rpx; }
.tab { padding: 12rpx 24rpx; border-radius: 40rpx; background: #fff; font-size: 28rpx; }
.tab-active { background: #4CAF50; color: #fff; }
.chart-area { background: #fff; border-radius: 16rpx; padding: 24rpx; }
.baseline-info { padding: 16rpx; background: #f9f9f9; border-radius: 12rpx; margin-bottom: 16rpx; font-size: 28rpx; }
.est-yes { color: #4CAF50; margin-left: 16rpx; }
.est-no { color: #FF9800; margin-left: 16rpx; }
.data-table { font-size: 28rpx; }
.table-row { display: flex; padding: 12rpx 0; border-bottom: 1px solid #eee; }
.table-header { font-weight: bold; color: #999; }
.col-date { flex: 1; }
.col-score { flex: 1; text-align: center; }
.col-status { flex: 1; text-align: right; }
.status-ok { color: #4CAF50; }
.status-warn { color: #FF9800; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>