<template>
  <view class="pet-create-page">
    <text class="page-title">添加猫咪</text>

    <view class="form-group">
      <text class="label">名字 *</text>
      <input v-model="form.name" class="input" placeholder="猫咪的名字" />
    </view>

    <view class="form-group">
      <text class="label">品种</text>
      <picker :range="breedList" @change="onBreedChange">
        <view class="picker-display">{{ form.breed || '选择品种' }}</view>
      </picker>
    </view>

    <view class="form-group">
      <text class="label">生日</text>
      <picker mode="date" @change="form.birthday = $event[0]">
        <view class="picker-display">{{ form.birthday || '选择生日' }}</view>
      </picker>
    </view>

    <view class="form-group">
      <text class="label">性别</text>
      <view class="radio-group">
        <view :class="['radio-item', form.gender === 'male' ? 'radio-active' : '']" @tap="form.gender = 'male'"><text>♂ 公</text></view>
        <view :class="['radio-item', form.gender === 'female' ? 'radio-active' : '']" @tap="form.gender = 'female'"><text>♀ 母</text></view>
        <view :class="['radio-item', form.gender === 'unknown' ? 'radio-active' : '']" @tap="form.gender = 'unknown'"><text>未知</text></view>
      </view>
    </view>

    <view class="form-group">
      <text class="label">体重(kg)</text>
      <input v-model="form.weight_kg" class="input" placeholder="如: 4.5" type="digit" />
    </view>

    <view class="form-group">
      <text class="label">颜色</text>
      <input v-model="form.color" class="input" placeholder="如: 蓝色" />
    </view>

    <!-- Breed health hint -->
    <view class="breed-hint" v-if="breedHint">
      <text class="hint-title">⚠️ {{ form.breed }} 健康提示</text>
      <text class="hint-text">{{ breedHint }}</text>
    </view>

    <button class="btn-primary" @tap="submit" :disabled="!form.name || loading">
      {{ loading ? '添加中...' : '添加猫咪' }}
    </button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { usePetStore } from '../../stores/pet'

const petStore = usePetStore()
const loading = ref(false)

const form = reactive({
  name: '',
  breed: '',
  birthday: '',
  gender: 'unknown',
  weight_kg: '',
  color: '',
})

const breedData = [
  { name: '英国短毛猫(英短)', hint: '英短容易肥胖和HCM，需注意体重管理和定期心脏检查' },
  { name: '布偶猫', hint: '布偶猫有HCM遗传倾向，建议定期心脏超声' },
  { name: '波斯猫', hint: '扁脸品种易有呼吸和眼部问题，需定期清理' },
  { name: '缅因猫', hint: '大型猫种，HCM遗传测试很重要' },
  { name: '暹罗猫', hint: '非常需要陪伴，长时间独处容易出现心理问题' },
  { name: '中华田园猫', hint: '基因多样性好，遗传病较少，但老年后肾病仍常见' },
  { name: '美国短毛猫(美短)', hint: '需注意HCM风险' },
  { name: '苏格兰折耳猫', hint: '折耳猫有骨骼遗传病风险，需定期检查关节' },
  { name: '加菲猫(异国短毛猫)', hint: '扁脸品种，需注意呼吸道和眼部问题' },
  { name: '其他品种', hint: '' },
]

const breedList = breedData.map(b => b.name)
const breedHint = computed(() => {
  const b = breedData.find(b => b.name === form.breed)
  return b?.hint || ''
})

function onBreedChange(e: any) {
  form.breed = breedList[e.detail.value]
}

async function submit() {
  loading.value = true
  try {
    await petStore.createPet({
      name: form.name,
      breed: form.breed || undefined,
      birthday: form.birthday || undefined,
      gender: form.gender,
      weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : undefined,
      color: form.color || undefined,
    })
    uni.navigateBack()
  } catch (e: any) {
    uni.showToast({ title: e.message || '添加失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.pet-create-page { padding: 24rpx; background: #f5f5f5; min-height: 100vh; }
.page-title { font-size: 36rpx; font-weight: bold; text-align: center; margin-bottom: 24rpx; }
.form-group { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.label { font-size: 28rpx; color: #999; margin-bottom: 12rpx; }
.input { height: 80rpx; border: 1px solid #eee; border-radius: 12rpx; padding: 12rpx; font-size: 32rpx; }
.picker-display { height: 80rpx; border: 1px solid #eee; border-radius: 12rpx; padding: 12rpx; font-size: 32rpx; color: #333; }
.radio-group { display: flex; gap: 16rpx; }
.radio-item { padding: 16rpx 32rpx; border-radius: 12rpx; background: #eee; font-size: 28rpx; }
.radio-active { background: #4CAF50; color: #fff; }
.breed-hint { background: #FFF3E0; border-radius: 16rpx; padding: 24rpx; margin-bottom: 24rpx; }
.hint-title { font-size: 28rpx; font-weight: bold; color: #FF9800; }
.hint-text { font-size: 26rpx; color: #666; margin-top: 8rpx; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; height: 96rpx; font-size: 32rpx; border: none; }
</style>