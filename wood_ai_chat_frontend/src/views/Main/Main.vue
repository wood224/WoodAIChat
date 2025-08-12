<script lang="ts" setup>
import "../../assets/github-markdown.min.css";
import Header from "../../components/Main/Header.vue";
</script>

<template>
  <div class="main-wrapper">
    <Header></Header>
    <!--    <Content></Content>-->
    <router-view></router-view>
  </div>
</template>

<style lang="scss" scoped>
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;

}
</style>