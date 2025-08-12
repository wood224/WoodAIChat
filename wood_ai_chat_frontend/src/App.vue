<script lang="ts" setup>
import {onMounted} from "vue";
import {useAuthStore} from "./store";

onMounted(() => {
  const authStore = useAuthStore();
  authStore.restoreTokens();
});
</script>

<template>
  <router-view></router-view>
</template>

<style lang="scss" scoped>
</style>
