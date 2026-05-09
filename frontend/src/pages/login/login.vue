<template>
  <view class="login-page">
    <view class="logo-area">
      <text class="logo-icon">🐱</text>
      <text class="app-name">AI宠物翻译官</text>
      <text class="app-desc">帮你发现宠物你没注意到的健康异常</text>
    </view>

    <view class="form-area">
      <view class="input-group">
        <input v-model="username" class="input" placeholder="用户名" type="text" />
        <input v-model="password" class="input" placeholder="密码" type="password" />
        <input v-if="isRegister" v-model="email" class="input" placeholder="邮箱(可选)" type="text" />
        <input v-if="isRegister" v-model="displayName" class="input" placeholder="昵称(可选)" type="text" />
      </view>

      <button class="btn-primary" @tap="handleSubmit" :disabled="loading">
        {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
      </button>

      <view class="switch-mode" @tap="isRegister = !isRegister">
        <text>{{ isRegister ? '已有账号？点击登录' : '没有账号？点击注册' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const username = ref('')
const password = ref('')
const email = ref('')
const displayName = ref('')
const isRegister = ref(false)
const loading = ref(false)

async function handleSubmit() {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    if (isRegister.value) {
      await userStore.register(username.value, password.value, email.value, displayName.value)
    } else {
      await userStore.login(username.value, password.value)
    }
    uni.switchTab({ url: '/pages/home/home' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  padding: 80rpx 40rpx;
  background: #f5f5f5;
  min-height: 100vh;
}
.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}
.logo-icon {
  font-size: 120rpx;
}
.app-name {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  margin-top: 20rpx;
}
.app-desc {
  font-size: 28rpx;
  color: #999;
  margin-top: 12rpx;
}
.form-area {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
}
.input-group {
  margin-bottom: 32rpx;
}
.input {
  height: 96rpx;
  border: 1px solid #eee;
  border-radius: 16rpx;
  padding: 0 24rpx;
  margin-bottom: 16rpx;
  font-size: 32rpx;
}
.btn-primary {
  background: #4CAF50;
  color: #fff;
  border-radius: 16rpx;
  height: 96rpx;
  font-size: 32rpx;
  border: none;
}
.switch-mode {
  text-align: center;
  margin-top: 24rpx;
  color: #4CAF50;
  font-size: 28rpx;
}
</style>