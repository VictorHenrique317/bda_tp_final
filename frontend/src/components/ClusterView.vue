<template>
  <div class="cluster-view">
    <div v-if="!clusters || clusters.length === 0" class="no-data">
      No cluster data available. Processing may be in progress...
    </div>
    <div v-else class="cluster-container">
      <div class="cluster-controls">
        <label>
          Color by:
          <select v-model="colorBy" @change="updateColors">
            <option value="sender">Sender</option>
            <option value="sentiment">Sentiment</option>
            <option value="cluster">Cluster</option>
          </select>
        </label>
        <button @click="resetZoom" class="reset-btn">Reset Zoom</button>
      </div>
      <svg ref="svg" class="cluster-svg" @mousedown="startPan" @mousemove="pan" @mouseup="endPan">
        <g ref="zoomGroup">
          <circle
            v-for="(point, index) in clusters"
            :key="index"
            :cx="point.x"
            :cy="point.y"
            :r="4"
            :fill="getPointColor(point)"
            :stroke="getPointStroke(point)"
            :stroke-width="1"
            class="cluster-point"
            @click="selectPoint(point)"
            @mouseenter="showTooltip(point, $event)"
            @mouseleave="hideTooltip"
          />
        </g>
      </svg>
      <div v-if="selectedPoint" class="selected-info">
        <h4>Selected Message</h4>
        <p><strong>Sender:</strong> {{ selectedPoint.sender }}</p>
        <p><strong>Message:</strong> {{ selectedPoint.message.substring(0, 100) }}{{ selectedPoint.message.length > 100 ? '...' : '' }}</p>
        <p v-if="selectedPoint.sentiment !== null">
          <strong>Sentiment:</strong> {{ selectedPoint.sentiment.toFixed(2) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ClusterView',
  props: {
    clusters: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      colorBy: 'sender',
      selectedPoint: null,
      isPanning: false,
      panStart: { x: 0, y: 0 },
      transform: { x: 0, y: 0, scale: 1 },
      senderColors: {},
      tooltip: null
    }
  },
  mounted() {
    this.initializeColors()
    this.setupSVG()
  },
  methods: {
    initializeColors() {
      const senders = [...new Set(this.clusters.map(c => c.sender))]
      const colors = [
        '#075e54', '#128c7e', '#25d366', '#dcf8c6', '#34b7f1',
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'
      ]
      
      senders.forEach((sender, index) => {
        this.senderColors[sender] = colors[index % colors.length]
      })
    },
    
    setupSVG() {
      if (this.$refs.svg) {
        const svg = this.$refs.svg
        const rect = svg.getBoundingClientRect()
        svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`)
      }
    },
    
    getPointColor(point) {
      switch (this.colorBy) {
        case 'sender':
          return this.senderColors[point.sender] || '#666'
        case 'sentiment':
          if (point.sentiment === null) return '#999'
          const intensity = Math.abs(point.sentiment)
          const hue = point.sentiment > 0 ? 120 : 0 // Green for positive, red for negative
          return `hsl(${hue}, 70%, ${50 + intensity * 30}%)`
        case 'cluster':
          const clusterColors = ['#075e54', '#128c7e', '#25d366', '#34b7f1', '#ff6b6b']
          return clusterColors[point.cluster % clusterColors.length] || '#666'
        default:
          return '#666'
      }
    },
    
    getPointStroke(point) {
      return this.selectedPoint === point ? '#000' : 'none'
    },
    
    selectPoint(point) {
      this.selectedPoint = point
      this.$emit('message-click', point)
    },
    
    showTooltip(point, event) {
      // Simple tooltip implementation
      if (!this.tooltip) {
        this.tooltip = document.createElement('div')
        this.tooltip.className = 'cluster-tooltip'
        document.body.appendChild(this.tooltip)
      }
      
      this.tooltip.innerHTML = `
        <strong>${point.sender}</strong><br>
        ${point.message.substring(0, 50)}${point.message.length > 50 ? '...' : ''}
      `
      this.tooltip.style.display = 'block'
      this.tooltip.style.left = event.pageX + 10 + 'px'
      this.tooltip.style.top = event.pageY - 10 + 'px'
    },
    
    hideTooltip() {
      if (this.tooltip) {
        this.tooltip.style.display = 'none'
      }
    },
    
    updateColors() {
      // Colors will be updated automatically through getPointColor
    },
    
    startPan(event) {
      this.isPanning = true
      this.panStart = { x: event.clientX, y: event.clientY }
    },
    
    pan(event) {
      if (!this.isPanning) return
      
      const dx = event.clientX - this.panStart.x
      const dy = event.clientY - this.panStart.y
      
      this.transform.x += dx
      this.transform.y += dy
      
      this.updateTransform()
      this.panStart = { x: event.clientX, y: event.clientY }
    },
    
    endPan() {
      this.isPanning = false
    },
    
    resetZoom() {
      this.transform = { x: 0, y: 0, scale: 1 }
      this.updateTransform()
    },
    
    updateTransform() {
      if (this.$refs.zoomGroup) {
        this.$refs.zoomGroup.style.transform = 
          `translate(${this.transform.x}px, ${this.transform.y}px) scale(${this.transform.scale})`
      }
    }
  },
  beforeUnmount() {
    if (this.tooltip) {
      document.body.removeChild(this.tooltip)
    }
  }
}
</script>

<style scoped>
.cluster-view {
  height: 400px;
  position: relative;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-style: italic;
}

.cluster-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.cluster-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.cluster-controls label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.cluster-controls select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.reset-btn {
  background: #075e54;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.reset-btn:hover {
  background: #064e46;
}

.cluster-svg {
  flex: 1;
  width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #fafafa;
}

.cluster-point {
  cursor: pointer;
  transition: r 0.2s;
}

.cluster-point:hover {
  r: 6;
}

.selected-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0f8f7;
  border-radius: 4px;
  border-left: 4px solid #075e54;
}

.selected-info h4 {
  color: #075e54;
  margin-bottom: 0.5rem;
}

.selected-info p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

:global(.cluster-tooltip) {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  pointer-events: none;
  z-index: 1000;
}
</style>
