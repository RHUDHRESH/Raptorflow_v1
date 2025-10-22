# 📊 Monitoring & Alerting Setup Guide

Comprehensive monitoring configuration for production observability.

---

## 🎯 Overview

This guide covers:
- Performance metrics monitoring
- Error tracking and alerting
- User behavior analytics
- Infrastructure monitoring
- Log aggregation
- Alert threshold configuration
- Dashboard setup

---

## 📈 Key Metrics to Monitor

### Frontend Metrics (Real User Monitoring)

```javascript
// Web Vitals
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1
- TTFB (Time to First Byte): < 600ms
- FCP (First Contentful Paint): < 1.8s

// Performance
- Page Load Time: < 3s
- API Response Time: < 500ms (p95)
- Time to Interactive: < 3.8s
- Interaction to Paint: < 100ms
- First Input Processing Time: < 100ms

// User Behavior
- Error Rate: < 2%
- 4xx Error Rate: < 1%
- 5xx Error Rate: < 0.5%
- JavaScript Errors: 0 allowed
- Session Duration: Track trending
- Bounce Rate: < 40%
```

### Backend Metrics

```javascript
// API Performance
- Response Time (avg): < 300ms
- Response Time (p95): < 500ms
- Response Time (p99): < 1000ms
- Throughput: > 100 requests/second
- Error Rate: < 1%

// Database
- Query Response Time: < 100ms
- Slow Query Count: < 5 per hour
- Connection Pool Usage: < 80%
- Lock Wait Time: < 1ms
- Replication Lag: < 1s

// Infrastructure
- CPU Usage: < 70%
- Memory Usage: < 80%
- Disk Usage: < 85%
- Network I/O: < 80% bandwidth
- Connection Count: < 80% of max

// Availability
- Uptime: > 99.9%
- Health Check Success: > 99%
- Deployment Success Rate: > 95%
```

### Business Metrics

```javascript
// User Metrics
- Active Users (concurrent): Track trending
- Daily Active Users (DAU): Track trending
- Monthly Active Users (MAU): Track trending
- New User Signups: Daily count
- User Retention: Day-1, Day-7, Day-30

// Feature Usage
- Most Used Features: Top 5
- Feature Adoption Rate: % of users using
- Workflow Completion Rate: % completing full flow
- Feature Performance: Response times by feature

// Business Goals
- Conversion Rate: % completing desired action
- Customer Acquisition Cost: $ per user
- Customer Lifetime Value: $ per user
- Churn Rate: % of users leaving
```

---

## 🔧 Monitoring Setup

### 1. Google Analytics 4 Setup

```bash
# 1a. Create GA4 property
# Google Analytics > Create Property
# - Property name: RaptorFlow Production
# - Reporting timezone: UTC
# - Currency: USD

# 1b. Get measurement ID
# Settings > Data Streams > Web > Get Measurement ID

# 1c. Add GA4 to application
```

```typescript
// lib/analytics.ts
import { GoogleAnalytics } from '@next/third-parties/google'

export function Analytics() {
  return (
    <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_ID} />
  )
}

// Or use gtag directly
import { pageview } from '@/lib/gtag'

export function trackPageView(path: string) {
  pageview({
    page_path: path,
    page_title: document.title,
  })
}

// Track events
export function trackEvent(eventName: string, params: Record<string, any>) {
  gtag('event', eventName, params)
}
```

```typescript
// pages/_app.tsx
import { Analytics } from '@/lib/analytics'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Analytics />
      <Component {...pageProps} />
    </>
  )
}
```

### 2. Web Vitals Monitoring

```typescript
// lib/web-vitals.ts
import { getCLS, getFCP, getFID, getLCP, getTTFB } from 'web-vitals'
import { trackEvent } from './analytics'

export function reportWebVitals() {
  getCLS(metric => {
    trackEvent('web_vital', {
      metric: 'CLS',
      value: metric.value,
      rating: metric.rating,
    })
  })

  getFCP(metric => {
    trackEvent('web_vital', {
      metric: 'FCP',
      value: metric.value,
      rating: metric.rating,
    })
  })

  getFID(metric => {
    trackEvent('web_vital', {
      metric: 'FID',
      value: metric.value,
      rating: metric.rating,
    })
  })

  getLCP(metric => {
    trackEvent('web_vital', {
      metric: 'LCP',
      value: metric.value,
      rating: metric.rating,
    })
  })

  getTTFB(metric => {
    trackEvent('web_vital', {
      metric: 'TTFB',
      value: metric.value,
      rating: metric.rating,
    })
  })
}

// Call in _app.tsx
useEffect(() => {
  reportWebVitals()
}, [])
```

### 3. Error Tracking (Sentry)

```bash
# 3a. Create Sentry account
# https://sentry.io/signup/

# 3b. Create new project
# Select: Next.js
# Get your DSN
```

```typescript
// pages/_app.tsx
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 0.1, // Sample 10% for performance tracking
  integrations: [
    new Sentry.Replay({
      maskAllText: true, // Redact sensitive data
      blockAllMedia: true,
    }),
  ],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0, // Capture all error sessions
})

// Catch errors
if (process.env.NODE_ENV === 'production') {
  Sentry.captureException(error)
}
```

