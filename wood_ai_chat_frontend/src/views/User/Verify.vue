<script lang="ts" setup>
import {onMounted, ref} from "vue";
import {useRouter} from "vue-router";

const success = ref(false);
const message = ref("");
const router = useRouter();

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  success.value = urlParams.get("success") === "true";
  message.value = urlParams.get("message") || (success.value ? "验证成功" : "验证失败");
});

const goToRegister = () => {
  router.push("/register");
};
</script>

<template>
  <div class="verify-wrapper">
    <div class="mask"></div>
    <div class="card">
      <div class="left">
        <div class="image-overlay"></div>
        <img alt="" src="../../assets/images/login.png">
      </div>
      <div class="right">
        <div class="title">
          <h1>Wood-AI-Chat</h1>
          <p>智能对话，创造无限可能</p>
        </div>
        <div class="verify-result">
          <div v-if="success" class="result success">
            <div class="icon success-icon">✓</div>
            <h2>验证成功</h2>
            <p>{{ message }}</p>
            <p>请继续完成注册</p>
          </div>
          <div v-else class="result error">
            <div class="icon error-icon">✗</div>
            <h2>验证失败</h2>
            <p>{{ message }}</p>
            <el-button
                class="action-btn"
                size="large"
                @click="goToRegister"
            >
              重新注册
            </el-button>
          </div>
        </div>
        <div class="footer">
          <p>© 2025 Wood-AI-Chat. 让AI为您的工作赋能</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.verify-wrapper {
  position: absolute;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 20px;

  .mask {
    position: absolute;
    z-index: 1;
    width: 100%;
    height: 100%;
    background-color: rgba(22, 22, 26, .6);
  }

  .card {
    display: flex;
    width: 900px;
    min-height: 500px;
    border-radius: var(--border-radius-large);
    box-shadow: var(--shadow-heavy);
    background-color: var(--white);
    overflow: hidden;
    backdrop-filter: blur(10px);
    z-index: 99;

    .left {
      width: 40%;
      min-width: 300px;
      position: relative;
      overflow: hidden;

      .image-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(100, 149, 237, 0.2) 0%, rgba(65, 105, 225, 0.1) 100%);
        z-index: 1;
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
      }

      &:hover img {
        transform: scale(1.05);
      }
    }

    .right {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 40px 50px;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(to bottom, rgba(100, 149, 237, 0.1), rgba(65, 105, 225, 0.2), rgba(100, 149, 237, 0.1));
      }

      .title {
        text-align: center;
        margin-bottom: 30px;

        h1 {
          font-size: 28px;
          font-weight: 600;
          color: var(--gray-800);
          margin-bottom: 10px;
          background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        p {
          font-size: 14px;
          color: var(--gray-500);
          margin: 0;
        }
      }

      .verify-result {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;

        .result {
          text-align: center;
          padding: 30px;
          border-radius: var(--border-radius-large);
          width: 100%;
          max-width: 400px;

          .icon {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 40px;
            font-weight: bold;
          }

          .success-icon {
            background-color: rgba(52, 211, 153, 0.2);
            color: #34d399;
          }

          .error-icon {
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
          }

          h2 {
            font-size: 24px;
            margin-bottom: 15px;
            color: var(--gray-800);
          }

          p {
            font-size: 16px;
            color: var(--gray-600);
            margin-bottom: 30px;
            line-height: 1.5;
          }

          .action-btn {
            width: 100%;
            background: linear-gradient(135deg, #63b3ed, #4f9cd9);
            border: none;
            color: var(--white);
            font-weight: 500;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
            }
          }
        }

        .error {
          .action-btn {
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            color: var(--gray-600);

            &:hover {
              background: var(--gray-100);
              border-color: var(--gray-300);
            }
          }
        }
      }

      .footer {
        text-align: center;
        margin-top: 30px;

        p {
          font-size: 12px;
          color: var(--gray-400);
          margin: 0;
        }
      }
    }
  }

  // 响应式设计
  @media (max-width: 768px) {
    .card {
      flex-direction: column;
      width: 95%;
      max-width: 500px;

      .left {
        width: 100%;
        height: 200px;
      }

      .right {
        padding: 30px 20px;

        &::before {
          width: 100%;
          height: 2px;
          top: 0;
          left: 0;
          right: 0;
          bottom: auto;
        }
      }
    }
  }
}
</style>
