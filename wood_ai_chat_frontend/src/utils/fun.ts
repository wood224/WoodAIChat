// 计算时间范围
export const getDateRange = (date: string) => {
    const now = new Date();
    const target = new Date(date);

    if (isNaN(target.getTime())) {
        return "时间范围错误";
    }

    // 设置为当天开始时间，避免时区和小时差异影响
    now.setHours(0, 0, 0, 0);
    target.setHours(0, 0, 0, 0);
    const diff = now.getTime() - target.getTime();

    if (diff < 0) {
        return "时间范围错误";
    }

    // 定义时间常量（毫秒）
    const ONE_DAY = 24 * 60 * 60 * 1000;
    const ONE_WEEK = 7 * ONE_DAY;
    const ONE_MONTH = 30 * ONE_DAY;

    if (diff === 0) {
        return "今天";
    } else if (diff < ONE_WEEK) {
        return "一周内";
    } else if (diff < ONE_MONTH) {
        return "一月内";
    } else {
        return "更早";
    }
};