<script lang="ts" setup>
import {reactive, ref} from "vue";
import type {FormInstance, FormRules} from "element-plus";
import {ElMessage} from "element-plus";
import {useRouter} from "vue-router";
import type {RegisterRequest} from "../../types/user.ts";
import {userApi} from "../../api";
import {useAuthStore} from "../../store";

const router = useRouter();
const authStore = useAuthStore();

const ruleFormRef = ref<FormInstance>();
const registerForm = reactive<RegisterRequest>({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  gender: 0,
});

const validatePassword = (rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error("两次输入密码不一致"));
  } else {
    callback();
  }
};

const rules = reactive<FormRules<RegisterRequest>>({
  username: [
    {required: true, message: "请输入用户名", trigger: "blur"},
    {max: 150, message: "长度不超过150个字符", trigger: "blur"},
    {pattern: /^[\w.@+-]+$/, message: "只能包含字母、数字、特殊字符“@”、“.”、“-”和“_”", trigger: "blur"},
  ],
  email: [
    {type: "email", message: "请输入有效的邮箱地址", trigger: ["blur", "change"]},
  ],
  password: [
    {required: true, message: "请输入密码", trigger: "blur"},
    {min: 1, max: 128, message: "密码长度应在1-128个字符之间", trigger: "blur"},
  ],
  confirmPassword: [
    {required: true, message: "请确认密码", trigger: "blur"},
    {validator: validatePassword, trigger: "blur"},
  ],
});

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate(async (valid) => {
    if (valid) {
      await userApi.register(registerForm);
      ElMessage.success("注册成功，请登录");
      await router.push("/login");
    }
  });
};

const goLogin = () => {
  router.push("/login");
};
</script>

<template>
  <div class="register-wrapper">
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
        <div class="register-form">
          <el-form
              ref="ruleFormRef"
              :model="registerForm"
              :rules="rules"
              class="form-container"
              label-position="top"
              label-width="auto"
              status-icon
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                  v-model="registerForm.username"
                  prefix-icon="User"
                  size="large"
              />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input
                  v-model="registerForm.email"
                  prefix-icon="Message"
                  size="large">
                <template #append>
                  <el-button round @click="authStore.getEmailVerityCode(registerForm.email || '')">发送验证码
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="性别">
              <el-select v-model="registerForm.gender" style="width: 100%">
                <el-option :value="0" label="保密"/>
                <el-option :value="1" label="男"/>
                <el-option :value="2" label="女"/>
              </el-select>
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                  v-model="registerForm.password"
                  autocomplete="off"
                  prefix-icon="Lock"
                  show-password
                  size="large"
                  type="password"
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                  v-model="registerForm.confirmPassword"
                  autocomplete="off"
                  prefix-icon="Lock"
                  show-password
                  size="large"
                  type="password"
              />
            </el-form-item>

            <el-form-item class="button-group">
              <el-button
                  class="submit-btn"
                  show-password
                  size="large"
                  type="primary"
                  @click="submitForm(ruleFormRef)"
              >
                注册
              </el-button>
              <el-button
                  class="login-btn"
                  size="large"
                  @click="goLogin"
              >
                返回登录
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="footer">
          <p>© 2025 Wood-AI-Chat. 让AI为您的工作赋能</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.register-wrapper {
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

      .register-form {
        flex: 1;
        display: flex;
        flex-direction: column;
        width: 100%;

        .form-container {
          width: 100%;

          :deep(.el-form-item) {
            margin-bottom: 24px;

            .el-form-item__label {
              font-weight: 500;
              color: var(--gray-700);
              font-size: 14px;
            }

            .el-input__wrapper {
              border-radius: var(--border-radius-medium);
              box-shadow: var(--shadow-light);
              border: 1px solid var(--gray-300); // 添加明显的边框
              transition: all 0.3s ease;

              &:hover {
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-color: var(--primary-color); // 悬停时显示主色调边框
              }

              &.is-focus {
                box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.3);
                border-color: var(--primary-color); // 聚焦时显示主色调边框
              }
            }

            .el-input-group__append {
              border-radius: var(--border-radius-medium);
              background: linear-gradient(135deg, #63b3ed, #4f9cd9);
              border: none;
              color: var(--white);
              font-weight: 500;
              transition: all 0.3s ease;
              overflow: hidden;
              box-shadow: var(--shadow-light);

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
              }

              .el-button {
                background: transparent;
                border: none;
                color: inherit;
                font-weight: inherit;
                padding: 0 20px;
              }
            }

            .el-select {
              .el-input__wrapper {
                @extend .el-input__wrapper;
              }
            }

          }

          .button-group {
            margin-top: 30px;
            display: flex;
            gap: 15px;

            .submit-btn {
              flex: 1;
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

            .login-btn {
              flex: 1;
              background: var(--gray-50);
              border: 1px solid var(--gray-200);
              color: var(--gray-600);
              font-weight: 500;
              transition: all 0.3s ease;

              &:hover {
                background: var(--gray-100);
                border-color: var(--gray-300);
                transform: translateY(-2px);
              }
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