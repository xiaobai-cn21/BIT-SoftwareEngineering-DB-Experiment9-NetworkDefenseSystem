// 更新时间函数
function updateTime() {
    const now = new Date();
    const timeElement = document.getElementById('currentTime');
    
    // 格式化时间为：YYYY年MM月DD日 HH:MM:SS 星期X
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
    const weekday = weekdays[now.getDay()];
    
    timeElement.textContent = `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds} 星期${weekday}`;
}

// 初始调用
updateTime();

// 每秒更新一次时间
setInterval(updateTime, 1000);