<template>
  <view class="pet-profile-page">
    <view class="profile-card" v-if="pet">
      <view class="profile-header">
        <text class="pet-name">{{ pet.name }}</text>
        <text :class="['pet-gender', pet.gender === 'male' ? 'gender-male' : pet.gender === 'female' ? 'gender-female' : '']">
          {{ pet.gender === 'male' ? '♂' : pet.gender === 'female' ? '♀' : '' }}
        </text>
      </view>
      <view class="info-grid">
        <view class="info-item"><text class="info-label">品种</text><text class="info-value">{{ pet.breed || '未知' }}</text></view>
        <view class="info-item"><text class="info-label">年龄</text><text class="info-value">{{ petAge }}</text></view>
        <view class="info-item"><text class="info-label">体重</text><text class="info-value">{{ pet.weight_kg ? pet.weight_kg + 'kg' : '未知' }}</text></view>
        <view class="info-item"><text class="info-label">颜色</text><text class="info-value">{{ pet.color || '未知' }}</text></view>
      </view>
    </view>

    <!-- Quick links -->
    <view class="quick-links">
      <view class="link-item" @tap="goVaccineCalendar"><text>📋 疫苗日历</text></view>
      <view class="link-item" @tap="goMedicalSummary"><text>🏥 就医摘要</text></view>
      <view class="link-item" @tap="goWarningCenter"><text>⚠️ 预警中心</text></view>
    </view>

    <button class="btn-danger" @tap="deletePet">删除宠物档案</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { usePetStore } from '../../stores/pet'

const petStore = usePetStore()
const petId = ref(0)
const pet = computed(() => petStore.petList.find(p => p.id === petId.value))
const petAge = computed(() => {
  if (!pet.value?.birthday) return '未知'
  const d = new Date(pet.value.birthday)
  const days = (Date.now() - d.getTime()) / (1000 * 86400)
  if (days < 365) return `${Math.floor(days / 30)}个月`
  return `${Math.floor(days / 365)}岁`
})

import { ref } from 'vue'

onLoad((options: any) => {
  petId.value = parseInt(options?.petId || petStore.currentPetId)
})

function goVaccineCalendar() {
  uni.navigateTo({ url: `/pages/vaccine-calendar/vaccine-calendar?petId=${petId.value}` })
}
function goMedicalSummary() {
  uni.navigateTo({ url: `/pages/medical-summary/medical-summary?petId=${petId.value}` })
}
function goWarningCenter() {
  uni.navigateTo({ url: `/pages/warning-center/warning-center?petId=${petId.value}` })
}
async function deletePet() {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法恢复，所有打卡和预警数据也会删除',
    success: async (res) => {
      if (res.confirm) {
        await petStore.deletePet(petId.value)
        uni.navigateBack()
      }
    },
  })
}
</script>

<style scoped>
.pet-profile-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.profile-card { background: #fff; border-radius: 16rpx; padding: 32rpx; }
.profile-header { display: flex; align-items: center; gap: 16rpx; }
.pet-name { font-size: 40rpx; font-weight: bold; }
.gender-male { color: #2196F3; }
.gender-female { color: #E91E63; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin-top: 24rpx; }
.info-item { display: flex; flex-direction: column; }
.info-label { font-size: 24rpx; color: #999; }
.info-value { font-size: 30rpx; font-weight: bold; margin-top: 4rpx; }
.quick-links { margin-top: 24rpx; }
.link-item { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 12rpx; font-size: 30rpx; }
.btn-danger { background: #F44336; color: #fff; border-radius: 16rpx; height: 80rpx; font-size: 28rpx; margin-top: 48rpx; border: none; }
</style>