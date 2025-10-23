<template>
  <div class="message-list">
    <div class="search-bar">
        <input
          v-model="localSearchQuery"
          type="text"
          placeholder="Search messages..."
          @input="handleSearch"
          class="search-input"
        />
      <button @click="clearSearch" class="clear-btn" v-if="localSearchQuery">
        Clear
      </button>
    </div>
    
    <div class="message-stats" v-if="filteredMessages.length > 0">
      Showing {{ filteredMessages.length }} of {{ messages.length }} messages
    </div>
    
    <div class="messages-container">
      <div v-if="filteredMessages.length === 0" class="no-messages">
        {{ searchQuery ? 'No messages match your search' : 'No messages available' }}
      </div>
      
      <div
        v-for="message in paginatedMessages"
        :key="message.id"
        class="message-item"
        :class="{ 'highlighted': message.similarity }"
        @click="selectMessage(message)"
      >
        <div class="message-header">
          <span class="sender">{{ message.sender }}</span>
          <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
          <span v-if="message.similarity" class="similarity">
            Similarity: {{ (message.similarity * 100).toFixed(1) }}%
          </span>
        </div>
        
        <div class="message-content">
          {{ message.message }}
        </div>
        
        <div class="message-meta" v-if="message.sentiment !== null || message.similarity">
          <span v-if="message.sentiment !== null" class="sentiment">
            Sentiment: {{ message.sentiment.toFixed(2) }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1"
        class="page-btn"
      >
        Previous
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessageList',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    searchQuery: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 20,
      localSearchQuery: this.searchQuery || ''
    }
  },
  computed: {
    filteredMessages() {
      if (!this.localSearchQuery.trim()) {
        return this.messages
      }
      
      const query = this.localSearchQuery.toLowerCase()
      return this.messages.filter(message => 
        message.message.toLowerCase().includes(query) ||
        message.sender.toLowerCase().includes(query)
      )
    },
    
    totalPages() {
      return Math.ceil(this.filteredMessages.length / this.itemsPerPage)
    },
    
    paginatedMessages() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredMessages.slice(start, end)
    }
  },
  watch: {
    searchQuery(newVal) {
      this.localSearchQuery = newVal || ''
      this.currentPage = 1
    },
    messages() {
      this.currentPage = 1
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', this.localSearchQuery)
    },
    
    clearSearch() {
      this.localSearchQuery = ''
      this.$emit('search', '')
    },
    
    selectMessage(message) {
      this.$emit('message-click', message)
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    },
    
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    }
  }
}
</script>

<style scoped>
.message-list {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: #075e54;
}

.clear-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.clear-btn:hover {
  background: #c82333;
}

.message-stats {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  background: white;
}

.no-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
  font-style: italic;
}

.message-item {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.message-item:hover {
  background-color: #f8f9fa;
}

.message-item.highlighted {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.sender {
  font-weight: 600;
  color: #075e54;
}

.timestamp {
  font-size: 0.8rem;
  color: #666;
}

.similarity {
  font-size: 0.8rem;
  color: #28a745;
  font-weight: 500;
}

.message-content {
  color: #333;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.message-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #666;
}

.sentiment {
  color: #6c757d;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
}

.page-btn {
  background: #075e54;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.page-btn:hover:not(:disabled) {
  background: #064e46;
}

.page-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}
</style>
