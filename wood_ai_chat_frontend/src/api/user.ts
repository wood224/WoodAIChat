import type {
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserInfo,
} from "../types/user.ts";
import api from "../utils/request.ts";
import {ElMessage} from "element-plus";
import {useAuthStore} from "../store";

const userPath = (path: string) => `/users${path}`;

export const login = ({username, password}: { username: string; password: string }) => {
    // 确保登录请求不携带旧的 Authorization 头
    const authStore = useAuthStore();
    return api.post<any, LoginResponse>(userPath("/login/"), {username, password}).then(res => {
        ElMessage.success(res.message);
        authStore.setUserInfo(res.data);
        authStore.setTokens(res.access, res.refresh);
        return res;
    }).catch(error => {
        ElMessage.error(error.message);
        throw error;
    });
};


export const register = (data: RegisterRequest) => {
    const req_data = {...data, confirm_password: data.confirmPassword};
    return api.post<any, RegisterResponse>(userPath("/register/"), req_data).then(res => {
        return res;
    }).catch(error => {
        ElMessage.error(error.message);
        throw error;
    });
};

export const getInfo = () => {
    const authStore = useAuthStore();
    return api.get(userPath("/query_info/")).then(res => {
        authStore.setUserInfo(res.data);
        return res;
    });
};

export const updateInfo = (data: Partial<UserInfo>) => {
    const authStore = useAuthStore();
    return api.patch(userPath(`/${data.id}/`), data).then(res => {
        authStore.setUserInfo(res.data);
        ElMessage.success("更新成功");
        return res;
    }).catch(error => {
        ElMessage.error(error.message);
        throw error;
    });
};

export const changePassword = (data: ChangePasswordRequest) => {
    return api.patch<any, ChangePasswordResponse>(userPath("/update_password/"), data).then(res => {
        return res;
    }).catch(error => {
        ElMessage.error(error.message);
        throw error;
    });
};