```typescript
// API error handling
import * as Sentry from '@sentry/nextjs'

export default async function handler(req, res) {
  try {
    // Handle request
  } catch (error) {
    Sentry.captureException(error, {
      tags: {
        route: req.url,
        method: req.method,
      },
      user: {
        id: session?.user?.id,
        email: session?.user?.email,
      },
    })
    res.status(500).json({ error: 'Internal server error' })
  }
}
```

### 4. CloudWatch Monitoring (AWS)

```bash
# 4a. Create log group
aws logs create-log-group \
  --log-group-name /raptorflow/prod \
  --region us-east-1

# 4b. Create metric filters
# Log Group Settings > Metric Filters > Create Metric Filter

# Search pattern for errors:
[time, request_id, level = "ERROR", ...]

# Metric name: ErrorCount
# Metric value: 1

# 4c. Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name raptorflow-error-rate-high \
  --alarm-description "Error rate exceeds 5%" \
  --metric-name ErrorRate \
  --namespace RaptorFlow \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:alerts
```

### 5. Custom Metrics

```typescript
// lib/metrics.ts
import { CloudWatch } from '@aws-sdk/client-cloudwatch'

const cloudwatch = new CloudWatch()

export async function publishMetric(
  metricName: string,
  value: number,
  unit: string = 'Count'
) {
  await cloudwatch.putMetricData({
    Namespace: 'RaptorFlow',
    MetricData: [
      {
        MetricName: metricName,
        Value: value,
        Unit: unit,
        Timestamp: new Date(),
      },
    ],
  })
}

// Usage
export async function trackAPIResponse(endpoint: string, duration: number) {
  await publishMetric(`API-${endpoint}`, duration, 'Milliseconds')
}

export async function trackFeatureUsage(featureName: string) {
  await publishMetric(`Feature-${featureName}`, 1, 'Count')
}

export async function trackUserEvent(eventType: string, userId: string) {
  await publishMetric(`User-${eventType}`, 1, 'Count')
}
```

---

## 📊 Dashboard Configuration

### 1. CloudWatch Dashboard

```bash
# Create JSON config for dashboard
cat > dashboard-config.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["RaptorFlow", "ErrorRate", {"stat": "Average"}],
          [".", "ResponseTime", {"stat": "p95"}],
          [".", "ApiThroughput", {"stat": "Sum"}],
          [".", "CPUUtilization", {"stat": "Average"}],
          [".", "MemoryUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Application Performance"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "fields @timestamp, @message, @duration | stats avg(@duration) by bin(5m)",
        "region": "us-east-1",
        "title": "API Response Times"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name RaptorFlow-Production \
  --dashboard-body file://dashboard-config.json
```

### 2. Grafana Dashboard

```bash
# Install Grafana
docker run -d -p 3000:3000 \
  --name grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Access at http://localhost:3000
# Add data sources:
# - CloudWatch
# - Prometheus
# - Elasticsearch

# Import dashboard template:
# Dashboard > Import > Grafana dashboard ID (e.g., 1860 for Node Exporter)
```

### 3. Custom Dashboard

```html
<!-- public/monitoring/dashboard.html -->
<html>
  <head>
    <title>RaptorFlow Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body>
    <div id="dashboard">
      <h1>RaptorFlow Production Monitoring</h1>

      <!-- Error Rate Chart -->
      <div class="metric">
        <h2>Error Rate</h2>
        <canvas id="errorRateChart"></canvas>
      </div>

      <!-- Response Time Chart -->
      <div class="metric">
        <h2>API Response Times</h2>
        <canvas id="responseTimeChart"></canvas>
      </div>

      <!-- User Activity Chart -->
      <div class="metric">
        <h2>Active Users</h2>
        <canvas id="activeUsersChart"></canvas>
      </div>
    </div>

    <script>
      // Fetch data and update charts every 30 seconds
      async function updateMetrics() {
        const metrics = await fetch('/api/metrics').then(r => r.json())

        // Update error rate chart
        errorRateChart.data.datasets[0].data = metrics.errorRates
        errorRateChart.update()

        // Update response time chart
        responseTimeChart.data.datasets[0].data = metrics.responseTimes
        responseTimeChart.update()

        // Update active users chart
        activeUsersChart.data.datasets[0].data = metrics.activeUsers
        activeUsersChart.update()
      }

      // Update every 30 seconds
      setInterval(updateMetrics, 30000)
      updateMetrics() // Initial load
    </script>
  </body>
</html>
```

---

## 🚨 Alert Configuration

### Alert Thresholds

