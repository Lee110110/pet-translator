<template>
  <view class="checkin-page">
    <text class="page-title">{{ isUpdate ? '更新打卡' : '每日打卡' }}</text>

    <!-- 4 metrics -->
    <view class="metric-section" v-for="metric in metrics" :key="metric.key">
      <text class="metric-name">{{ metric.icon }} {{ metric.label }}</text>
      <view class="score-buttons">
        <view
          v-for="score in 5"
          :key="score"
          :class="['score-btn', scores[metric.key] === score ? 'score-btn-active' : '']"
          @tap="scores[metric.key] = score"
        >
          <text class="score-num">{{ score }}</text>
          <text class="score-label">{{ metric.scoreLabels[score as 1|2|3|4|5] }}</text>
        </view>
      </view>
      <input v-model="notes[metric.key]" class="metric-note" placeholder="备注(可选)" />
    </view>

    <!-- General note -->
    <input v-model="generalNote" class="general-note" placeholder="总体备注(可选)" />

    <!-- Submit -->
    <button class="btn-primary" @tap="submit" :disabled="loading || !allScoresSet">
      {{ loading ? 'AI正在解读...' : '提交' }}
    </button>

    <!-- Result -->
    <view class="result-card" v-if="result">
      <view class="result-header">
        <text :class="['result-level', `level-${result.ai_warning_level || 'green'}`]">
          {{ getWarningLabel(result.ai_warning_level || 'green') }}
        </text>
      </view>
      <text class="result-text">{{ result.ai_interpretation }}</text>
      <text class="result-confidence">置信度: {{ ((result.ai_confidence || 0) * 100).toFixed(0) }}%</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { usePetStore } from '../../stores/pet'
import { useCheckinStore } from '../../stores/checkin'
import { getWarningLabel } from '../../utils/format'

const petStore = usePetStore()
const checkinStore = useCheckinStore()

const scores = reactive<Record<string, number>>({ diet: 0, water: 0, stool: 0, spirit: 0 })
const notes = reactive<Record<string, string>>({ diet: '', water: '', stool: '', spirit: '' })
const generalNote = ref('')
const loading = ref(false)
const result = ref<any>(null)
const isUpdate = ref(false)
const checkinId = ref<number>(0)

const metrics = [
  { key: 'diet', label: '饮食量', icon: '🍽️', scoreLabels: { 1: '不吃', 2: '偏少', 3: '正常', 4: '不错', 5: '很好' } },
  { key: 'water', label: '饮水量', icon: '💧', scoreLabels: { 1: '不喝', 2: '偏少', 3: '正常', 4: '偏多', 5: '很多' } },
  { key: 'stool', label: '排便状态', icon: '🚽', scoreLabels: { 1: '腹泻', 2: '软便', 3: '正常', 4: '良好', 5: '很好' } },
  { key: 'spirit', label: '精神状态', icon: '😸', scoreLabels: { 1: '嗜睡', 2: '安静', 3: '正常', 4: '活跃', 5: '活跃' } },
]

const allScoresSet = computed(() => scores.diet > 0 && scores.water > 0 && scores.stool > 0 && scores.spirit > 0)

onLoad(() => {
  // If already checked in today, pre-fill scores for update
  const today = checkinStore.todayCheckin
  if (today) {
    isUpdate.value = true
    checkinId.value = today.id
    scores.diet = today.diet_score
    scores.water = today.water_score
    scores.stool = today.stool_score
    scores.spirit = today.spirit_score
    generalNote.value = today.note || ''
  }
})

async function submit() {
  if (!petStore.currentPetId) return
  loading.value = true
  try {
    const data = {
      diet_score: scores.diet,
      diet_note: notes.diet || null,
      water_score: scores.water,
      water_note: notes.water || null,
      stool_score: scores.stool,
      stool_note: notes.stool || null,
      spirit_score: scores.spirit,
      spirit_note: notes.spirit || null,
      note: generalNote.value || null,
    }
    if (isUpdate.value) {
      result.value = await checkinStore.updateCheckin(petStore.currentPetId, checkinId.value, data)
    } else {
      result.value = await checkinStore.submitCheckin(petStore.currentPetId, data)
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '提交失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.checkin-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.page-title { font-size: 36rpx; font-weight: bold; text-align: center; margin-bottom: 24rpx; }
.metric-section { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.metric-name { font-size: 32rpx; font-weight: bold; }
.score-buttons { display: flex; gap: 8rpx; margin-top: 12rpx; }
.score-btn { width: 100rpx; padding: 12rpx; border-radius: 12rpx; background: #eee; text-align: center; }
.score-btn-active { background: #4CAF50; color: #fff; }
.score-num { font-size: 32rpx; font-weight: bold; }
.score-label { font-size: 20rpx; }
.metric-note { height: 64rpx; border: 1px solid #eee; border-radius: 8rpx; padding: 12rpx; margin-top: 12rpx; font-size: 28rpx; }
.general-note { height: 96rpx; border: 1px solid #eee; border-radius: 16rpx; padding: 16rpx; margin: 16rpx 0; font-size: 28rpx; background: #fff; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; height: 96rpx; font-size: 32rpx; border: none; }
.result-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-top: 24rpx; }
.result-header { display: flex; justify-content: space-between; }
.result-level { font-size: 32rpx; font-weight: bold; }
.level-green { color: #4CAF50; }
.level-yellow { color: #FFC107; }
.level-orange { color: #FF9800; }
.level-red { color: #F44336; }
.result-text { font-size: 28rpx; margin-top: 12rpx; }
.result-confidence { font-size: 24rpx; color: #999; margin-top: 12rpx; }
</style>