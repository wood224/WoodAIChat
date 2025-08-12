import {defineStore} from "pinia";
import type {ChatMessage, ChatSession} from "../types/chat.ts";

interface ChatState {
    sessionList: ChatSession[];
    activeSessionId: number | undefined;
    messageList: ChatMessage[];
    tempMessage: {
        thinkingStatus: "thinking" | "end",
        reasoningContent: string;
        content: string;
    } | null;
}

export const useChatStore = defineStore("chat", {
    state: (): ChatState => ({
        sessionList: [],
        activeSessionId: undefined,
        messageList: [],
        tempMessage: null,
    }),
    actions: {
        // 会话
        setSessionList(sessionList: ChatSession[]) {
            this.sessionList = sessionList;
        },
        addSession(session: ChatSession) {
            this.sessionList.unshift(session);
        },

        updateSession(session: Partial<ChatSession>) {
            const index = this.sessionList.findIndex(item => item.id === session.id);
            if (index !== -1) {
                this.sessionList[index] = {...this.sessionList[index], ...session};
            }
        },
        deleteSession(id: number) {
            const index = this.sessionList.findIndex(item => item.id === id);
            if (index !== -1) {
                this.sessionList.splice(index, 1);
            }
        },
        updateSessionTime(id: ChatSession["id"] | undefined) {
            if (!id) return;
            const index = this.sessionList.findIndex(item => item.id === id);
            if (index !== -1) this.sessionList[index] = {
                ...this.sessionList[index],
                updatedAt: new Date().toISOString(),
            };
        },

        // 消息
        setMessageList(messageList: ChatMessage[]) {
            this.messageList = messageList;
        },

        addMessage(message: ChatMessage) {
            // 检查消息是否已存在（避免重复添加）
            const existingIndex = this.messageList.findIndex(msg => msg.id === message.id);
            if (existingIndex !== -1) {
                // 如果消息已存在，则更新它
                this.messageList[existingIndex] = message;
            } else {
                // 否则添加新消息
                this.messageList.push(message);
            }
        },

        // 更新临时消息（用于流式响应）
        updateTempMessage(content: string, isFirst: boolean, reasoning_content: string) {
            if (isFirst) {
                this.tempMessage = {
                    thinkingStatus: "thinking",
                    reasoningContent: reasoning_content,
                    content: content,
                };
            } else {
                if (this.tempMessage) {
                    if (reasoning_content) this.tempMessage.reasoningContent += reasoning_content;
                    else if (content) this.tempMessage.content += content;
                }
            }
        },

        // 清除临时消息
        clearTempMessage() {
            this.tempMessage = null;
        },
    },
    getters: {
        // 获取包括临时消息在内的完整消息列表
        allMessages: (state) => {
            if (state.tempMessage) {
                return [...state.messageList, state.tempMessage];
            }
            return [...state.messageList];
        },

        // 查找最后一个角色是 assistant 的消息
        lastAssistantMessage: (state) => {
            // 先在完整消息列表中查找
            for (let i = state.messageList.length - 1; i >= 0; i--) {
                if (state.messageList[i].role === "assistant") {
                    return state.messageList[i];
                }
            }
            // // 如果完整消息列表中没有，则检查临时消息
            // if (state.tempMessage && state.tempMessage.role === "assistant") {
            //     return state.tempMessage;
            // }
            // 如果都没有找到，返回 null
            return null;
        },
    },
});