// 自定义JavaScript功能

// 切换配置状态
function toggleConfig(type, configId) {
    fetch(`/api/${type}/toggle/${configId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('操作失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失败，请重试');
    });
}

// 确认删除
function confirmDelete(message) {
    return confirm(message || '确定要删除这个配置吗？');
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // 显示成功提示
        showToast('已复制到剪贴板', 'success');
    }, function(err) {
        console.error('复制失败: ', err);
        showToast('复制失败', 'error');
    });
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // 自动移除
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// 创建提示消息容器
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// 格式化时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 截断文本
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 图片点击放大功能
function initImageModal() {
    // 为所有消息内容中的图片添加点击事件
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'IMG' && 
            (e.target.closest('.message-content') || e.target.closest('.message-content-full'))) {
            e.preventDefault();
            
            const imgSrc = e.target.src;
            const modalImage = document.getElementById('modalImage');
            const imageModal = new bootstrap.Modal(document.getElementById('imageModal'));
            
            if (modalImage && imgSrc) {
                modalImage.src = imgSrc;
                modalImage.alt = e.target.alt || '放大图片';
                imageModal.show();
            }
        }
    });
    
    // 模态框关闭时清空图片源
    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.addEventListener('hidden.bs.modal', function() {
            const modalImage = document.getElementById('modalImage');
            if (modalImage) {
                modalImage.src = '';
            }
        });
    }
}

// 页面加载完成后初始化图片模态框
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有提示工具
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 自动隐藏警告消息
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // 初始化图片放大功能
    initImageModal();
});

// 实时更新时间显示
function updateTimeDisplays() {
    const timeElements = document.querySelectorAll('[data-time]');
    timeElements.forEach(function(element) {
        const timestamp = element.getAttribute('data-time');
        element.textContent = formatDateTime(timestamp);
    });
}

// 每分钟更新一次时间显示
setInterval(updateTimeDisplays, 60000);