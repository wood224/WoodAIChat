// 聊天消息角色枚举
export type ChatMessageRole = "user" | "assistant" | "system";

// 聊天模型
export interface ChatModel {
    id: number;
    name: string;
    modelID: string;
    description: string;
    isActive: boolean;
    epId: string | null;
}

// 聊天会话
export interface ChatSession {
    id: number;
    title: string;
    user: number; // 用户ID
    createdAt: string;
    updatedAt: string;
    isActive: boolean;
}

// 聊天消息
export interface ChatMessage {
    id: number;
    session: ChatSession;
    role: ChatMessageRole;
    reasoningContent: string | null;
    content: string;
    model: ChatModel | null;
    createdAt: string;
    tokens: number;
    parentMessage: ChatMessage | null;
    messageRespId: string | null;
}

// 聊天设置
export interface ChatSettings {
    id: number;
    user: number; // 用户ID
    defaultModel: ChatModel | null;
    temperature: number;
    maxTokens: number;
    createdAt: string;
    updatedAt: string;
}

// 创建聊天消息请求参数
export interface CreateChatMessageRequest {
    content: string;
    sessionId: number | undefined;
    parentMessageId: number | null;
    modelId: string;
    thinkType?: number;
}

// 聊天会话列表响应数据
export interface ChatSessionListResponse extends StandardResponse<ChatSession[]> {
}

// 聊天消息列表响应数据
export interface ChatMessageListResponse extends StandardResponse<ChatMessage[]> {
}

// 聊天消息响应数据
export interface ChatMessageResponse extends StandardResponse<ChatMessage> {
}

// 聊天模型列表响应数据
export interface ChatModelListResponse extends StandardResponse<ChatModel[]> {
}

// 聊天设置响应数据
export interface ChatSettingsResponse extends StandardResponse<ChatSettings> {
}

// 标准响应格式
export interface StandardResponse<T = any> {
    data: T;
    message: string;
    timestamp: string;
    status: number;

    [key: string]: any; // 用于额外的响应字段
}
