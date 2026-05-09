<template>
  <view class="vaccine-page">
    <text class="page-title">疫苗日历</text>

    <button class="btn-auto" @tap="autoSchedule" v-if="petId">📋 自动生成接种计划</button>

    <view class="vaccine-list">
      <view class="vaccine-card" v-for="v in vaccines" :key="v.id">
        <view class="vaccine-header">
          <text :class="['vaccine-type', v.type === 'vaccine' ? 'type-vaccine' : 'type-deworm']">
            {{ v.type === 'vaccine' ? '💉' : '🐛' }}
          </text>
          <text class="vaccine-name">{{ v.name }}</text>
          <text :class="['vaccine-status', `status-${v.status}`]">{{ statusLabel(v.status) }}</text>
        </view>
        <view class="vaccine-info">
          <text>计划日期: {{ v.scheduled_date }}</text>
          <text v-if="v.actual_date">实际日期: {{ v.actual_date }}</text>
        </view>
        <view class="vaccine-actions">
          <button class="btn-complete" v-if="v.status === 'scheduled'" @tap="markComplete(v)">✓ 已完成</button>
          <button class="btn-delete" @tap="deleteVaccine(v)">删除</button>
        </view>
      </view>
    </view>

    <view class="empty" v-if="vaccines.length === 0">
      <text>暂无疫苗记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import * as vaccinesApi from '../../api/vaccines'

const petId = ref(0)
const vaccines = ref<any[]>([])

onLoad((options: any) => {
  petId.value = parseInt(options?.petId)
})
onShow(() => { fetchVaccines() })

async function fetchVaccines() {
  if (!petId.value) return
  vaccines.value = await vaccinesApi.listVaccines(petId.value)
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = { scheduled: '待接种', completed: '已完成', overdue: '已逾期' }
  return labels[status] || status
}

async function markComplete(v: any) {
  await vaccinesApi.updateVaccine(petId.value, v.id, {
    actual_date: new Date().toISOString().split('T')[0],
    status: 'completed',
  })
  await fetchVaccines()
}

async function deleteVaccine(v: any) {
  await vaccinesApi.deleteVaccine(petId.value, v.id)
  await fetchVaccines()
}

async function autoSchedule() {
  uni.showLoading({ title: '生成计划中...' })
  try {
    const suggestions = await vaccinesApi.getVaccineSchedule(petId.value)
    for (const s of suggestions) {
      await vaccinesApi.createVaccine(petId.value, s)
    }
    await fetchVaccines()
    uni.showToast({ title: `已添加${suggestions.length}条计划`, icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '生成失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}
</script>

<style scoped>
.vaccine-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.page-title { font-size: 36rpx; font-weight: bold; text-align: center; margin-bottom: 24rpx; }
.btn-auto { background: #fff; color: #4CAF50; border: 2px solid #4CAF50; border-radius: 16rpx; height: 80rpx; font-size: 28rpx; margin-bottom: 24rpx; }
.vaccine-list { display: flex; flex-direction: column; gap: 12rpx; }
.vaccine-card { background: #fff; border-radius: 16rpx; padding: 24rpx; }
.vaccine-header { display: flex; align-items: center; gap: 12rpx; }
.vaccine-name { font-size: 30rpx; font-weight: bold; flex: 1; }
.vaccine-status { font-size: 24rpx; padding: 4rpx 12rpx; border-radius: 20rpx; }
.status-scheduled { background: #E3F2FD; color: #2196F3; }
.status-completed { background: #E8F5E9; color: #4CAF50; }
.status-overdue { background: #FFEBEE; color: #F44336; }
.vaccine-info { font-size: 26rpx; color: #666; margin-top: 8rpx; }
.vaccine-actions { display: flex; gap: 12rpx; margin-top: 12rpx; }
.btn-complete { background: #4CAF50; color: #fff; border-radius: 12rpx; font-size: 24rpx; padding: 8rpx 16rpx; height: auto; border: none; }
.btn-delete { background: #fff; color: #999; border: 1px solid #ddd; border-radius: 12rpx; font-size: 24rpx; padding: 8rpx 16rpx; height: auto; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>