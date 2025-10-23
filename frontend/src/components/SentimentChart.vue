<template>
  <div class="sentiment-chart">
    <div v-if="!chartData" class="no-data">
      No sentiment data available
    </div>
    <canvas v-else ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'SentimentChart',
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
      
      // Filter messages with sentiment data
      const messagesWithSentiment = this.messages.filter(msg => 
        msg.sentiment !== null && msg.sentiment !== undefined
      )
      
      if (messagesWithSentiment.length === 0) {
        this.chartData = null
        return
      }
      
      // Group by date and calculate average sentiment
      const dateGroups = {}
      
      messagesWithSentiment.forEach(msg => {
        const date = new Date(msg.timestamp).toDateString()
        
        if (!dateGroups[date]) {
          dateGroups[date] = {
            sentiments: [],
            count: 0
          }
        }
        
        dateGroups[date].sentiments.push(msg.sentiment)
        dateGroups[date].count++
      })
      
      // Sort dates and calculate averages
      const sortedDates = Object.keys(dateGroups).sort((a, b) => 
        new Date(a) - new Date(b)
      )
      
      const avgSentiments = sortedDates.map(date => {
        const group = dateGroups[date]
        return group.sentiments.reduce((sum, s) => sum + s, 0) / group.sentiments.length
      })
      
      this.chartData = {
        labels: sortedDates,
        datasets: [{
          label: 'Average Sentiment',
          data: avgSentiments,
          borderColor: '#075e54',
          backgroundColor: '#075e5440',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }]
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
              display: false
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
                text: 'Sentiment Score'
              },
              min: -1,
              max: 1
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
.sentiment-chart {
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
