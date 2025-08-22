document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const loadingIndicator = document.getElementById('loading-indicator');
    const uploadBtn = document.getElementById('upload-btn');
    const fileUpload = document.getElementById('file-upload');
    const micBtn = document.getElementById('mic-btn');

    let sessionId = localStorage.getItem('victus_session_id');
    let isNewSession = false; // <-- New flag to track a new session

    if (!sessionId) {
        sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('victus_session_id', sessionId);
        isNewSession = true; // <-- Set the flag to true only when a new ID is created
    }

    // --- Voice Recording Logic ---
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    micBtn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    async function startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('Your browser does not support audio recording.');
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.onstop = sendAudioForTranscription;
            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Could not access microphone. Please grant permission.');
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            isRecording = false;
            micBtn.classList.remove('recording');
        }
    }
    
    async function sendAudioForTranscription() {
        if (audioChunks.length === 0) return;
        
        loadingIndicator.style.display = 'flex';
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];

        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        
        try {
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Transcription failed');
            const data = await response.json();
            messageInput.value = data.transcription;
            chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
        } catch (error) {
            console.error('Error during transcription:', error);
            addMessageToChat('Error transcribing audio.', 'ai');
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    });

    // --- Chat Logic ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        addMessageToChat(message, 'user');
        messageInput.value = '';
        messageInput.style.height = '50px';
        loadingIndicator.style.display = 'flex';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: sessionId })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An error occurred');
            }

            const data = await response.json();
            addMessageToChat(data.response, 'ai');

        } catch (error) {
            console.error('Error sending message:', error);
            addMessageToChat(`Error: ${error.message}`, 'ai');
        } finally {
            loadingIndicator.style.display = 'none';
        }
    });

    function addMessageToChat(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);

        const icon = document.createElement('div');
        icon.classList.add('icon');
        icon.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.classList.add('message-content');
        
        const textSpan = document.createElement('span');
        textSpan.classList.add('message-text');
        textSpan.textContent = message;
        content.appendChild(textSpan);

        if (sender === 'ai') {
            const speakerBtn = document.createElement('button');
            speakerBtn.classList.add('speaker-btn');
            speakerBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            speakerBtn.onclick = () => speakText(message);
            content.appendChild(speakerBtn);
        }

        messageElement.appendChild(icon);
        messageElement.appendChild(content);

        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function speakText(text) {
        try {
            loadingIndicator.style.display = 'flex';
            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!response.ok) throw new Error('Speech synthesis failed');
            
            const data = await response.json();
            const audio = new Audio(data.audio_url);
            audio.play();
        } catch (error) {
            console.error('Error in TTS:', error);
            alert('Could not play audio.');
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // --- File Upload Logic ---
    uploadBtn.addEventListener('click', () => fileUpload.click());

    fileUpload.addEventListener('change', async () => {
        const file = fileUpload.files[0];
        if (!file) return;

        loadingIndicator.style.display = 'flex';
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                addMessageToChat(`Successfully uploaded and indexed "${file.name}". You can now ask questions about it.`, 'ai');
            } else {
                throw new Error(data.detail || 'Upload failed');
            }

        } catch (error) {
            console.error('Error uploading file:', error);
            addMessageToChat(`Error: ${error.message}`, 'ai');
        } finally {
            loadingIndicator.style.display = 'none';
            fileUpload.value = '';
        }
    });

    // --- Auto-resize textarea Logic ---
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = `${messageInput.scrollHeight}px`;
    });

    // ==============================================================================
    // === CORRECTED FEATURE: Add a welcome message on new sessions ===
    // ==============================================================================
    // Check the flag we set during session ID creation.
    if (isNewSession) {
        addMessageToChat("Hello! I'm VICTUS, your personal AI assistant. How can I help you today?", 'ai');
    }
});
