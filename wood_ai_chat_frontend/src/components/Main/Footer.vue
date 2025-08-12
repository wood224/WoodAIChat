<script lang="ts" setup>
import {Check, Close, ElementPlus, MagicStick, Paperclip, Promotion} from "@element-plus/icons-vue";
import {MentionSender} from "vue-element-plus-x";
import {markRaw, ref} from "vue";
import {ElMessage} from "element-plus";
import {useChatStore} from "../../store";
import {abortCurrentRequest, sendMessage} from "../../api/chat.ts";

const chatStore = useChatStore();

const senderPlaceholder = "💌 欢迎使用 Wood-AI-Chat ~（Enter 提交，Shift + Enter 换行）";

const senderRef = ref();
const submitBtnDisabled = ref(false);
const senderValue = ref("");
const senderLoading = ref(false);

const thinkType = ref(Number(localStorage.getItem("think_type")) || 0);
const thinkList = [
  {name: "关", desc: "快速直接回答", icon: markRaw(Close)},
  {name: "开", desc: "输出带推理过程的答案", icon: markRaw(Check)},
  {name: "自动", desc: "根据上下文智能切换", icon: markRaw(MagicStick)},
];

// 发送消息
const handleSubmit = () => {
  submitBtnDisabled.value = true;
  senderLoading.value = true;

  sendMessage({
    content: senderValue.value,
    sessionId: chatStore.activeSessionId,
    parentMessageId: chatStore.lastAssistantMessage?.id || null,
    modelId: "doubao-seed-1-6-flash-250715",
    thinkType: thinkType.value,
  }).then(() => {
    senderLoading.value = false;
    submitBtnDisabled.value = false;
  });

  // 更新会话时间
  chatStore.updateSessionTime(chatStore.activeSessionId);
  // 清空输入框
  senderValue.value = "";
};

// 取消发送
function handleCancel() {
  senderLoading.value = false;
  ElMessage.info(`取消发送`);
  abortCurrentRequest();
}

const handleThinkCommand = (value: number) => {
  thinkType.value = value;
  localStorage.setItem("think_type", value.toString());
};

const selectUpload = () => {
  ElMessage.info(`上传功能尚未实现`);
};
</script>

<template>
  <div class="footer">
    <MentionSender ref="senderRef" v-model="senderValue" :auto-size="{ minRows: 2, maxRows: 5 }"
                   :placeholder="senderPlaceholder" :submit-btn-disabled="submitBtnDisabled" allow-speech
                   variant="updown" @submit="handleSubmit">
      <template #prefix>
        <div style="display: flex;align-items: center;gap: 8px; flex-wrap: wrap;">
          <el-button color="#626aef" plain round @click="selectUpload">
            <el-icon>
              <Paperclip/>
            </el-icon>
          </el-button>
          <el-dropdown trigger="click" @command="handleThinkCommand">
            <div :class="['depth-thinking', { 'is-select': thinkType }]">
              <el-icon :size="20">
                <ElementPlus/>
              </el-icon>
              <span>深度思考：{{ thinkList[thinkType].name }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <template v-for="(item,index) in thinkList">
                  <el-dropdown-item :command="index">
                    <div :style="index === thinkType ? {color: 'var(--primary-color)',fontWeight: 'bold'} : {}"
                         style="display: flex">
                      <div class="icon">
                        <el-icon :size="16">
                          <component :is="item.icon"/>
                        </el-icon>
                      </div>
                      <div class="text">
                        <div>
                          {{ item.name }}
                        </div>
                        <div style="font-size: 14px; color: var(--secondary-light)">
                          {{ item.desc }}
                        </div>
                      </div>
                    </div>
                  </el-dropdown-item>
                </template>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>

      <template #action-list>
        <div v-if="!senderLoading" style="display: flex; align-items: center;">
          <el-button round type="primary" @click="handleSubmit">
            <el-icon>
              <Promotion/>
            </el-icon>
          </el-button>
        </div>
        <template v-else>
          <div class="cancel-button" @click="handleCancel">
            <div class="cancel-rotate"></div>
            <div class="cancel-inner"></div>
          </div>
        </template>
      </template>
    </MentionSender>
  </div>
</template>

<style lang="scss" scoped>
.footer {
  width: 100%;
  max-width: 840px;
  max-height: 300px;

  :deep(.el-sender-wrap) {
    .el-textarea__inner {
      font-size: 16px;
    }
  }

  .depth-thinking {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 2px 12px;
    border: 1px solid silver;
    border-radius: 15px;
    height: 32px;
    cursor: pointer;
    transition: all 0.3s ease; // 添加过渡效果

    // 默认状态
    background-color: transparent;
    color: #333;

    // 激活状态
    &.is-select {
      background-color: #409eff; // Element Plus 主题色
      color: white;
      border-color: #409eff;
      box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
    }

    // 悬停效果
    &:hover {
      border-color: #409eff;
    }
  }

  .cancel-button {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    color: white;
    overflow: hidden;
    cursor: pointer;

    .cancel-rotate {
      width: 100%;
      height: 100%;
      border: rgba(0, 0, 255, 0.1) 6px solid;
      border-radius: 50%;
      border-top: var(--primary-color) 4px solid;
      animation: spin 1s linear infinite;
    }

    .cancel-inner {
      position: absolute;
      top: 50%;
      left: 50%;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-color: white;
      transform: translate(-50%, -50%);

      &::after {
        content: '';
        width: 8px;
        height: 8px;
        background-color: var(--primary-color);
      }
    }

    @keyframes spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
  }
}
</style>