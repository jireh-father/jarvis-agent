/**
 * Jarvis 채팅 UI 로직
 */

// DOM 요소
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// 메시지 전송 함수
async function sendMessage() {
    const message = messageInput.value.trim();
    
    // 빈 메시지 체크
    if (!message) {
        return;
    }
    
    // 버튼 비활성화
    sendButton.disabled = true;
    
    // 사용자 메시지 추가
    addUserMessage(message);
    
    // 입력창 초기화
    messageInput.value = '';
    
    // 로딩 메시지 추가
    const loadingMessageElement = addAgentMessage('응답을 생성하는 중입니다...');
    loadingMessageElement.querySelector('.message-text').classList.add('loading');
    
    try {
        // API 호출
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 로딩 메시지 제거
        loadingMessageElement.remove();
        
        // 에이전트 응답 추가
        addAgentMessage(data.response);
        
    } catch (error) {
        console.error('Error:', error);
        
        // 로딩 메시지 제거
        loadingMessageElement.remove();
        
        // 에러 메시지 추가
        addAgentMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해 주세요.');
    } finally {
        // 버튼 활성화
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// 사용자 메시지 추가
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            <div class="message-label">사용자</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// 에이전트 메시지 추가
function addAgentMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            <div class="message-label">JARVIS</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 스크롤을 맨 아래로
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 이벤트 리스너
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 초기 포커스
messageInput.focus();

