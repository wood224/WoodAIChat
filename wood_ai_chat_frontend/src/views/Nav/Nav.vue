<script lang="ts" setup>
import {computed, onMounted, watch} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";
import {Conversations} from "vue-element-plus-x";
import type {ConversationItem, ConversationMenuCommand} from "vue-element-plus-x/types/Conversations";
import {deleteSession, getMessageList, getSessionList, updateSession} from "../../api/chat.ts";
import {useChatStore} from "../../store";
import {getDateRange} from "../../utils/fun.ts";
import {Plus} from "@element-plus/icons-vue";
import {useRoute, useRouter} from "vue-router";

const chatStore = useChatStore();
const router = useRouter();
const route = useRoute();

const conversationList = computed(() => {
  return chatStore.sessionList.map(item => {
    return {
      id: item.id,
      label: item.title,
      // 判断是否是今天、一周内、一月内、很久前
      group: getDateRange(item.updatedAt),
    };
  });
});

// 添加新建对话功能
const createNewSession = () => {
  router.push("/chat/");
};

// 处理会话切换
const handleChange = (sessionId: number) => {
  // 只更新 store 中的 activeSessionId
  chatStore.activeSessionId = sessionId;
};

// 路由变化处理
const handleRouteChange = async () => {
  const sessionId = Number(route.params.id);

  if (sessionId) {
    await getMessageList(sessionId);
  } else {
    // 如果没有会话 ID，设置为 undefined
    chatStore.activeSessionId = undefined;
  }
};

// 监听路由变化，设置当前激活的会话
watch(
    () => route.params.id,
    () => {
      handleRouteChange();
    },
    {immediate: true},
);

// 监听活跃会话变化，但避免重复触发路由变化
watch(
    () => chatStore.activeSessionId,
    (newSessionId) => {
      // 增加对初始化状态的判断
      if (newSessionId === undefined && route.params.id) {
        // 如果是初始加载且路由有id，不跳转，而是设置store
        chatStore.activeSessionId = Number(route.params.id);
        return;
      }

      // 只有当 store 中的 session ID 与路由中的不一致时才更新路由
      if ((!newSessionId && !route.params.id) || newSessionId === Number(route.params.id)) return;
      router.push(`/chat/${newSessionId || ""}`);
    },
    {immediate: true},
);

const handleMenuCommand = (command: ConversationMenuCommand, item: ConversationItem) => {
  if (command === "rename") {
    ElMessageBox.prompt("", "编辑对话名称", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      inputPattern: /\S/,
      inputErrorMessage: "请至少输入一个字符",
    }).then(async ({value}) => {
      await updateSession({id: item.id, title: value});
      ElMessage.success(`修改成功。`);
    });
    return;
  }
  if (command === "delete") {
    ElMessageBox.confirm("删除后，聊天记录将不可恢复。", "确定删除对话？", {
      type: "warning",
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      confirmButtonClass: "box-warning-delete-btn",
    }).then(async () => {
      await deleteSession(item.id);
      // 如果删除的是当前活跃会话，则导航到 /chat
      if (chatStore.activeSessionId === item.id) await router.push(`/chat`);
      ElMessage.success(`删除成功。`);
    });
    return;
  }
};

onMounted(async () => {
  await getSessionList();
});
</script>

<template>
  <div class="nav-container">
    <div class="nav-header">
      <h1 class="nav-title">WoodAI Chat</h1>
    </div>
    <div class="nav-controls">
      <el-button
          :icon="Plus"
          class="new-session-btn"
          round
          type="primary"
          @click="createNewSession"
      >
        新建对话
      </el-button>
    </div>
    <div class="nav-menu">
      <Conversations
          v-model:active="chatStore.activeSessionId"
          :items="conversationList || []"
          :label-max-width="200"
          :show-tooltip="true"
          :tooltip-offset="35"
          groupable
          row-key="id"
          show-built-in-menu
          show-to-top-btn
          tooltip-placement="right"
          @change="handleChange"
          @menu-command="handleMenuCommand"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.nav-container {
  background: var(--white);
  padding: 10px 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid var(--gray-200);
  box-shadow: var(--shadow-light);
  /* 增加过渡效果使整体更流畅 */
  transition: box-shadow 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-medium);
  }
}

.nav-header {
  padding: 20px 0;
  width: 100%;
  text-align: center;
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 20px;
  position: relative;

  /* 标题装饰元素 */
  &::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 3px;
    background: var(--primary-color);
    border-radius: 3px 3px 0 0;
  }

  .nav-title {
    font-size: 24px;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.5px;
    /* 标题渐变效果 */
    background: linear-gradient(90deg, var(--primary-color), var(--primary-dark));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    position: relative;
    display: inline-block;

    &::first-letter {
      font-size: 1.2em;
    }
  }
}

.nav-controls {
  width: 100%;
  max-width: 300px;
  margin-bottom: 20px;

  .new-session-btn {
    display: flex;
    align-items: center;
    width: 100%;
    height: 40px;
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
    font-weight: 500;
    transition: all 0.3s ease;

    &:hover {
      background: var(--primary-dark);
      border-color: var(--primary-dark);
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(74, 144, 226, 0.2);
    }

    :deep(.el-icon) {
      margin-right: 8px;
    }
  }
}

.nav-menu {
  flex: 1;
  display: flex;
  gap: 30px;
  width: 100%;
  max-width: 300px;
  padding-top: 10px;
  overflow-y: auto;

  /* 滚动条美化 */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--gray-100);
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--gray-300);
    border-radius: 10px;
    transition: background 0.2s ease;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--gray-400);
  }

  :deep(.conversations-list) {
    background-color: var(--white);
    border-radius: var(--border-radius-medium);
    padding: 10px;
    width: 100%;
    box-shadow: var(--shadow-light);
    border: 1px solid var(--gray-200);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: var(--shadow-medium);
    }

    .conversation-group-title {
      color: var(--primary-color);
      font-weight: 600;
      font-size: 13px;
      padding: 8px 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--gray-200);
      margin-bottom: 8px;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        left: 12px;
        bottom: -1px;
        width: 30px;
        height: 1px;
        background: var(--primary-color);
      }
    }

    .conversation-item {
      border-radius: var(--border-radius-small);
      margin-bottom: 4px;
      transition: all 0.2s ease;
      color: var(--gray-700);
      padding: 12px 14px 12px 16px;
      position: relative;
      font-size: 14px;
      cursor: pointer;
      line-height: 1.5;

      /* 文本溢出处理优化 */
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;

      /* 悬停发光效果 */
      &:hover {
        background: var(--gray-50);
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(74, 144, 226, 0.08);
      }

      &.active {
        background: rgba(74, 144, 226, 0.05);
        color: var(--primary-dark);
        font-weight: 500;
        border-left: 3px solid var(--primary-color);
        padding-left: 13px; /* 补偿左边框宽度 */
      }

      &.disabled {
        color: var(--gray-400);
        cursor: not-allowed;
        background: var(--gray-50);
        text-decoration: line-through;
        opacity: 0.8;

        &:hover {
          transform: none;
          box-shadow: none;
        }
      }
    }
  }
}
</style>