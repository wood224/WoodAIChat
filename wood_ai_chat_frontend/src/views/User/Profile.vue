<script lang="ts" setup>
import {computed, reactive, ref} from "vue";
import {useAuthStore} from "../../store";
import type {FormInstance, FormRules, UploadInstance, UploadProps} from "element-plus";
import {ElMessage} from "element-plus";
import type {UserGender, UserInfo} from "../../types/user.ts";
import {userApi} from "../../api";
import {useRouter} from "vue-router";
import {Plus} from "@element-plus/icons-vue";


const authStore = useAuthStore();
const router = useRouter();
const formRef = ref<FormInstance>();

// 控制编辑状态
const isEditing = ref(false);

// 性别映射
const genderMap = {
  0: "保密",
  1: "男",
  2: "女",
};

// 计算属性获取用户信息
const userInfo = computed(() => authStore.userInfo);

// 编辑表单数据
const editForm = reactive({
  id: -1,
  username: "",
  name: "",
  email: "",
  gender: 0 as UserGender,
});

// 表单验证规则
const rules = reactive<FormRules>({
  name: [
    {required: true, message: "请输入昵称", trigger: "blur"},
  ],
  email: [
    {type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"]},
  ],
  gender: [
    {required: true, message: "请选择性别", trigger: "change"},
  ],
});

// 初始化编辑表单数据
const initEditForm = () => {
  if (userInfo.value) {
    editForm.id = userInfo.value.id || -1;
    editForm.username = userInfo.value.username || "";
    editForm.name = userInfo.value.name || "";
    editForm.email = userInfo.value.email || "";
    editForm.gender = userInfo.value.gender || 0;
  }
};

// 开始编辑
const startEdit = () => {
  isEditing.value = true;
  initEditForm();
};

// 保存更改
const uploadRef = ref<UploadInstance>();
const saveChanges = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const submitData: Partial<UserInfo> = {
        id: editForm.id,
        name: editForm.name,
        gender: editForm.gender,
      };
      if (editForm.email !== authStore.userInfo?.email) {
        submitData.email = editForm.email;
      }

      await userApi.updateInfo(submitData);

      // 更新 store 中的用户信息
      await userApi.getInfo();

      isEditing.value = false;
    } else {
      ElMessage.error("请检查表单信息");
    }
  });
};

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false;
  // 重置表单验证状态
  formRef.value?.resetFields();
};

// 返回聊天界面
const goBack = () => {
  router.push("/");
  // 退出编辑模式
  isEditing.value = false;
};

// 头像上传
const imageUrl = ref(authStore.getAvatarURL);
// 计算头像上传的完整URL
const avatarUploadUrl = computed(() => {
  return `${authStore.baseURL || "http://127.0.0.1:8000"}/users/update_avatar/`;
});
// 设置上传请求头
const uploadHeaders = computed(() => {
  const accessToken = authStore.access_token || localStorage.getItem("access_token");
  if (accessToken) {
    return {
      "Authorization": `Bearer ${accessToken}`,
    };
  }
  return {};
});

const handleAvatarSuccess: UploadProps["onSuccess"] = (
    response,
    uploadFile,
) => {
  userApi.getInfo();
  imageUrl.value = URL.createObjectURL(uploadFile.raw!);
  ElMessage.success("更新头像成功");
};

const beforeAvatarUpload: UploadProps["beforeUpload"] = (rawFile) => {
  const isJPGOrPNG = rawFile.type === "image/jpeg" || rawFile.type === "image/png";

  if (!isJPGOrPNG) {
    ElMessage.error("头像必须是 JPG 或 PNG 格式!");
    return false;
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error("图片大小不能超过 2MB!");
    return false;
  }
  return true;
};
</script>

<template>
  <div class="user-profile">
    <div class="profile-content">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span>用户信息</span>
            <div class="header-actions">
              <el-button
                  v-if="!isEditing"
                  size="small"
                  type="primary"
                  @click="startEdit"
              >
                编辑信息
              </el-button>
              <div v-else>
                <el-button
                    size="small"
                    type="primary"
                    @click="saveChanges"
                >
                  保存
                </el-button>
                <el-button
                    size="small"
                    style="margin-left: 10px;"
                    @click="cancelEdit"
                >
                  取消
                </el-button>
              </div>
            </div>
          </div>
        </template>

        <div class="profile-info">
          <!-- 查看模式 -->
          <el-descriptions v-if="!isEditing" :column="1" border>
            <el-descriptions-item label="头像">
              <el-avatar :size="200" :src="authStore.getAvatarURL" fit="cover"
                         shape="square"></el-avatar>
            </el-descriptions-item>
            <el-descriptions-item label="用户名">
              {{ userInfo?.username || "未知" }}
            </el-descriptions-item>
            <el-descriptions-item label="昵称">
              {{ userInfo?.name || "未知" }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo?.email || "未设置" }}
            </el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ genderMap[userInfo?.gender || 0] }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- 编辑模式 -->
          <el-form
              v-else
              ref="formRef"
              :model="editForm"
              :rules="rules"
              class="edit-form"
              label-position="left"
              label-width="80px"
          >
            <el-form-item label="头像（上传自动更新）">
              <el-upload
                  ref="uploadRef"
                  :action="avatarUploadUrl"
                  :auto-upload="true"
                  :before-upload="beforeAvatarUpload"
                  :headers="uploadHeaders"
                  :on-success="handleAvatarSuccess"
                  :show-file-list="false"
                  class="avatar-uploader"
                  name="avatar"
              >
                <img v-if="imageUrl" :alt="editForm.name" :src="imageUrl"
                     class="avatar"/>
                <el-icon v-else class="avatar-uploader-icon">
                  <Plus/>
                </el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="用户名" prop="username">
              <el-input v-model="editForm.username" disabled></el-input>
            </el-form-item>

            <el-form-item label="昵称" prop="name">
              <el-input v-model="editForm.name"></el-input>
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email">
                <template #append>
                  <el-button round @click="authStore.getEmailVerityCode(editForm.email)">发送验证码</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="性别" prop="gender">
              <el-select v-model="editForm.gender" placeholder="请选择性别">
                <el-option :value="0" label="保密"></el-option>
                <el-option :value="1" label="男"></el-option>
                <el-option :value="2" label="女"></el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <div class="profile-actions">
            <el-button v-if="!isEditing" @click="goBack">返回聊天</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.user-profile {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 20px;
  overflow-y: auto;

  .profile-content {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;

    .profile-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
        font-size: 18px;
      }

      .profile-info {
        .edit-form {
          margin-bottom: 20px;

          .avatar-uploader {
            width: 200px;
            height: 200px;

            :deep(.el-upload) {
              width: 100%;
              height: 100%;
              border: 1px dashed var(--el-border-color);
              border-radius: 6px;
              cursor: pointer;
              position: relative;
              overflow: hidden;
              transition: var(--el-transition-duration-fast);

              &:hover {
                border-color: var(--el-color-primary);
              }
            }

            .avatar {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }

            .el-icon.avatar-uploader-icon {
              font-size: 28px;
              color: #8c939d;
              width: 178px;
              height: 178px;
              text-align: center;
            }
          }
        }

        .profile-actions {
          margin-top: 20px;
          text-align: center;
        }
      }
    }
  }
}
</style>
