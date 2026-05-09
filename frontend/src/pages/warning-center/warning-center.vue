<template>
  <view class="warning-page">
    <!-- Dashboard -->
    <view class="dashboard">
      <view class="dash-item" v-for="level in levels" :key="level.key">
        <text :class="['dash-count', `count-${level.key}`]">{{ dashboard[level.key] }}</text>
        <text class="dash-label">{{ level.label }}</text>
      </view>
    </view>

    <!-- Filter -->
    <view class="filter-tabs">
      <view :class="['filter-tab', !filterLevel ? 'filter-active' : '']" @tap="filterLevel = ''"><text>全部</text></view>
      <view v-for="level in levels" :key="level.key" :class="['filter-tab', filterLevel === level.key ? 'filter-active' : '']" @tap="filterLevel = level.key">
        <text>{{ level.label }}</text>
      </view>
    </view>

    <!-- List -->
    <view class="warning-list">
      <view class="warning-card" v-for="w in filteredWarnings" :key="w.id" @tap="goDetail(w)">
        <view class="warning-left">
          <text :class="['level-dot', `dot-${w.level}`]">●</text>
        </view>
        <view class="warning-body">
          <text class="warning-msg">{{ w.message?.substring(0, 60) }}{{ w.message?.length > 60 ? '...' : '' }}</text>
          <text class="warning-date">{{ formatDate(w.created_at) }}</text>
        </view>
        <text v-if="!w.is_read" class="unread-badge">未读</text>
      </view>
    </view>
    <view class="empty" v-if="filteredWarnings.length === 0">
      <text>{{ dashboard.total_unread > 0 ? '当前筛选无结果' : '🎉 一切正常' }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { usePetStore } from '../../stores/pet'
import { useWarningStore } from '../../stores/warning'
import { formatDate } from '../../utils/format'

const petStore = usePetStore()
const warningStore = useWarningStore()
const filterLevel = ref('')

const levels = [
  { key: 'red', label: '急症' },
  { key: 'orange', label: '异常' },
  { key: 'yellow', label: '偏离' },
  { key: 'green', label: '正常' },
]

const dashboard = computed(() => warningStore.dashboard)
const filteredWarnings = computed(() => {
  if (!filterLevel.value) return warningStore.warningList
  return warningStore.warningList.filter(w => w.level === filterLevel.value)
})

onShow(async () => {
  if (!petStore.currentPetId) return
  await warningStore.fetchDashboard(petStore.currentPetId)
  await warningStore.fetchWarnings(petStore.currentPetId)
})

function goDetail(w: any) {
  uni.navigateTo({ url: `/pages/warning-detail/warning-detail?petId=${w.pet_id}&warningId=${w.id}` })
}
</script>

<style scoped>
.warning-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.dashboard { display: flex; justify-content: space-around; background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 24rpx; }
.dash-item { display: flex; flex-direction: column; align-items: center; }
.dash-count { font-size: 40rpx; font-weight: bold; }
.count-red { color: #F44336; }
.count-orange { color: #FF9800; }
.count-yellow { color: #FFC107; }
.count-green { color: #4CAF50; }
.dash-label { font-size: 24rpx; color: #999; margin-top: 4rpx; }
.filter-tabs { display: flex; gap: 12rpx; margin-bottom: 16rpx; }
.filter-tab { padding: 8rpx 20rpx; border-radius: 40rpx; background: #fff; font-size: 24rpx; }
.filter-active { background: #4CAF50; color: #fff; }
.warning-card { display: flex; align-items: center; background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 12rpx; }
.warning-left { margin-right: 16rpx; }
.level-dot { font-size: 36rpx; }
.dot-red { color: #F44336; }
.dot-orange { color: #FF9800; }
.dot-yellow { color: #FFC107; }
.dot-green { color: #4CAF50; }
.warning-body { flex: 1; }
.warning-msg { font-size: 28rpx; color: #333; }
.warning-date { font-size: 24rpx; color: #999; display: block; margin-top: 4rpx; }
.unread-badge { font-size: 22rpx; color: #F44336; background: #FFEBEE; padding: 4rpx 12rpx; border-radius: 20rpx; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>