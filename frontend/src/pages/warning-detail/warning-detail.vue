<template>
  <view class="warning-detail-page" v-if="warning">
    <view :class="['level-banner', `banner-${warning.level}`]">
      <text class="level-emoji">{{ getEmoji(warning.level) }}</text>
      <text class="level-text">{{ getWarningLabel(warning.level) }}</text>
    </view>

    <view class="detail-card">
      <text class="detail-label">预警详情</text>
      <text class="detail-msg">{{ warning.message }}</text>
      <text class="detail-time">{{ formatDateTime(warning.created_at) }}</text>
    </view>

    <view class="actions">
      <button class="btn-primary" @tap="startConversation">💬 开始症状对话</button>
      <button class="btn-secondary" @tap="goMedicalSummary">🏥 生成就医摘要</button>
      <button class="btn-secondary" @tap="markRead" v-if="!warning.is_read">✓ 标记已读</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as warningsApi from '../../api/warnings'
import { getWarningLabel, formatDateTime } from '../../utils/format'

const warning = ref<any>(null)
const petId = ref(0)
const warningId = ref(0)

function getEmoji(level: string): string {
  const emojis: Record<string, string> = { green: '🟢', yellow: '🟡', orange: '🟠', red: '🔴' }
  return emojis[level] || '🟢'
}

onLoad(async (options: any) => {
  petId.value = parseInt(options?.petId)
  warningId.value = parseInt(options?.warningId)
  if (petId.value && warningId.value) {
    warning.value = await warningsApi.getWarning(petId.value, warningId.value)
  }
})

function startConversation() {
  uni.navigateTo({
    url: `/pages/conversation/conversation?petId=${petId.value}&warningLevel=${warning.value.level}`
  })
}
function goMedicalSummary() {
  uni.navigateTo({
    url: `/pages/medical-summary/medical-summary?petId=${petId.value}`
  })
}
async function markRead() {
  await warningsApi.markWarningRead(petId.value, warningId.value)
  warning.value.is_read = true
}
</script>

<style scoped>
.warning-detail-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.level-banner { border-radius: 16rpx; padding: 40rpx; display: flex; flex-direction: column; align-items: center; margin-bottom: 24rpx; }
.banner-green { background: #E8F5E9; }
.banner-yellow { background: #FFF8E1; }
.banner-orange { background: #FFF3E0; }
.banner-red { background: #FFEBEE; }
.level-emoji { font-size: 80rpx; }
.level-text { font-size: 36rpx; font-weight: bold; margin-top: 12rpx; }
.detail-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 24rpx; }
.detail-label { font-size: 28rpx; color: #999; }
.detail-msg { font-size: 32rpx; margin-top: 12rpx; display: block; }
.detail-time { font-size: 24rpx; color: #999; margin-top: 12rpx; display: block; }
.actions { display: flex; flex-direction: column; gap: 12rpx; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; height: 88rpx; font-size: 30rpx; border: none; }
.btn-secondary { background: #fff; color: #333; border-radius: 16rpx; height: 88rpx; font-size: 30rpx; border: 1px solid #ddd; }
</style>