<script lang="ts" setup>
import {reactive, ref} from "vue";
import type {FormInstance, FormRules} from "element-plus";
import {ElMessage} from "element-plus";
import {useRouter} from "vue-router";
import {userApi} from "../../api";
import {useAuthStore} from "../../store";

const router = useRouter();
const authStore = useAuthStore();

const ruleFormRef = ref<FormInstance>();

const ruleForm = reactive({
  email: authStore.userInfo?.email || "",
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const validateNewPassword = (_: any, value: string, callback: any) => {
  if (value !== ruleForm.newPassword) {
    callback(new Error("两次输入的新密码不一致"));
  } else {
    callback();
  }
};

const rules = reactive<FormRules>({
  email: [
    {required: true, message: "请输入邮箱地址", trigger: "blur"},
    {type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"]},
  ],
  oldPassword: [
    {required: true, message: "请输入当前密码", trigger: "blur"},
    {min: 1, max: 128, message: "密码长度应在1-128个字符之间", trigger: "blur"},
  ],
  newPassword: [
    {required: true, message: "请输入新密码", trigger: "blur"},
    {min: 1, max: 128, message: "密码长度应在1-128个字符之间", trigger: "blur"},
  ],
  confirmPassword: [
    {required: true, message: "请确认新密码", trigger: "blur"},
    {validator: validateNewPassword, trigger: "blur"},
  ],
});

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;

  if (!authStore.userInfo) {
    ElMessage.error("用户信息不存在");
    return;
  }

  await formEl.validate(async (valid) => {
    if (valid) {
      try {
        await userApi.changePassword({
          email: ruleForm.email,
          oldPassword: ruleForm.oldPassword,
          newPassword: ruleForm.newPassword,
          confirmPassword: ruleForm.confirmPassword,
        });
        ElMessage.success("修改成功，请重新登陆");

        // 修改成功后退出登录，需要重新登录
        authStore.setUserInfo(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        await router.push("/login");
      } catch (error) {
        console.error(error);
      }
    }
  });
};

const goBack = () => {
  router.back();
};
</script>

<template>
  <div class="change-password-wrapper">
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
        <div class="change-password-form">
          <el-form
              ref="ruleFormRef"
              :model="ruleForm"
              :rules="rules"
              class="form-container"
              label-position="top"
              label-width="auto"
              status-icon
          >
            <el-form-item label="邮箱" prop="email">
              <el-input
                  v-model="ruleForm.email"
                  autocomplete="off"
                  prefix-icon="Message"
                  size="large"
              >
                <template #append>
                  <el-button round @click="authStore.getEmailVerityCode(ruleForm.email || '', 'changePwd')">发送验证码
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="当前密码" prop="oldPassword">
              <el-input
                  v-model="ruleForm.oldPassword"
                  autocomplete="off"
                  prefix-icon="Lock"
                  show-password
                  size="large"
                  type="password"
              />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input
                  v-model="ruleForm.newPassword"
                  autocomplete="off"
                  prefix-icon="Lock"
                  show-password
                  size="large"
                  type="password"
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                  v-model="ruleForm.confirmPassword"
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
                  size="large"
                  type="primary"
                  @click="submitForm(ruleFormRef)"
              >
                修改密码
              </el-button>
              <el-button
                  class="back-btn"
                  size="large"
                  @click="goBack"
              >
                返回
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.change-password-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  padding: 20px;
  box-sizing: border-box;

  .card {
    position: relative;
    display: flex;
    width: 900px;
    height: 600px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    z-index: 1;
    backdrop-filter: blur(10px);

    .left {
      position: relative;
      flex: 1;
      height: 100%;
      overflow: hidden;

      .image-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;

        z-index: 1;
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .right {
      flex: 1;
      padding: 40px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      box-sizing: border-box;

      .title {
        text-align: center;
        margin-bottom: 30px;

        h1 {
          font-size: 32px;
          font-weight: bold;
          margin-bottom: 10px;
          background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
          background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        p {
          font-size: 16px;
          color: #666;
        }
      }

      .change-password-form {
        .form-container {
          :deep(.el-form-item__label) {
            font-weight: bold;
            color: #333;
          }

          :deep(.el-input__wrapper) {
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;

            &:hover {
              box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            }

            &.is-focus {
              box-shadow: 0 6px 15px rgba(102, 126, 234, 0.3);
            }
          }

          .button-group {
            margin-top: 30px;

            .submit-btn {
              flex: 1;
              border-radius: 10px;
              background: var(--el-color-primary);
              border: none;
              font-weight: bold;
              letter-spacing: 1px;
              transition: all 0.3s ease;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
              }
            }

            .back-btn {
              flex: 1;
              border-radius: 10px;
              border: 1px solid #ddd;
              font-weight: bold;
              transition: all 0.3s ease;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                border-color: #667eea;
                color: #667eea;
              }
            }
          }
        }
      }
    }
  }

  @media (max-width: 768px) {
    padding: 10px;

    .card {
      flex-direction: column;
      width: 100%;
      height: auto;

      .left {
        display: none;
      }

      .right {
        padding: 30px 20px;
      }
    }
  }
}
</style>
