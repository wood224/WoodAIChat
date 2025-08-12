<script lang="ts" setup>
import {computed} from "vue";
import {useAuthStore, useChatStore} from "../../store";
import {ElMessageBox} from "element-plus";
import {useRouter} from "vue-router";
import {userApi} from "../../api/";
import {Key, SwitchButton, User} from "@element-plus/icons-vue";

const authStore = useAuthStore();
const chatStore = useChatStore();
const router = useRouter();

const sessionTitle = computed(() => {
  for (const session of chatStore.sessionList) {
    if (session.id === chatStore.activeSessionId) {
      return session.title;
    }
  }
  return "未命名对话";
});

// 获取用户信息
userApi.getInfo();

const handleCommand = (command: string) => {
  switch (command) {
    case "logout":
      ElMessageBox.confirm(
          "退出登录不会丢失任何数据，你仍可以登录此账号。",
          "确认退出登录？",
          {
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            confirmButtonClass: "el-button--danger",
            type: "warning",
            center: true,
          },
      )
          .then(() => {
            logout();
          });
      break;
    case "info":
      // 跳转到用户信息页面
      router.push("/profile");
      break;
    case "changePassword":
      // 跳转到修改密码页面
      router.push("/change-pwd");
      break;
  }
};

// 控制登录组件显示/隐藏
const toggleLogin = () => {
  router.push("/login");
};

const logout = () => {
  authStore.setUserInfo(null);
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.reload();
};

</script>

<template>
  <div class="header">
    <div class="header-left">
      <div class="chat-title">
        {{ sessionTitle }}
      </div>
      <div class="tip">
        内容由 AI（豆包大模型） 生成
      </div>
    </div>
    <div class="header-right">
      <div class="menu-list">
      </div>
      <div v-if="authStore.isAuthenticated" class="avatar">
        <el-dropdown trigger="click" @command="handleCommand">
          <el-avatar :size="40" :src="authStore.getAvatarURL" fit="cover"
                     shape="square"></el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :icon="User" command="info">个人信息</el-dropdown-item>
              <el-dropdown-item :icon="Key" command="changePassword">修改密码</el-dropdown-item>
              <el-dropdown-item :icon="SwitchButton" class="logout" command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div v-else class="login-btn">
        <el-button size="large" type="primary" @click="toggleLogin">登录</el-button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.header {
  display: flex;
  justify-content: space-between;
  padding: 6px 20px;
  width: 100%;
  height: fit-content;

  .header-left {
    display: flex;
    flex-direction: column;
    justify-content: center;

    .chat-title {
      font-size: 18px;
      font-weight: bold;
    }

    .tip {
      font-size: 12px;
      color: rgba(0, 0, 0, 0.5);
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    padding-top: 20px;

    .avatar {
      width: 40px;
      height: 40px;
      cursor: pointer;
      border-radius: 50%;
      overflow: hidden;

      // 覆盖 Element Plus 的默认样式
      :deep(.el-dropdown) {
        outline: none;
      }
    }
  }
}
</style>