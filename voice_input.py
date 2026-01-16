"""
ui/voice_input.py

Voice input component for hands-free querying.
Uses browser's native Web Speech API (free, no external API needed).
"""

import streamlit as st


def render_voice_button_inline():
    """
    Render floating voice input button.
    Uses HTML/JS for browser-native speech recognition.
    Works in Chrome, Edge (not Firefox/Safari).
    """
    st.markdown("""
    <style>
    .voice-btn {
        position: fixed;
        bottom: 100px;
        right: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        cursor: pointer;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        transition: all 0.3s ease;
    }
    .voice-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .voice-btn.recording {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }
        50% { 
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(245,87,108,0.6);
        }
    }
    .voice-status {
        position: fixed;
        bottom: 170px;
        right: 30px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        z-index: 999;
        display: none;
    }
    .voice-status.show {
        display: block;
        animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    
    <div id="voiceStatus" class="voice-status">Listening...</div>
    <button id="voiceBtn" class="voice-btn" onclick="toggleVoiceInput()" title="Voice Input (Click to speak)">
        🎤
    </button>
    
    <script>
    let recognition;
    let isRecording = false;
    
    function toggleVoiceInput() {
        const btn = document.getElementById('voiceBtn');
        const status = document.getElementById('voiceStatus');
        
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('🚫 Voice input not supported in this browser.\\n\\nPlease use Chrome or Edge for voice features.');
            return;
        }
        
        if (isRecording) {
            // Stop recording
            recognition.stop();
            btn.classList.remove('recording');
            btn.innerHTML = '🎤';
            status.classList.remove('show');
            isRecording = false;
            return;
        }
        
        // Start recording
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isRecording = true;
            btn.classList.add('recording');
            btn.innerHTML = '⏹️';
            status.classList.add('show');
            status.textContent = 'Listening...';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            
            // Insert into Streamlit chat input
            const chatInput = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = transcript;
                // Trigger input event to update Streamlit
                const inputEvent = new Event('input', { bubbles: true });
                chatInput.dispatchEvent(inputEvent);
                chatInput.focus();
                
                status.textContent = '✅ "' + transcript + '"';
                setTimeout(() => {
                    status.classList.remove('show');
                }, 2000);
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            let errorMsg = 'Error: ';
            switch(event.error) {
                case 'no-speech':
                    errorMsg += 'No speech detected';
                    break;
                case 'audio-capture':
                    errorMsg += 'No microphone found';
                    break;
                case 'not-allowed':
                    errorMsg += 'Microphone permission denied';
                    break;
                default:
                    errorMsg += event.error;
            }
            status.textContent = errorMsg;
            status.classList.add('show');
            setTimeout(() => {
                status.classList.remove('show');
            }, 3000);
            
            btn.classList.remove('recording');
            btn.innerHTML = '🎤';
            isRecording = false;
        };
        
        recognition.onend = function() {
            btn.classList.remove('recording');
            btn.innerHTML = '🎤';
            isRecording = false;
        };
        
        recognition.start();
    }
    
    // Keyboard shortcut: Ctrl+Shift+V
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            toggleVoiceInput();
        }
    });
    </script>
    """, unsafe_allow_html=True)


def show_voice_tutorial():
    """Show quick tutorial for voice feature."""
    st.info("""
    🎤 **Voice Input Tutorial**
    
    1. Click the floating microphone button (bottom-right)
    2. Speak your question clearly
    3. Your speech will appear in the chat input
    4. Press Enter to send
    
    **Keyboard Shortcut:** Ctrl+Shift+V
    
    **Supported Browsers:** Chrome, Edge (not Firefox/Safari)
    """)