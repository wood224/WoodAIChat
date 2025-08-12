import {createRouter, createWebHistory} from "vue-router";
import {useAuthStore} from "../store";

const routes = [
    {
        path: "/",
        name: "Index",
        component: () => import("../views/Index/Index.vue"),
        children: [
            {
                path: "",
                name: "Main",
                component: () => import("../views/Main/Main.vue"),
                children: [
                    {
                        path: "chat/:id?",
                        name: "Chat",
                        component: () => import("../components/Main/Content.vue"),
                    },
                ],
                meta: {requiresAuth: true},
            },
            {
                path: "profile",
                name: "Profile",
                component: () => import("../views/User/Profile.vue"),
                meta: {requiresAuth: true},
            },
            {
                path: "change-pwd",
                name: "ChangePwd",
                component: () => import("../views/User/ChangePassword.vue"),
                meta: {requiresAuth: true},
            },
        ],
    },
    {
        path: "/login",
        name: "Login",
        component: () => import("../views/User/Login.vue"),
    },
    {
        path: "/register",
        name: "Register",
        component: () => import("../views/User/Register.vue"),
    },
    {
        path: "/verify-result",
        name: "VerifyResult",
        component: () => import("../views/User/Verify.vue"),
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// 添加路由守卫
router.beforeEach((to, _, next) => {
    const authStore = useAuthStore();

    // 设置标题
    document.title = "Wood-AI-Chat";

    // 检查目标路由是否需要认证
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // 如果需要认证但未认证，重定向到登录
        next("/login");
    } else {
        // 否则正常导航
        next();
    }
});

export default router;