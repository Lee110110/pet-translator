<template>
  <view class="home-page">
    <!-- Pet switcher -->
    <view class="pet-bar" v-if="petStore.petList.length > 0">
      <view
        v-for="pet in petStore.petList"
        :key="pet.id"
        :class="['pet-item', pet.id === petStore.currentPetId ? 'pet-item-active' : '']"
        @tap="petStore.setCurrentPet(pet.id)"
      >
        <text class="pet-name">{{ pet.name }}</text>
      </view>
      <view class="pet-item pet-add" @tap="goPetCreate">
        <text>+</text>
      </view>
    </view>

    <!-- Empty state -->
    <view class="empty-state" v-if="petStore.petList.length === 0">
      <text class="empty-icon">🐱</text>
      <text class="empty-text">添加你的第一只猫咪吧</text>
      <button class="btn-primary" @tap="goPetCreate">添加宠物</button>
    </view>

    <!-- Status light -->
    <view class="status-section" v-if="petStore.currentPet">
      <view :class="['status-light', `status-${warningStore.getMaxLevel()}`]">
        <text class="status-emoji">{{ getLevelEmoji(warningStore.getMaxLevel()) }}</text>
      </view>
      <text class="status-label">{{ getWarningLabel(warningStore.getMaxLevel()) }}</text>

      <!-- Unread warning badge -->
      <view class="warning-badge" v-if="warningStore.dashboard.total_unread > 0" @tap="goWarningCenter">
        <text>{{ warningStore.dashboard.total_unread }}条未读预警</text>
      </view>
    </view>

    <!-- Today checkin -->
    <view class="checkin-section" v-if="petStore.currentPet">
      <view class="checkin-card" v-if="!checkinStore.todayCheckin" @tap="goCheckin">
        <text class="checkin-title">今日打卡</text>
        <text class="checkin-hint">点击记录4项健康指标</text>
      </view>
      <view class="checkin-done" v-else @tap="goCheckin">
        <text class="checkin-title">✅ 已打卡</text>
        <view class="score-row">
          <text>饮食{{ checkinStore.todayCheckin.diet_score }}</text>
          <text>饮水{{ checkinStore.todayCheckin.water_score }}</text>
          <text>排便{{ checkinStore.todayCheckin.stool_score }}</text>
          <text>精神{{ checkinStore.todayCheckin.spirit_score }}</text>
        </view>
        <text class="ai-text" v-if="checkinStore.todayCheckin.ai_interpretation">
          {{ checkinStore.todayCheckin.ai_interpretation.substring(0, 50) }}...
        </text>
      </view>
    </view>

    <!-- AI message feed -->
    <view class="feed-section" v-if="petStore.currentPet">
      <text class="section-title">近期解读</text>
      <view class="feed-card" v-for="c in checkinStore.checkinHistory.slice(0, 7)" :key="c.id">
        <view class="feed-header">
          <text class="feed-date">{{ formatDate(c.checkin_date) }}</text>
          <text :class="['feed-level', `level-${c.ai_warning_level || 'green'}`]">
            {{ getWarningLabel(c.ai_warning_level || 'green') }}
          </text>
        </view>
        <view class="feed-scores">
          <text>饮食{{ c.diet_score }} 饮水{{ c.water_score }} 排便{{ c.stool_score }} 精神{{ c.spirit_score }}</text>
        </view>
        <text class="feed-interpretation" v-if="c.ai_interpretation">{{ c.ai_interpretation }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { usePetStore } from '../../stores/pet'
import { useCheckinStore } from '../../stores/checkin'
import { useWarningStore } from '../../stores/warning'
import { useUserStore } from '../../stores/user'
import { formatDate, getWarningLabel } from '../../utils/format'

const petStore = usePetStore()
const checkinStore = useCheckinStore()
const warningStore = useWarningStore()
const userStore = useUserStore()

function getLevelEmoji(level: string): string {
  const emojis: Record<string, string> = { green: '🟢', yellow: '🟡', orange: '🟠', red: '🔴' }
  return emojis[level] || '🟢'
}

onShow(async () => {
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/login/login' })
    return
  }
  await petStore.fetchPets()
  if (petStore.currentPetId) {
    await checkinStore.fetchLatest(petStore.currentPetId)
    await checkinStore.fetchHistory(petStore.currentPetId)
    await warningStore.fetchDashboard(petStore.currentPetId)
  }
})

function goCheckin() {
  uni.navigateTo({ url: '/pages/checkin/checkin' })
}
function goPetCreate() {
  uni.navigateTo({ url: '/pages/pet-create/pet-create' })
}
function goWarningCenter() {
  uni.navigateTo({ url: '/pages/warning-center/warning-center' })
}
</script>

<style scoped>
.home-page { padding: 24rpx; min-height: 100vh; background: #f5f5f5; }
.pet-bar { display: flex; padding: 16rpx 0; gap: 16rpx; }
.pet-item { padding: 12rpx 24rpx; border-radius: 40rpx; background: #fff; font-size: 28rpx; }
.pet-item-active { background: #4CAF50; color: #fff; }
.pet-add { background: #eee; color: #999; }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.empty-icon { font-size: 120rpx; }
.empty-text { font-size: 32rpx; color: #999; margin: 24rpx 0; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; width: 240rpx; height: 80rpx; font-size: 28rpx; border: none; }
.status-section { display: flex; flex-direction: column; align-items: center; padding: 40rpx 0; }
.status-light { width: 160rpx; height: 160rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.status-green { background: #4CAF50; }
.status-yellow { background: #FFC107; }
.status-orange { background: #FF9800; animation: pulse 1.5s infinite; }
.status-red { background: #F44336; animation: pulse 1s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.status-emoji { font-size: 80rpx; }
.status-label { font-size: 36rpx; font-weight: bold; margin-top: 16rpx; }
.warning-badge { background: #F44336; color: #fff; padding: 12rpx 24rpx; border-radius: 40rpx; margin-top: 16rpx; font-size: 28rpx; }
.checkin-section { margin: 24rpx 0; }
.checkin-card { background: #fff; border-radius: 16rpx; padding: 32rpx; border: 2px solid #4CAF50; }
.checkin-title { font-size: 36rpx; font-weight: bold; }
.checkin-hint { font-size: 28rpx; color: #999; margin-top: 12rpx; }
.checkin-done { background: #fff; border-radius: 16rpx; padding: 32rpx; }
.score-row { display: flex; gap: 24rpx; margin-top: 16rpx; font-size: 28rpx; }
.ai-text { font-size: 28rpx; color: #4CAF50; margin-top: 12rpx; }
.feed-section { margin-top: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; }
.feed-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.feed-header { display: flex; justify-content: space-between; }
.feed-date { font-size: 28rpx; color: #999; }
.feed-level { font-size: 28rpx; }
.level-green { color: #4CAF50; }
.level-yellow { color: #FFC107; }
.level-orange { color: #FF9800; }
.level-red { color: #F44336; }
.feed-scores { font-size: 28rpx; margin-top: 12rpx; }
.feed-interpretation { font-size: 28rpx; margin-top: 12rpx; color: #333; }
</style>