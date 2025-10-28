<template>
  <div class="upload-container">
    <div class="upload-card">
      <h2>Upload WhatsApp Chat</h2>
      <p class="upload-description">
        Upload a WhatsApp chat export file (.txt) to analyze and visualize your conversations.
      </p>
      
      <div 
        class="upload-area"
        :class="{ 'drag-over': isDragOver, 'uploading': isUploading }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <div v-if="!isUploading" class="upload-content">
          <div class="upload-icon">📁</div>
          <p class="upload-text">
            {{ isDragOver ? 'Drop your file here' : 'Click to upload or drag and drop' }}
          </p>
          <p class="upload-hint">WhatsApp .txt files only</p>
        </div>
        
        <div v-else class="upload-progress">
          <div class="spinner"></div>
          <p>Processing your chat...</p>
        </div>
      </div>
      
      <input 
        ref="fileInput"
        type="file"
        accept=".txt"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="success" class="success-message">
        <p>✅ Chat uploaded successfully!</p>
        <p>{{ success.message_count }} messages processed</p>
        <router-link :to="`/chat/${success.chat_id}`" class="view-chat-btn">
          View Chat Analysis
        </router-link>
      </div>
    </div>
    
    <div v-if="recentChats.length > 0" class="recent-chats">
      <h3>Recent Chats</h3>
      <div class="chat-list">
        <div 
          v-for="chat in recentChats" 
          :key="chat.id"
          class="chat-item"
          @click="viewChat(chat.id)"
        >
          <div class="chat-info">
            <h4>{{ chat.name }}</h4>
            <p>{{ chat.message_count }} messages</p>
            <p class="chat-date">{{ formatDate(chat.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { chatAPI } from '../services/api'

export default {
  name: 'ChatUpload',
  data() {
    return {
      isDragOver: false,
      isUploading: false,
      error: null,
      success: null,
      recentChats: []
    }
  },
  async mounted() {
    await this.loadRecentChats()
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    handleDragOver(e) {
      this.isDragOver = true
    },
    
    handleDragLeave(e) {
      this.isDragOver = false
    },
    
    handleDrop(e) {
      this.isDragOver = false
      const files = e.dataTransfer.files
      if (files.length > 0) {
        this.uploadFile(files[0])
      }
    },
    
    handleFileSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.uploadFile(file)
      }
    },
    
    async uploadFile(file) {
      if (!file.name.endsWith('.txt')) {
        this.error = 'Please select a .txt file'
        return
      }
      
      this.isUploading = true
      this.error = null
      this.success = null
      
      try {
        const result = await chatAPI.uploadChat(file)
        this.success = result
        await this.loadRecentChats()
      } catch (error) {
        this.error = error.response?.data?.error || 'Upload failed'
      } finally {
        this.isUploading = false
      }
    },
    
    async loadRecentChats() {
      try {
        this.recentChats = await chatAPI.getChats()
      } catch (error) {
        console.error('Failed to load recent chats:', error)
      }
    },
    
    viewChat(chatId) {
      this.$router.push(`/chat/${chatId}`)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.upload-card h2 {
  color: #075e54;
  margin-bottom: 0.5rem;
}

.upload-description {
  color: #666;
  margin-bottom: 2rem;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #075e54;
  background: #f0f8f7;
}

.upload-area.uploading {
  border-color: #075e54;
  background: #f0f8f7;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  font-size: 3rem;
}

.upload-text {
  font-size: 1.1rem;
  color: #333;
  margin: 0;
}

.upload-hint {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.upload-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #075e54;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.success-message {
  background: #efe;
  color: #363;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  text-align: center;
}

.view-chat-btn {
  display: inline-block;
  background: #075e54;
  color: white;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 4px;
  margin-top: 1rem;
  transition: background-color 0.2s;
}

.view-chat-btn:hover {
  background: #064e46;
}

.recent-chats {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.recent-chats h3 {
  color: #075e54;
  margin-bottom: 1rem;
}

.chat-list {
  display: grid;
  gap: 1rem;
}

.chat-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-item:hover {
  border-color: #075e54;
  background: #f0f8f7;
}

.chat-info h4 {
  color: #333;
  margin-bottom: 0.5rem;
}

.chat-info p {
  color: #666;
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.chat-date {
  font-size: 0.8rem !important;
  color: #999 !important;
}
</style>



