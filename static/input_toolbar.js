/**
 * Input Toolbar - File/Image/Video/Audio/Voice/Camera Upload
 * Replit-style multi-modal input
 */

class InputToolbar {
  constructor() {
    this.attachments = [];
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
  }

  /**
   * Initialize toolbar
   */
  init() {
    this.createToolbar();
    this.setupDragAndDrop();
  }

  /**
   * Create toolbar HTML
   */
  createToolbar() {
    const toolbar = document.getElementById('inputToolbar');
    if (!toolbar) return;

    toolbar.innerHTML = `
      <div class="toolbar-buttons">
        <button class="toolbar-btn" onclick="inputToolbar.attachFile()" title="Attach File">
          <span class="btn-icon">📎</span>
          <span class="btn-label">File</span>
        </button>
        
        <button class="toolbar-btn" onclick="inputToolbar.attachImage()" title="Add Image">
          <span class="btn-icon">🖼️</span>
          <span class="btn-label">Image</span>
        </button>
        
        <button class="toolbar-btn" id="voiceBtn" onclick="inputToolbar.toggleVoiceInput()" title="Voice Input">
          <span class="btn-icon">🎤</span>
          <span class="btn-label">Voice</span>
        </button>
        
        <button class="toolbar-btn" onclick="inputToolbar.attachVideo()" title="Upload Video">
          <span class="btn-icon">📹</span>
          <span class="btn-label">Video</span>
        </button>
        
        <button class="toolbar-btn" onclick="inputToolbar.openCamera()" title="Take Photo">
          <span class="btn-icon">📷</span>
          <span class="btn-label">Camera</span>
        </button>
      </div>
      
      <div class="attachments-preview" id="attachmentsPreview"></div>
    `;
  }

