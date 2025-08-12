import {defineStore} from "pinia";
import type {UserInfo} from "../types/user.ts";
import {ElMessage} from "element-plus";
import {verifyApi} from "../api";

interface AuthState {
    isAuthenticated: boolean;
    access_token: string;
    refresh_token: string;
    userInfo: UserInfo | null;
    baseURL: string;
}

export const useAuthStore = defineStore("auth", {
    state: (): AuthState => ({
        isAuthenticated: false,
        access_token: "",
        refresh_token: "",
        userInfo: null,
        baseURL: import.meta.env.VITE_API_BASE_URL,
    }),

    actions: {
        setUserInfo(userInfo: UserInfo | null) {
            this.userInfo = userInfo;
            this.isAuthenticated = true;
        },

        setTokens(access_token: string, refresh_token: string) {
            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", refresh_token);
            this.access_token = localStorage.getItem("access_token") ?? "";
            this.refresh_token = localStorage.getItem("refresh_token") ?? "";
            this.isAuthenticated = true;
        },

        // 从 localStorage 恢复token
        restoreTokens() {
            const accessToken = localStorage.getItem("access_token");
            const refreshToken = localStorage.getItem("refresh_token");

            if (accessToken && refreshToken) {
                this.access_token = accessToken;
                this.refresh_token = refreshToken;
                this.isAuthenticated = true;
            }
        },

        getEmailVerityCode(email: string, action: "create" | "changePwd" = "create") {
            const changePwd = action === "changePwd";

            if (!email) {
                ElMessage.error("请输入邮箱");
                return;
            }
            if (!this.userInfo) {
                ElMessage.error("请先登录");
                return;
            }
            if (email === this.userInfo.email && !changePwd) {
                ElMessage.warning("请勿使用已绑定的邮箱");
                return;
            }
            if (email !== this.userInfo.email && changePwd) {
                ElMessage.warning("该邮箱未绑定此账号");
                return;
            }
            verifyApi.get_code(email, changePwd);
        },
    },
    getters: {
        getAvatarURL: (state) => state.baseURL + state.userInfo?.avatar,
    },
});
