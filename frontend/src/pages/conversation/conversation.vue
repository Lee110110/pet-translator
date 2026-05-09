<template>
  <view class="conversation-page">
    <view class="round-indicator">
      <text>Round {{ conversation?.current_round || 0 }} / {{ conversation?.max_rounds || 3 }}</text>
    </view>

    <!-- Messages -->
    <scroll-view class="messages" scroll-y :scroll-top="scrollTop" :scroll-with-animation="true">
      <view v-for="msg in messages" :key="msg.id" :class="['msg-row', msg.role === 'user' ? 'msg-right' : 'msg-left']">
        <view :class="['msg-bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-ai']">
          <!-- AI message: parse JSON content -->
          <template v-if="msg.role === 'assistant'">
            <view v-if="parseAiContent(msg.content)">
              <text class="ai-question" v-if="parsedContent.question">{{ parsedContent.question }}</text>
              <view class="ai-options" v-if="parsedContent.options && !isFinalRound">
                <view v-for="(opt, i) in parsedContent.options" :key="i" class="option-btn" @tap="selectOption(opt)">
                  <text>{{ opt }}</text>
                </view>
              </view>
              <text class="ai-assessment" v-if="parsedContent.assessment">💡 {{ parsedContent.assessment }}</text>
              <text class="ai-recommendation" v-if="parsedContent.recommendation">📋 {{ parsedContent.recommendation }}</text>
            </view>
            <text v-else>{{ msg.content }}</text>
          </template>
          <text v-else>{{ msg.content }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Input -->
    <view class="input-area" v-if="conversation?.status === 'active'">
      <input v-model="inputText" class="msg-input" placeholder="描述症状..." :disabled="aiLoading" />
      <button class="send-btn" @tap="sendReply" :disabled="aiLoading || !inputText">发送</button>
    </view>
    <view class="input-area ended" v-else>
      <text>对话已结束</text>
    </view>

    <!-- Start conversation form -->
    <view class="start-form" v-if="!conversation">
      <text class="form-title">描述你观察到的症状</text>
      <textarea v-model="initialSymptoms" class="symptoms-input" placeholder="如：今天吐了、不怎么吃东西..." />
      <button class="btn-primary" @tap="startConversation" :disabled="!initialSymptoms || aiLoading">
        {{ aiLoading ? 'AI分析中...' : '开始分析' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as conversationsApi from '../../api/conversations'

const petId = ref(0)
const conversation = ref<any>(null)
const messages = ref<any[]>([])
const inputText = ref('')
const initialSymptoms = ref('')
const aiLoading = ref(false)
const scrollTop = ref(0)
const parsedContent = ref<any>({})
const warningLevel = ref('yellow')
const checkinId = ref<number | null>(null)

const isFinalRound = computed(() => conversation.value?.current_round >= conversation.value?.max_rounds)

function parseAiContent(content: string): boolean {
  try {
    parsedContent.value = JSON.parse(content)
    return !!parsedContent.value.question || !!parsedContent.value.assessment
  } catch {
    return false
  }
}

onLoad((options: any) => {
  petId.value = parseInt(options?.petId)
  warningLevel.value = options?.warningLevel || 'yellow'
  checkinId.value = options?.checkinId ? parseInt(options.checkinId) : null
  const convId = options?.conversationId
  if (convId) {
    loadConversation(parseInt(convId))
  }
})

async function loadConversation(convId: number) {
  conversation.value = await conversationsApi.getConversation(petId.value, convId)
  messages.value = conversation.value.messages || []
  scrollToBottom()
}

async function startConversation() {
  aiLoading.value = true
  try {
    const data: any = { initial_symptoms: initialSymptoms.value, warning_level: warningLevel.value }
    if (checkinId.value) data.checkin_id = checkinId.value
    conversation.value = await conversationsApi.startConversation(petId.value, data)
    messages.value = conversation.value.messages || []
    scrollToBottom()
  } catch (e: any) {
    uni.showToast({ title: '启动对话失败', icon: 'none' })
  } finally {
    aiLoading.value = false
  }
}

async function sendReply() {
  if (!inputText.value || !conversation.value) return
  const text = inputText.value
  inputText.value = ''
  aiLoading.value = true
  try {
    conversation.value = await conversationsApi.replyConversation(petId.value, conversation.value.id, { content: text })
    messages.value = conversation.value.messages || []
    scrollToBottom()
  } catch (e: any) {
    uni.showToast({ title: e.message || '回复失败', icon: 'none' })
  } finally {
    aiLoading.value = false
  }
}

function selectOption(opt: string) {
  inputText.value = opt
  sendReply()
}

function scrollToBottom() {
  setTimeout(() => { scrollTop.value = 99999 }, 100)
}
</script>

<style scoped>
.conversation-page { display: flex; flex-direction: column; height: 100vh; background: #f5f5f5; }
.round-indicator { text-align: center; padding: 16rpx; background: #fff; font-size: 28rpx; color: #4CAF50; font-weight: bold; }
.messages { flex: 1; padding: 16rpx; }
.msg-row { margin-bottom: 16rpx; display: flex; }
.msg-left { justify-content: flex-start; }
.msg-right { justify-content: flex-end; }
.msg-bubble { max-width: 80%; padding: 20rpx; border-radius: 16rpx; font-size: 28rpx; }
.bubble-ai { background: #fff; color: #333; }
.bubble-user { background: #4CAF50; color: #fff; }
.ai-question { font-weight: bold; display: block; margin-bottom: 12rpx; }
.ai-options { display: flex; flex-wrap: wrap; gap: 8rpx; margin-bottom: 12rpx; }
.option-btn { background: #E8F5E9; color: #4CAF50; padding: 8rpx 20rpx; border-radius: 40rpx; font-size: 26rpx; }
.ai-assessment { display: block; color: #FF9800; margin-top: 8rpx; }
.ai-recommendation { display: block; color: #2196F3; margin-top: 8rpx; }
.input-area { display: flex; padding: 16rpx; background: #fff; gap: 12rpx; }
.msg-input { flex: 1; height: 72rpx; border: 1px solid #ddd; border-radius: 36rpx; padding: 0 24rpx; font-size: 28rpx; }
.send-btn { background: #4CAF50; color: #fff; border-radius: 36rpx; height: 72rpx; padding: 0 32rpx; font-size: 28rpx; border: none; }
.ended { justify-content: center; }
.start-form { padding: 40rpx; background: #fff; }
.form-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; }
.symptoms-input { width: 100%; height: 200rpx; border: 1px solid #ddd; border-radius: 16rpx; padding: 16rpx; font-size: 28rpx; margin-bottom: 16rpx; }
.btn-primary { background: #4CAF50; color: #fff; border-radius: 16rpx; height: 88rpx; font-size: 30rpx; border: none; }
</style>