```bash
# CRITICAL ALERTS (page immediately)
aws cloudwatch put-metric-alarm \
  --alarm-name critical-error-rate \
  --metric-name ErrorRate \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --period 60 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:critical-alerts

aws cloudwatch put-metric-alarm \
  --alarm-name critical-uptime \
  --metric-name HealthCheckStatus \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2 \
  --period 60 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:critical-alerts

# WARNING ALERTS (notify team)
aws cloudwatch put-metric-alarm \
  --alarm-name warning-error-rate \
  --metric-name ErrorRate \
  --threshold 2 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 5 \
  --period 300 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:warning-alerts

aws cloudwatch put-metric-alarm \
  --alarm-name warning-response-time \
  --metric-name ResponseTime \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 5 \
  --period 300 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:warning-alerts
```

### SNS Notification Setup

```bash
# Create SNS topics
aws sns create-topic --name raptorflow-critical-alerts
aws sns create-topic --name raptorflow-warning-alerts

# Get topic ARNs
aws sns list-topics

# Subscribe email to alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:raptorflow-critical-alerts \
  --protocol email \
  --notification-endpoint team@raptorflow.com

# Subscribe Slack to alerts
# Using webhook integration:
# 1. Create Slack webhook: https://api.slack.com/messaging/webhooks
# 2. Use SNS Lambda trigger to post to Slack
```

---

## 📋 Logging Setup

### 1. Application Logging

```typescript
// lib/logger.ts
import winston from 'winston'

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'raptorflow' },
  transports: [
    // Console output
    new winston.transports.Console({
      format: winston.format.simple(),
    }),

    // File output (CloudWatch will read this)
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})

export default logger

// Usage
logger.info('User login', { userId: user.id, email: user.email })
logger.error('Database connection failed', { error: error.message })
logger.warn('High response time', { duration: 1200, endpoint: '/api/analyze' })
```

### 2. CloudWatch Logs

```bash
# Configure log streaming to CloudWatch
# In your application server (EC2, ECS, Lambda):

# For ECS, add to task definition:
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/raptorflow/prod",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs"
    }
  }
}

# View logs
aws logs tail /raptorflow/prod --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /raptorflow/prod \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s)*1000 - 3600000))
```

### 3. Log Aggregation with ELK Stack

```bash
# Option: Self-hosted ELK Stack
docker run -d --name elasticsearch \
  -e discovery.type=single-node \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.5.0

docker run -d --name kibana \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/kibana/kibana:8.5.0

docker run -d --name filebeat \
  -v /var/log:/var/log \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/beats/filebeat:8.5.0
```

---

## 📞 On-Call & Incident Response

### Escalation Policy

```
LEVEL 1 (0-5 min): #incidents Slack channel
├─ Post critical alert
├─ Page on-call engineer
└─ Create incident in PagerDuty

LEVEL 2 (5-15 min): Tech Lead
├─ If Level 1 can't resolve
├─ Page tech lead
└─ Escalate in PagerDuty

LEVEL 3 (15+ min): Management
├─ If Level 2 can't resolve
├─ Contact VP Engineering
└─ CEO notification (if < 99.9% uptime impact)
```

### Incident Severity Levels

```
SEVERITY 1 (Critical)
- System completely down
- Data loss occurring
- Security breach
- All users affected
- Response time: < 5 minutes
- Resolution time: < 1 hour

SEVERITY 2 (High)
- Major features not working
- Significant performance degradation
- Many users affected (> 10%)
- Response time: < 15 minutes
- Resolution time: < 4 hours

SEVERITY 3 (Medium)
- Minor features affected
- Small user impact (< 10%)
- Workaround available
- Response time: < 1 hour
- Resolution time: < 24 hours

SEVERITY 4 (Low)
- Cosmetic issues
- Documentation needed
- No user impact
- Response time: < 8 hours
- Resolution time: < 1 week
```

---

## ✅ Monitoring Checklist

```
SETUP
☐ Google Analytics 4 configured
☐ Web Vitals tracking enabled
☐ Sentry error tracking enabled
☐ CloudWatch log groups created
☐ Custom metrics defined
☐ SNS topics created

DASHBOARDS
☐ CloudWatch dashboard created
☐ Grafana dashboard configured
☐ Custom dashboard deployed
☐ Real-time metrics visible
☐ Team has access to dashboards

ALERTS
☐ Critical alerts configured
☐ Warning alerts configured
☐ Email notifications working
☐ Slack notifications working
☐ Alert thresholds validated
☐ Escalation policy documented

LOGGING
☐ Application logging configured
☐ CloudWatch logs streaming
☐ Log retention policy set
☐ Sensitive data redacted
☐ Log search functionality tested

INCIDENT RESPONSE
☐ On-call schedule created
☐ Escalation policy documented
☐ Runbook for common issues
☐ Communication plan established
☐ Post-incident review process
```

---

## 🔗 Monitoring Resources

- [Google Analytics Documentation](https://support.google.com/analytics)
- [Web Vitals Guide](https://web.dev/vitals/)
- [Sentry Documentation](https://docs.sentry.io/)
- [CloudWatch User Guide](https://docs.aws.amazon.com/cloudwatch/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

**Last Updated:** Phase 5 Week 3
**Version:** 1.0
**Monitoring Tools:** GA4, Sentry, CloudWatch, Grafana, Custom Dashboards
