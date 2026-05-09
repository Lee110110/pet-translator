<template>
  <view class="my-page">
    <view class="profile-section" v-if="userStore.userInfo">
      <text class="user-name">{{ userStore.userInfo.display_name || userStore.userInfo.username }}</text>
      <text class="user-email">{{ userStore.userInfo.email || '' }}</text>
    </view>

    <view class="pet-list">
      <text class="section-title">我的猫咪</text>
      <view class="pet-card" v-for="pet in petStore.petList" :key="pet.id" @tap="goPetProfile(pet.id)">
        <text class="pet-name">{{ pet.name }}</text>
        <text class="pet-breed">{{ pet.breed || '未知品种' }}</text>
      </view>
      <view class="pet-add-card" @tap="goPetCreate">
        <text>+ 添加猫咪</text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" @tap="goVaccineCalendar"><text>📋 疫苗日历</text></view>
      <view class="menu-item" @tap="goWarningCenter"><text>⚠️ 预警中心</text></view>
    </view>

    <button class="btn-logout" @tap="logout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '../../stores/user'
import { usePetStore } from '../../stores/pet'

const userStore = useUserStore()
const petStore = usePetStore()

onShow(async () => {
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/login/login' })
    return
  }
  await userStore.fetchProfile()
  await petStore.fetchPets()
})

function goPetProfile(petId: number) {
  uni.navigateTo({ url: `/pages/pet-profile/pet-profile?petId=${petId}` })
}
function goPetCreate() {
  uni.navigateTo({ url: '/pages/pet-create/pet-create' })
}
function goVaccineCalendar() {
  if (petStore.currentPetId) {
    uni.navigateTo({ url: `/pages/vaccine-calendar/vaccine-calendar?petId=${petStore.currentPetId}` })
  }
}
function goWarningCenter() {
  if (petStore.currentPetId) {
    uni.navigateTo({ url: `/pages/warning-center/warning-center?petId=${petStore.currentPetId}` })
  }
}
function logout() {
  userStore.logout()
}
</script>

<style scoped>
.my-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.profile-section { background: #4CAF50; border-radius: 16rpx; padding: 40rpx; margin-bottom: 24rpx; }
.user-name { font-size: 40rpx; font-weight: bold; color: #fff; display: block; }
.user-email { font-size: 28rpx; color: #C8E6C9; margin-top: 8rpx; display: block; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 12rpx; }
.pet-list { margin-bottom: 24rpx; }
.pet-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 12rpx; display: flex; justify-content: space-between; align-items: center; }
.pet-name { font-size: 32rpx; font-weight: bold; }
.pet-breed { font-size: 26rpx; color: #999; }
.pet-add-card { background: #fff; border: 2px dashed #4CAF50; border-radius: 16rpx; padding: 24rpx; text-align: center; color: #4CAF50; font-size: 28rpx; }
.menu-list { margin-bottom: 24rpx; }
.menu-item { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 12rpx; font-size: 30rpx; }
.btn-logout { background: #fff; color: #F44336; border: 1px solid #F44336; border-radius: 16rpx; height: 88rpx; font-size: 30rpx; margin-top: 24rpx; }
</style>