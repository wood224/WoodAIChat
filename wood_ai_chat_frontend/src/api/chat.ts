import api from "../utils/request.ts";
import {useChatStore} from "../store";
import {ElMessage} from "element-plus";
import type {ChatMessage, ChatSession, CreateChatMessageRequest} from "../types/chat.ts";

// 聊天
const chatPath = (path: string) => `/chat${path}`;

export const getMessageList = async (id: number) => {
    const chatStore = useChatStore();
    return api.get(chatPath(`/message/`), {
        params: {"session_id": id},
    }).then(res => {
        chatStore.setMessageList(res.data);
    });
};

// 定义一个变量存储当前的AbortController，用于中断请求
let abortController: AbortController | null = null;
// 中断当前请求的方法
export const abortCurrentRequest = () => {
    if (abortController) {
        abortController.abort();
        abortController = null;
        // 清理临时消息
        // const chatStore = useChatStore();
        // chatStore.clearTempMessage();
    }
};
export const sendMessage = async (data: CreateChatMessageRequest) => {
    // 先取消可能存在的未完成请求
    if (abortController) {
        abortController.abort();
    }

    // 创建新的AbortController
    abortController = new AbortController();
    const {signal} = abortController;

    const chatStore = useChatStore();

    try {
        // 用户消息提交请求
        const userMessageRes = await api.post(chatPath(`/message/`), data);
        chatStore.addMessage(userMessageRes.data);
        const user_message_id = userMessageRes.data.id;

        // 获取 AI 流式响应
        // 使用 fetch 发起 POST 请求并手动处理流式响应
        const res = await fetch(api.defaults.baseURL + chatPath(`/message/ai-response/`), {
            method: "POST",
            body: JSON.stringify({...data, user_message_id}),
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
            signal, // 将signal传递给fetch
        });

        if (!res.ok || !res.body) {
            return new Error(`请求失败: ${res.status} ${res.statusText}`);
        }

        // 临时消息标记
        let isFirstChunk = true;

        // 读取流式响应
        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        // 初始化消息结构
        let finalMessage: ChatMessage | null = null;

        while (true) {
            // 检查是否已中止
            if (signal.aborted) {
                throw new Error("生成已被终止");
            }

            const {done, value} = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, {stream: true});
            const lines = chunk.split("\n\n");

            for (const line of lines) {
                if (line.startsWith("data:")) {
                    const jsonStr = line.slice(5).trim(); // 去除 "data:" 前缀
                    try {
                        const data = JSON.parse(jsonStr);
                        const message = data.data;
                        // 获取初始化数据
                        if (data.type === "message_start") {
                            finalMessage = {
                                id: message.id,
                                role: "assistant",
                                reasoningContent: message.reasoning_content,
                                content: message.content,
                                createdAt: message.created_at,
                                tokens: message.tokens,
                                messageRespId: message.message_resp_id,
                                session: {
                                    id: message.session.id,
                                    title: message.session.title,
                                    user: message.session.user,
                                    updatedAt: message.session.updated_at,
                                    isActive: message.session.is_active,
                                    createdAt: message.session.created_at,
                                },
                                model: {
                                    id: message.model.id,
                                    name: message.model.name,
                                    modelID: message.model.model_id,
                                    description: message.model.description,
                                    isActive: message.model.is_active,
                                    epId: message.model.ep_id,
                                },
                                parentMessage: message.parent_message,
                            };
                            if (!chatStore.activeSessionId || chatStore.activeSessionId !== message.session.id) {
                                chatStore.addSession(finalMessage.session);
                                chatStore.activeSessionId = finalMessage.session.id;
                            }
                            continue;
                        }
                        // 检查是否是结束消息
                        else if (data.type === "message_end" && finalMessage) {
                            // 流结束，创建最终消息
                            (finalMessage as ChatMessage) = {...finalMessage, ...chatStore.tempMessage, ...message};
                            chatStore.addMessage(finalMessage);
                            chatStore.clearTempMessage();
                            // 清除控制器引用
                            abortController = null;
                            return finalMessage;
                        }

                        const reasoningContent = data.choices[0]?.delta?.reasoning_content || "";
                        const content = data.choices[0]?.delta?.content || "";

                        // 临时消息更新
                        chatStore.updateTempMessage(content, isFirstChunk, reasoningContent);
                        if (isFirstChunk) isFirstChunk = false;

                    } catch (e) {
                        console.error("JSON 解析错误", e);
                    }
                }
            }
        }
    } catch (err) {
        // 处理中断错误
        if (err instanceof Error && err.name === "AbortError") {
            console.log("请求已被用户中断");
            ElMessage.info("请求已中断");
        } else {
            // 处理其他错误
            ElMessage.error("消息接收失败: " + (err instanceof Error ? err.message : "未知错误"));
        }
        chatStore.clearTempMessage();
        // 清除控制器引用
        abortController = null;
        throw err;
    }
};


// 聊天会话
export const getSessionList = async () => {
    const chatStore = useChatStore();
    return api.get(chatPath(`/session/`)).then(res => {
        chatStore.setSessionList(res.data);
        return res.data;
    });

};

export const updateSession = async (data: Partial<ChatSession>) => {
    const chatStore = useChatStore();
    return api.patch(chatPath(`/session/${data.id}/`), data).then(res => {
        chatStore.updateSession(res.data);
    });
};

export const deleteSession = async (id: number) => {
    const chatStore = useChatStore();
    return api.delete(chatPath(`/session/${id}/`)).then(() => {
        chatStore.deleteSession(id);
    });
};