<template>
  <div class="dashboard">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading chat data...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <h3>Error</h3>
      <p>{{ error }}</p>
      <router-link to="/" class="back-btn">← Back to Upload</router-link>
    </div>
    
    <div v-else class="dashboard-content">
      <div class="dashboard-header">
        <h2>{{ chatName }}</h2>
        <div class="chat-stats">
          <span class="stat">{{ stats.total_messages }} messages</span>
          <span class="stat">{{ stats.sender_stats.length }} participants</span>
        </div>
      </div>
      
      <div class="dashboard-grid">
        <!-- Timeline Chart -->
        <div class="chart-card">
          <h3>Message Timeline</h3>
          <TimelineChart :messages="messages" />
        </div>
        
        <!-- Sentiment Chart -->
        <div class="chart-card">
          <h3>Sentiment Trends</h3>
          <SentimentChart :messages="messages" />
        </div>
        
        <!-- Cluster Visualization -->
        <div class="chart-card cluster-card">
          <h3>Message Clusters</h3>
          <ClusterView :clusters="clusters" @message-click="showMessage" />
        </div>
        
        <!-- Message List -->
        <div class="chart-card">
          <h3>Messages</h3>
          <MessageList 
            :messages="messages" 
            :search-query="searchQuery"
            @search="handleSearch"
          />
        </div>
      </div>
      
      <!-- Message Detail Modal -->
      <div v-if="selectedMessage" class="modal-overlay" @click="closeModal">
        <div class="modal" @click.stop>
          <h3>Message Details</h3>
          <div class="message-detail">
            <p><strong>Sender:</strong> {{ selectedMessage.sender }}</p>
            <p><strong>Time:</strong> {{ formatDateTime(selectedMessage.timestamp) }}</p>
            <p><strong>Message:</strong></p>
            <div class="message-text">{{ selectedMessage.message }}</div>
            <p v-if="selectedMessage.sentiment !== null">
              <strong>Sentiment:</strong> {{ selectedMessage.sentiment.toFixed(2) }}
            </p>
          </div>
          <button @click="closeModal" class="close-btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { chatAPI } from '../services/api'
import TimelineChart from './TimelineChart.vue'
import SentimentChart from './SentimentChart.vue'
import ClusterView from './ClusterView.vue'
import MessageList from './MessageList.vue'

export default {
  name: 'ChatDashboard',
  components: {
    TimelineChart,
    SentimentChart,
    ClusterView,
    MessageList
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      chatName: '',
      messages: [],
      stats: {},
      clusters: [],
      searchQuery: '',
      selectedMessage: null
    }
  },
  async mounted() {
    await this.loadChatData()
  },
  methods: {
    async loadChatData() {
      try {
        this.loading = true
        
        // Load messages and stats in parallel
        const [messages, stats, clusters] = await Promise.all([
          chatAPI.getMessages(this.id),
          chatAPI.getChatStats(this.id),
          chatAPI.getClusters(this.id)
        ])
        
        this.messages = messages
        this.stats = stats
        this.clusters = clusters
        this.chatName = `Chat ${this.id}`
        
        // If no clusters, try to process the chat
        if (clusters.length === 0) {
          try {
            await chatAPI.processChat(this.id)
            this.clusters = await chatAPI.getClusters(this.id)
          } catch (error) {
            console.warn('Failed to process chat for clusters:', error)
          }
        }
        
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to load chat data'
      } finally {
        this.loading = false
      }
    },
    
    async handleSearch(query) {
      this.searchQuery = query
      if (query.trim()) {
        try {
          const results = await chatAPI.searchMessages(this.id, query)
          // Update messages with search results
          this.messages = results
        } catch (error) {
          console.error('Search failed:', error)
        }
      } else {
        // Reload all messages
        await this.loadChatData()
      }
    },
    
    showMessage(message) {
      this.selectedMessage = message
    },
    
    closeModal() {
      this.selectedMessage = null
    },
    
    formatDateTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #075e54;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error h3 {
  color: #c33;
  margin-bottom: 1rem;
}

.back-btn {
  display: inline-block;
  background: #075e54;
  color: white;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 4px;
  margin-top: 1rem;
}

.dashboard-header {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h2 {
  color: #075e54;
  margin: 0;
}

.chat-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  background: #f0f8f7;
  color: #075e54;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-card h3 {
  color: #075e54;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.cluster-card {
  grid-column: 1 / -1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  color: #075e54;
  margin-bottom: 1rem;
}

.message-detail p {
  margin-bottom: 0.5rem;
}

.message-text {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  margin: 0.5rem 0;
  white-space: pre-wrap;
}

.close-btn {
  background: #075e54;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.close-btn:hover {
  background: #064e46;
}
</style>



