<template>
  <div class="timeline-chart">
    <div v-if="!chartData" class="no-data">
      No timeline data available
    </div>
    <canvas v-else ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'TimelineChart',
  props: {
    messages: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chart: null,
      chartData: null
    }
  },
  watch: {
    messages: {
      handler() {
        this.processData()
        this.renderChart()
      },
      immediate: true
    }
  },
  mounted() {
    this.processData()
    this.renderChart()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy()
    }
  },
  methods: {
    processData() {
      if (!this.messages || this.messages.length === 0) {
        this.chartData = null
        return
      }
      
      // Group messages by date and sender
      const dateGroups = {}
      const senders = new Set()
      
      this.messages.forEach(msg => {
        const date = new Date(msg.timestamp).toDateString()
        const sender = msg.sender
        
        senders.add(sender)
        
        if (!dateGroups[date]) {
          dateGroups[date] = {}
        }
        
        if (!dateGroups[date][sender]) {
          dateGroups[date][sender] = 0
        }
        
        dateGroups[date][sender]++
      })
      
      // Sort dates
      const sortedDates = Object.keys(dateGroups).sort((a, b) => 
        new Date(a) - new Date(b)
      )
      
      // Create datasets for each sender
      const datasets = Array.from(senders).map((sender, index) => {
        const colors = [
          '#075e54', '#128c7e', '#25d366', '#dcf8c6', '#34b7f1',
          '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'
        ]
        
        return {
          label: sender,
          data: sortedDates.map(date => dateGroups[date][sender] || 0),
          backgroundColor: colors[index % colors.length] + '40',
          borderColor: colors[index % colors.length],
          borderWidth: 2,
          fill: false
        }
      })
      
      this.chartData = {
        labels: sortedDates,
        datasets: datasets
      }
    },
    
    renderChart() {
      if (!this.chartData) return
      
      if (this.chart) {
        this.chart.destroy()
      }
      
      const ctx = this.$refs.chartCanvas.getContext('2d')
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: this.chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: false
            },
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 20
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Messages'
              },
              beginAtZero: true
            }
          },
          interaction: {
            intersect: false,
            mode: 'index'
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.timeline-chart {
  height: 300px;
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
</style>
