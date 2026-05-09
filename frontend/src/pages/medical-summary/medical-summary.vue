<template>
  <view class="medical-page">
    <text class="page-title">就医摘要</text>

    <view class="form-area">
      <view class="form-group">
        <text class="label">就诊原因</text>
        <input v-model="visitReason" class="input" placeholder="如：猫咪呕吐两天" />
      </view>
      <view class="date-row">
        <view class="form-group half">
          <text class="label">开始日期</text>
          <picker mode="date" @change="startDate = $event[0]">
            <view class="picker-display">{{ startDate || '选择日期' }}</view>
          </picker>
        </view>
        <view class="form-group half">
          <text class="label">结束日期</text>
          <picker mode="date" @change="endDate = $event[0]">
            <view class="picker-display">{{ endDate || '今天' }}</view>
          </picker>
        </view>
      </view>
    </view>

    <button class="btn-primary" @tap="generateSummary" :disabled="loading">
      {{ loading ? 'AI生成中...' : '生成就医摘要' }}
    </button>

    <view class="result-area" v-if="summary">
      <view class="summary-card">
        <text class="summary-title">📋 就诊摘要</text>
        <text class="summary-text">{{ summary.summary_text }}</text>
      </view>

      <view class="findings-card" v-if="summary.key_findings?.length">
        <text class="card-title">🔍 关键发现</text>
        <text v-for="(f, i) in summary.key_findings" :key="i" class="list-item">• {{ f }}</text>
      </view>

      <view class="findings-card" v-if="summary.recommendations?.length">
        <text class="card-title">📋 建议</text>
        <text v-for="(r, i) in summary.recommendations" :key="i" class="list-item">• {{ r }}</text>
      </view>

      <view class="findings-card" v-if="summary.suggested_tests?.length">
        <text class="card-title">🧪 建议检查</text>
        <text v-for="(t, i) in summary.suggested_tests" :key="i" class="list-item">• {{ t }}</text>
      </view>

      <button class="btn-copy" @tap="copySummary">📋 复制摘要给医生</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as medicalApi from '../../api/medical'

const petId = ref(0)
const visitReason = ref('')
const startDate = ref('')
const endDate = ref('')
const loading = ref(false)
const summary = ref<any>(null)

onLoad((options: any) => {
  petId.value = parseInt(options?.petId)
  // Default to last 7 days
  const d = new Date()
  endDate.value = d.toISOString().split('T')[0]
  d.setDate(d.getDate() - 7)
  startDate.value = d.toISOString().split('T')[0]
})

async function generateSummary() {
  loading.value = true
  try {
    summary.value = await medicalApi.generateMedicalSummary(petId.value, {
      start_date: startDate.value,
      end_date: endDate.value,
      visit_reason: visitReason.value,
    })
  } catch (e: any) {
    uni.showToast({ title: '生成失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function copySummary() {
  if (!summary.value) return
  const text = [
    summary.value.summary_text,
    '\n关键发现:', ...summary.value.key_findings.map((f: string) => `• ${f}`),
    '\n建议:', ...summary.value.recommendations.map((r: string) => `• ${r}`),
    '\n建议检查:', ...summary.value.suggested_tests.map((t: string) => `• ${t}`),
  ].join('\n')
  uni.setClipboardData({ data: text })
  uni.showToast({ title: '已复制', icon: 'success' })
}
</script>

<style scoped>
.medical-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.page-title { font-size: 36rpx; font-weight: bold; text-align: center; margin-bottom: 24rpx; }
.form-area { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 24rpx; }
.form-group { margin-bottom: 16rpx; }
.half { flex: 1; }
.label { font-size: 28rpx; color: #999; margin-bottom: 8rpx; }
.input { height: 80rpx; border: 1px solid #eee; border-radius: 12rpx; padding: 12rpx; font-size: 30rpx; }
.picker-display { height: 80rpx; border: 1px solid #eee; border-radius: 12rpx; padding: 12rpx; font-size: 30rpx; }
.date-row { display: flex; gap: 16rpx; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; height: 96rpx; font-size: 32rpx; border: none; }
.result-area { margin-top: 24rpx; }
.summary-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.summary-title { font-size: 32rpx; font-weight: bold; display: block; margin-bottom: 12rpx; }
.summary-text { font-size: 28rpx; line-height: 1.6; }
.findings-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.card-title { font-size: 30rpx; font-weight: bold; display: block; margin-bottom: 8rpx; }
.list-item { font-size: 28rpx; display: block; margin: 4rpx 0; }
.btn-copy { background: #2196F3; color: #fff; border-radius: 16rpx; height: 88rpx; font-size: 30rpx; border: none; }
</style>