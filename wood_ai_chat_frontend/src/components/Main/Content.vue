<script lang="ts" setup>
import {useChatStore} from "../../store";
import {nextTick, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {CaretBottom} from "@element-plus/icons-vue";
import {Bubble, Thinking, XMarkdown} from "vue-element-plus-x";

const chatStore = useChatStore();

// 思考状态
const showThinking = ref<Set<number>>(new Set());
// 切换思考状态
const toggleThinking = (id: number) => {
  const newSet = new Set(showThinking.value);
  if (newSet.has(id)) {
    newSet.delete(id);
  } else {
    newSet.add(id);
  }
  showThinking.value = newSet;
};

// 滚动到底部
const contentRef = ref<HTMLElement | null>(null);
const scrollToBottom = async () => {
  await nextTick();

  if (contentRef.value) {
    contentRef.value.scrollTo({
      top: contentRef.value.scrollHeight,
      behavior: "smooth",
    });
  }
};

const isBottom = ref(true);
const userHasScrolledUp = ref(false);
// 检查用户是否滚动到了底部附近
const checkIfNearBottom = () => {
  if (!contentRef.value) return true;

  const {scrollTop, scrollHeight, clientHeight} = contentRef.value;
  // 距离底部100px以内认为是底部
  return scrollTop + clientHeight >= scrollHeight - 100;
};

// 监听所有消息变化（包括临时消息）并自动滚动
watch(
    () => chatStore.allMessages,
    async () => {
      // 如果用户没有主动向上滚动，则自动滚动到底部
      if (!userHasScrolledUp.value) {
        await scrollToBottom();
      }
    },
    {deep: true},
);

// 滚动事件处理函数
const handleScroll = () => {
  if (!contentRef.value) return;
  isBottom.value = !checkIfNearBottom();
  userHasScrolledUp.value = !checkIfNearBottom();
};

onMounted(() => {
  // 监听滚动事件
  contentRef.value?.addEventListener("scroll", handleScroll);
  nextTick(() => {
    scrollToBottom();
  });
});

// 在组件卸载前移除事件监听器
onBeforeUnmount(() => {
  contentRef.value?.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <div class="content-container">
    <div ref="contentRef" class="content">
      <div v-if="chatStore.activeSessionId" class="chat-list">
        <template v-for="item in chatStore.messageList">
          <div v-if="item.role === 'user'" class="user-message">
            <div class="message-content">
              <Bubble :content="item.content" placement="end"/>
            </div>
          </div>
          <div v-else class="assistant-message">
            <div class="message-content">
              <Thinking
                  v-if="item.reasoningContent"
                  :content="item.reasoningContent || ''"
                  :model-value="showThinking.has(item.id)"
                  max-width="100%"
                  status="end"
                  @update:model-value="toggleThinking(item.id)"
              />
              <XMarkdown :markdown="item.content" class="markdown-body"/>
            </div>
          </div>
        </template>
        <div v-if="chatStore.tempMessage">
          <Thinking v-if="chatStore.tempMessage.reasoningContent"
                    :content="chatStore.tempMessage.reasoningContent || ''"
                    :status="chatStore.tempMessage.thinkingStatus"
                    max-width="100%"/>
          <XMarkdown :markdown="chatStore.tempMessage.content" class="markdown-body"/>
        </div>
      </div>
      <div v-else class="welcome">
        <div class="welcome-container">
          <div class="welcome-header">
            <h1>欢迎使用 WoodAI Chat</h1>
            <p>基于AI技术的聊天助手</p>
          </div>
          <div class="welcome-features">
            <div class="feature-item">
              <i class="feature-icon">💬</i>
              <h3>对话聊天</h3>
              <p>与AI模型进行对话交流</p>
            </div>
            <div class="feature-item">
              <i class="feature-icon">📝</i>
              <h3>内容创作</h3>
              <p>协助撰写各类文本内容</p>
            </div>
            <div class="feature-item">
              <i class="feature-icon">🔍</i>
              <h3>信息查询</h3>
              <p>查询和获取各类信息</p>
            </div>
          </div>
          <div class="welcome-footer">
            <p>选择或创建一个新的聊天会话开始对话</p>
          </div>
        </div>
      </div>
    </div>
    <div v-show="userHasScrolledUp" class="scroll-bottom-wrapper">
      <div class="scroll-bottom-btn">
        <el-button :icon="CaretBottom" circle @click="scrollToBottom"></el-button>
      </div>
    </div>
  </div>
  <Footer></Footer>
</template>

<style lang="scss" scoped>
.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  overflow: auto;

  .content {
    position: relative;
    flex: 1;
    overflow: auto;
    margin: 20px 0;
    width: 100%;

    .chat-list {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin: 0 auto;
      height: 100%;
      max-width: 840px;

      .user-message, .assistant-message {
        margin: 20px 0;
        width: 100%;
      }

      .user-message {
        :deep(.el-bubble-content-wrapper) {
          .el-bubble-content {
            font-size: 16px;
          }
        }
      }
    }

    .welcome {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;

      .welcome-container {
        text-align: center;
        max-width: 800px;
        padding: 20px;

        .welcome-header {
          margin-bottom: 50px;

          h1 {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 15px;
          }

          p {
            font-size: 1.2rem;
            color: var(--gray-600);
          }
        }

        .welcome-features {
          display: flex;
          justify-content: space-around;
          flex-wrap: wrap;
          margin-bottom: 50px;

          .feature-item {
            flex: 1;
            min-width: 200px;
            margin: 15px;
            padding: 20px;
            border-radius: var(--border-radius-medium);
            background-color: var(--background-light);
            box-shadow: var(--shadow-light);

            .feature-icon {
              font-size: 2rem;
              margin-bottom: 15px;
            }

            h3 {
              color: var(--primary-dark);
              margin-bottom: 10px;
            }

            p {
              color: var(--gray-600);
            }
          }
        }

        .welcome-footer {
          p {
            font-size: 1.1rem;
            color: var(--gray-500);
          }
        }
      }
    }
  }

  .scroll-bottom-wrapper {
    position: relative;
    height: 0;

    .scroll-bottom-btn {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
    }
  }
}
</style>