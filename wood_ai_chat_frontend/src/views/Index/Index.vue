<template>
  <div class="index-wrapper">
    <Nav></Nav>
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Nav from "../Nav/Nav.vue";
import {onMounted} from "vue";
import {useAuthStore} from "../../store";
import {useRouter} from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  // 如果用户未认证，重定向到登录页面
  if (!authStore.isAuthenticated) {
    router.push("/login");
  }
});
</script>

<style lang="scss" scoped>
.index-wrapper {
  position: relative;
  display: flex;
  height: 100vh;

  .main-content {
    flex: 1;
  }
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.2s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>