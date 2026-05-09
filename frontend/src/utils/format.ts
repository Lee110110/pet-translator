export function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

export function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function getWarningColor(level: string): string {
  const colors: Record<string, string> = {
    green: '#4CAF50',
    yellow: '#FFC107',
    orange: '#FF9800',
    red: '#F44336',
  }
  return colors[level] || '#999999'
}

export function getWarningLabel(level: string): string {
  const labels: Record<string, string> = {
    green: '正常',
    yellow: '轻微偏离',
    orange: '持续异常',
    red: '急症信号',
  }
  return labels[level] || '未知'
}

export function getScoreLabel(metric: string, score: number): string {
  const labels: Record<string, Record<number, string>> = {
    diet: { 1: '完全不吃', 2: '吃得少', 3: '正常', 4: '不错', 5: '很好' },
    water: { 1: '几乎不喝', 2: '喝得少', 3: '正常', 4: '喝得多', 5: '非常多' },
    stool: { 1: '腹泻/无排便', 2: '软便', 3: '正常', 4: '良好', 5: '很好' },
    spirit: { 1: '嗜睡', 2: '安静', 3: '正常', 4: '活跃', 5: '非常活跃' },
  }
  return labels[metric]?.[score] || String(score)
}

export function getMetricEmoji(metric: string): string {
  const emojis: Record<string, string> = {
    diet: '🍽️',
    water: '💧',
    stool: '🚽',
    spirit: '😸',
  }
  return emojis[metric] || '📊'
}