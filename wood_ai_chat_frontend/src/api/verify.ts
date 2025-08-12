import api from "../utils/request.ts";
import {ElMessage} from "element-plus";
import type {StandardResponse} from "../types/user.ts";

const verPath = (path: string) => `/verify${path}`;

export const get_code = (email: string, changePwd: boolean = false) => {
    return api.get<any, StandardResponse>(verPath("/email_code/"), {params: {email, changePwd}}).then(res => {
        ElMessage.success(res.message);
        return res;
    }).catch(error => {
        ElMessage.error(error.message);
        throw error;
    });
};