  /**
   * File Upload
   */
  attachFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.txt,.md,.pdf,.doc,.docx,.json,.csv,.xlsx,.py,.js,.html,.css';
    input.onchange = (e) => this.handleFiles(Array.from(e.target.files));
    input.click();
  }

  /**
   * Image Upload
   */
  attachImage() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*';
    input.onchange = (e) => this.handleImages(Array.from(e.target.files));
    input.click();
  }

  /**
   * Video Upload
   */
  attachVideo() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = (e) => this.handleVideo(e.target.files[0]);
    input.click();
  }

  /**
   * Handle file uploads
   */
  async handleFiles(files) {
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/api/v1/upload-file', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (data.success) {
          this.attachments.push({
            type: 'file',
            id: data.file_id,
            name: data.filename,
            size: data.size_human,
            content: data.content_preview,
            data: data
          });
          
          this.renderAttachments();
          this.showNotification(`✅ ${file.name} uploaded`);
        }
      } catch (error) {
        console.error('File upload error:', error);
        this.showNotification(`❌ Failed to upload ${file.name}`, 'error');
      }
    }
  }

  /**
   * Handle image uploads
   */
  async handleImages(files) {
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/api/v1/upload-image', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (data.success) {
          // Create preview URL
          const previewUrl = URL.createObjectURL(file);
          
          this.attachments.push({
            type: 'image',
            id: data.image_id,
            name: data.filename,
            size: data.size_human,
            url: data.url,
            previewUrl: previewUrl,
            dimensions: data.dimensions,
            data: data
          });
          
          this.renderAttachments();
          this.showNotification(`✅ ${file.name} uploaded`);
        }
      } catch (error) {
        console.error('Image upload error:', error);
        this.showNotification(`❌ Failed to upload ${file.name}`, 'error');
      }
    }
  }

  /**
   * Handle video upload
   */
  async handleVideo(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/v1/upload-video', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        const previewUrl = URL.createObjectURL(file);
        
        this.attachments.push({
          type: 'video',
          id: data.video_id,
          name: data.filename,
          size: data.size_human,
          url: data.url,
          previewUrl: previewUrl,
          data: data
        });
        
        this.renderAttachments();
        this.showNotification(`✅ ${file.name} uploaded`);
      }
    } catch (error) {
      console.error('Video upload error:', error);
      this.showNotification(`❌ Failed to upload ${file.name}`, 'error');
    }
  }

  /**
   * Voice Input - Toggle recording
   */
  toggleVoiceInput() {
    if (this.isRecording) {
      this.stopVoiceInput();
    } else {
      this.startVoiceInput();
    }
  }

  /**
   * Start voice input
   */
  async startVoiceInput() {
    try {
      // Try Web Speech API first (Chrome/Edge)
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        this.startWebSpeechRecognition();
      } else {
        // Fallback to audio recording
        this.startAudioRecording();
      }
    } catch (error) {
      console.error('Voice input error:', error);
      this.showNotification('❌ Voice input not available', 'error');
    }
  }

  /**
   * Web Speech Recognition (Chrome/Edge)
   */
  startWebSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      this.isRecording = true;
      this.updateVoiceButton(true);
      this.showNotification('🎤 Listening...', 'info');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      this.appendToInput(transcript);
      this.showNotification(`✅ Transcribed: "${transcript}"`);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.showNotification('❌ Voice input failed', 'error');
      this.isRecording = false;
      this.updateVoiceButton(false);
    };

    recognition.onend = () => {
      this.isRecording = false;
      this.updateVoiceButton(false);
    };

    recognition.start();
  }

  /**
   * Audio Recording (fallback)
   */
  async startAudioRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        await this.uploadAudioForTranscription(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      this.mediaRecorder.start();
      this.isRecording = true;
      this.updateVoiceButton(true);
      this.showNotification('🎤 Recording...', 'info');
      
    } catch (error) {
      console.error('Audio recording error:', error);
      this.showNotification('❌ Microphone access denied', 'error');
    }
  }

  /**
   * Stop voice input
   */
  stopVoiceInput() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    this.isRecording = false;
    this.updateVoiceButton(false);
  }

  /**
   * Upload audio for transcription
   */
  async uploadAudioForTranscription(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');

    try {
      const response = await fetch('/api/v1/upload-audio', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success && data.transcript) {
        this.appendToInput(data.transcript);
        this.showNotification(`✅ Transcribed: "${data.transcript}"`);
      }
    } catch (error) {
      console.error('Transcription error:', error);
      this.showNotification('❌ Transcription failed', 'error');
    }
  }

  /**
   * Camera Capture
   */
  async openCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.showCameraModal(stream);
    } catch (error) {
      console.error('Camera error:', error);
      this.showNotification('❌ Camera access denied', 'error');
    }
  }

  /**
   * Show camera modal
   */
  showCameraModal(stream) {
    const modal = document.createElement('div');
    modal.className = 'camera-modal';
    modal.innerHTML = `
      <div class="camera-container">
        <h3>📷 Take Photo</h3>
        <video id="cameraVideo" autoplay></video>
        <canvas id="cameraCanvas" style="display:none;"></canvas>
        <div class="camera-actions">
          <button class="btn-secondary" onclick="inputToolbar.closeCamera()">Cancel</button>
          <button class="btn-primary" onclick="inputToolbar.capturePhoto()">📸 Capture</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    const video = document.getElementById('cameraVideo');
    video.srcObject = stream;
    
    this.cameraStream = stream;
  }

  /**
   * Capture photo from camera
   */
  async capturePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    canvas.toBlob(async (blob) => {
      const file = new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' });
      await this.handleImages([file]);
      this.closeCamera();
    }, 'image/jpeg');
  }

  /**
   * Close camera
   */
  closeCamera() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => track.stop());
    }
    
    const modal = document.querySelector('.camera-modal');
    if (modal) {
      modal.remove();
    }
  }

  /**
   * Drag and Drop Support
   */
  setupDragAndDrop() {
    const inputArea = document.getElementById('userInput');
    if (!inputArea) return;

    inputArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      inputArea.classList.add('drag-over');
    });

    inputArea.addEventListener('dragleave', () => {
      inputArea.classList.remove('drag-over');
    });

    inputArea.addEventListener('drop', async (e) => {
      e.preventDefault();
      inputArea.classList.remove('drag-over');
      
      const files = Array.from(e.dataTransfer.files);
      
      // Separate by type
      const images = files.filter(f => f.type.startsWith('image/'));
      const videos = files.filter(f => f.type.startsWith('video/'));
      const others = files.filter(f => !f.type.startsWith('image/') && !f.type.startsWith('video/'));
      
      if (images.length > 0) await this.handleImages(images);
      if (videos.length > 0) await this.handleVideo(videos[0]);
      if (others.length > 0) await this.handleFiles(others);
    });
  }

  /**
   * Render attachments preview
   */
  renderAttachments() {
    const preview = document.getElementById('attachmentsPreview');
    if (!preview) return;

    if (this.attachments.length === 0) {
      preview.innerHTML = '';
      return;
    }

    preview.innerHTML = this.attachments.map((att, index) => {
      if (att.type === 'image') {
        return `
          <div class="attachment-item">
            <img src="${att.previewUrl}" alt="${att.name}" class="attachment-thumbnail">
            <div class="attachment-info">
              <div class="attachment-name">${att.name}</div>
              <div class="attachment-size">${att.size}</div>
            </div>
            <button class="attachment-remove" onclick="inputToolbar.removeAttachment(${index})">×</button>
          </div>
        `;
      } else if (att.type === 'video') {
        return `
          <div class="attachment-item">
            <video src="${att.previewUrl}" class="attachment-thumbnail" controls></video>
            <div class="attachment-info">
              <div class="attachment-name">${att.name}</div>
              <div class="attachment-size">${att.size}</div>
            </div>
            <button class="attachment-remove" onclick="inputToolbar.removeAttachment(${index})">×</button>
          </div>
        `;
      } else {
        return `
          <div class="attachment-item">
            <div class="attachment-icon">📎</div>
            <div class="attachment-info">
              <div class="attachment-name">${att.name}</div>
              <div class="attachment-size">${att.size}</div>
            </div>
            <button class="attachment-remove" onclick="inputToolbar.removeAttachment(${index})">×</button>
          </div>
        `;
      }
    }).join('');
  }

  /**
   * Remove attachment
   */
  removeAttachment(index) {
    this.attachments.splice(index, 1);
    this.renderAttachments();
  }

  /**
   * Get all attachments
   */
  getAttachments() {
    return this.attachments;
  }

  /**
   * Clear all attachments
   */
  clearAttachments() {
    this.attachments = [];
    this.renderAttachments();
  }

  /**
   * Append text to input
   */
  appendToInput(text) {
    const input = document.getElementById('userInput');
    if (input) {
      const currentValue = input.value;
      input.value = currentValue ? `${currentValue} ${text}` : text;
    }
  }

  /**
   * Update voice button state
   */
  updateVoiceButton(isRecording) {
    const btn = document.getElementById('voiceBtn');
    if (btn) {
      if (isRecording) {
        btn.classList.add('recording');
        btn.querySelector('.btn-icon').textContent = '⏹️';
        btn.querySelector('.btn-label').textContent = 'Stop';
      } else {
        btn.classList.remove('recording');
        btn.querySelector('.btn-icon').textContent = '🎤';
        btn.querySelector('.btn-label').textContent = 'Voice';
      }
    }
  }

  /**
   * Show notification
   */
  showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Initialize toolbar
const inputToolbar = new InputToolbar();
document.addEventListener('DOMContentLoaded', () => {
  inputToolbar.init();
});
