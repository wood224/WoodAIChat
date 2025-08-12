// 用户性别枚举

export type UserGender = 0 | 1 | 2;

// 注册请求参数
export interface RegisterRequest {
    username: string;
    email?: string;
    password: string;
    confirmPassword: string;
    gender?: UserGender;
}

// 用户信息
export interface UserInfo {
    id: number;
    username: string;
    name: string;
    email: string;
    gender: UserGender;
    isActive: boolean;
    dateJoined: string;
    lastLogin?: string;
    avatar: string;
}

// 标准响应格式
export interface StandardResponse<T = any> {
    data: T;
    message: string;
    timestamp: string;
    status: number;

    [key: string]: any; // 用于额外的响应字段，如 access_token 等
}

// 注册响应数据
export interface RegisterResponse extends StandardResponse<UserInfo> {
}

// 登录请求参数
export interface LoginRequest {
    username: string;
    password: string;
}

// 登录响应数据
export interface LoginResponse extends StandardResponse<UserInfo> {
    access: string;
    refresh: string;
    expiresIn: number;
}

// 修改密码请求参数
export interface ChangePasswordRequest {
    email: string;
    oldPassword: string;
    newPassword: string;
    confirmPassword: string;
}

// 修改密码响应数据
export interface ChangePasswordResponse extends StandardResponse<UserInfo> {
}
