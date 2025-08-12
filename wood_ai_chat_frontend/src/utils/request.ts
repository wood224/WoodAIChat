import {default as axios} from "axios";
import {useAuthStore} from "../store";
import router from "../router";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
    },
});

let isRefreshing = false;
let refreshSubscribers: Function[] = [];

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 只有在非登录、非注册等公开接口才添加token
        const publicPaths = ["/users/login/", "/users/register/", "/users/refresh_token/"];
        const isPublicPath = publicPaths.some(path => config.url && config.url.includes(path));

        if (!isPublicPath) {
            const authStore = useAuthStore(); // 在拦截器中动态获取 store 实例
            const access_token = authStore.access_token || localStorage.getItem("access_token");
            if (access_token) {
                config.headers.Authorization = `Bearer ${access_token}`;
            }
        }
        return config;
    },
);

// 响应拦截器
api.interceptors.response.use(
    response => {
        return response.data;
    },
    async error => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;    // （自定义属性）标记已尝试过刷新 Token

            if (!isRefreshing) {
                isRefreshing = true;    // 标记 Token 正在刷新
                const authStore = useAuthStore(); // 在需要时动态获取 store 实例
                try {
                    const refreshToken = localStorage.getItem("refresh_token");
                    const res = await api.post<any, {
                        access: string,
                        refresh: string
                    }>("/users/refresh_token/", {refresh: refreshToken});
                    const {access, refresh} = res;

                    authStore.setTokens(access, refresh);

                    // 通知所有等待的请求使用新 Token
                    refreshSubscribers.forEach(callback => callback(access));
                    refreshSubscribers = [];

                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    const retryResponse = await axios(originalRequest);  // 重试原请求
                    return retryResponse.data; // 返回处理后的数据
                } catch (err) {
                    // 刷新 Token 失败，清除 Token 并重新登录
                    authStore.$reset();
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    router.push({name: "Login"});
                    return Promise.reject(err);
                } finally {
                    isRefreshing = false;  // 重置刷新状态
                }
            } else {
                // 等待刷新完成
                return new Promise((resolve) => {
                    refreshSubscribers.push(async (accessToken: string) => {
                        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
                        const retryResponse = await axios(originalRequest);  // 重试原请求
                        resolve(retryResponse.data);  // 返回处理后的数据
                    });
                });
            }
        } else if (error.response.status >= 400 && error.response.status !== 401 && error.response.status < 500) {
            // 处理 400 错误，将错误信息返回给调用方
            return Promise.reject(error.response.data);
        }
        return Promise.reject(error);
    });

export default api;
