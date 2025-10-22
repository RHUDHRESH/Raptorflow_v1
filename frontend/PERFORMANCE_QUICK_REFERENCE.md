# Performance Optimization Quick Reference

**Updated:** Phase 4 Week 3 Complete
**For:** RaptorFlow Frontend Developers

---

## 🚀 Quick Start

### 1. Use Performance-Enhanced Components
```typescript
// Use memoized versions (with -memoized suffix)
import ContextIntakePanel from '@/components/strategy/ContextIntakePanel-memoized';
import Toast from '@/components/ui/Toast-memoized';
import ConfirmationDialog from '@/components/ui/ConfirmationDialog-memoized';
import ContextItemsList from '@/components/strategy/ContextItemsList-memoized';
```

### 2. Track Your Custom Metrics
```typescript
import { getMetricsCollector } from '@/lib/performance-metrics';

const collector = getMetricsCollector();

// Record component render time
collector.recordComponentRender('MyComponent', 45);

// Record API call
collector.recordApiCall('/api/endpoint', 180, 200);

// Record user interaction
collector.recordInteraction('button-click', 50);
```

### 3. Wrap API Calls
```typescript
import { fetchWithMetrics } from '@/lib/performance-metrics';

// Automatically tracks timing
const data = await fetchWithMetrics<DataType>('/api/endpoint');
```

### 4. Access Performance Dashboard
```
Look for "📊 Performance" button in bottom-right corner
Click to expand → See real-time metrics
Click "Export JSON" to download data
```

---

## 📊 Performance Monitoring

### View Web Vitals
```typescript
import { getWebVitalsMonitor } from '@/lib/web-vitals';

const monitor = getWebVitalsMonitor();
const vitals = monitor.getVitals();

console.log(vitals.LCP);   // Largest Contentful Paint (ms)
console.log(vitals.FID);   // First Input Delay (ms)
console.log(vitals.CLS);   // Cumulative Layout Shift
```

### Check Metrics Report
```typescript
import { getMetricsCollector } from '@/lib/performance-metrics';

const collector = getMetricsCollector();
const report = collector.getReport();

console.log(report.metrics);    // Aggregated metrics
console.log(report.topSlow);    // 5 slowest events
console.log(report.topFrequent); // 5 most frequent
```

### Track Errors
```typescript
import { getErrorTracker } from '@/lib/error-tracking';

const tracker = getErrorTracker();

tracker.addBreadcrumb('User action', 'user-action');

try {
  // some operation
} catch (error) {
  tracker.captureError(error.message, 'error', 'high', error.stack);
}
```

---

## ⚡ Optimization Techniques

### 1. Debounce High-Frequency Updates
```typescript
import { debounce } from '@/lib/performance-utils';

const debouncedOnChange = debounce((value) => {
  // Called max once per 100ms
  updateState(value);
}, 100);

// Use in event handlers
<input onChange={(e) => debouncedOnChange(e.target.value)} />
```

### 2. Throttle for Smooth Interactions
```typescript
import { throttle } from '@/lib/performance-utils';

const throttledOnScroll = throttle(() => {
  // Called max once per 100ms
  handleScroll();
}, 100);

window.addEventListener('scroll', throttledOnScroll);
```

### 3. RAF Debounce for Animations
```typescript
import { rafDebounce } from '@/lib/performance-utils';

const debouncedDrag = rafDebounce((x, y) => {
  // Scheduled next animation frame
  updatePosition(x, y);
});

element.addEventListener('drag', (e) => debouncedDrag(e.x, e.y));
```

### 4. Memoize Expensive Calculations
```typescript
import { memoize } from '@/lib/performance-utils';

const expensiveCalculation = memoize((input) => {
  // Cached by input value
  return computeResult(input);
});
```

### 5. Use React.memo for Components
```typescript
import { memo } from 'react';

const ExpensiveComponent = memo(({ data }) => {
  return <div>{data}</div>;
});

// With custom comparison
export default memo(Component, (prev, next) => {
  return prev.id === next.id;  // Only re-render if ID changes
});
```

### 6. useCallback for Event Handlers
```typescript
import { useCallback } from 'react';

const handleClick = useCallback(() => {
  // Handler reference stays stable
  doSomething();
}, [dependency]); // Re-create only if dependency changes
```

### 7. useMemo for Expensive Computations
```typescript
import { useMemo } from 'react';

const memoizedValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]); // Recalculate only if data changes
```

---

## 🎯 Performance Targets

### Core Web Vitals
```
LCP (Largest Contentful Paint):
  Good:  ≤ 2.5s
  Poor:  > 4.0s

FID (First Input Delay):
  Good:  ≤ 100ms
  Poor:  > 300ms

CLS (Cumulative Layout Shift):
  Good:  ≤ 0.1
  Poor:  > 0.25
```

### Custom Metrics
```
Component Render Time:
  Good:  ≤ 50ms
  Poor:  > 100ms

API Call Duration:
  Good:  ≤ 500ms
  Poor:  > 2000ms

User Interaction Response:
  Good:  ≤ 100ms
  Poor:  > 500ms
```

---

## 🔍 Debugging Performance

### Find Slow Components
```typescript
const report = collector.getReport();

// Look at componentMetrics
Object.entries(report.metrics).forEach(([name, metric]) => {
  if (name.startsWith('component:') && metric.mean > 50) {
    console.warn(`Slow component: ${name}, avg ${metric.mean}ms`);
  }
});
```

### Find Slow API Calls
```typescript
// Look at API metrics
Object.entries(report.metrics).forEach(([name, metric]) => {
  if (name.startsWith('api:') && metric.p95 > 500) {
    console.warn(`Slow API: ${name}, p95 ${metric.p95}ms`);
  }
});
```

### Check Error Trends
```typescript
const errorTracker = getErrorTracker();
const summary = errorTracker.getSummary();

console.log('Total errors:', summary.total);
console.log('By severity:', summary.bySeverity);
console.log('By type:', summary.byType);

// Get recent errors
const recentErrors = errorTracker.getErrors().slice(-10);
```

### Export Data for Analysis
```typescript
// Export metrics
const metricsJson = collector.export();
console.log(metricsJson);

// Export errors
const errorJson = errorTracker.export();
console.log(errorJson);

// Download as file
const blob = new Blob([metricsJson], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'metrics.json';
a.click();
```

---

## 🛠️ Common Patterns

### Pattern 1: Track Component Render Time
```typescript
import { memo, useEffect, useRef } from 'react';
import { getMetricsCollector } from '@/lib/performance-metrics';

const MyComponent = memo(() => {
  const startTime = useRef(performance.now());

  useEffect(() => {
    const renderTime = performance.now() - startTime.current;
    getMetricsCollector().recordComponentRender('MyComponent', renderTime);
  });

  return <div>Content</div>;
});
```

### Pattern 2: Track API with Timing
```typescript
import { getMetricsCollector } from '@/lib/performance-metrics';

async function fetchJobs(workspaceId: string) {
  const startTime = performance.now();

  try {
    const response = await fetch(`/api/jobs/${workspaceId}`);
    const duration = performance.now() - startTime;

    getMetricsCollector().recordApiCall(
      `/api/jobs/${workspaceId}`,
      duration,
      response.status
    );

    return response.json();
  } catch (error) {
    const duration = performance.now() - startTime;
    getMetricsCollector().recordApiCall(`/api/jobs/${workspaceId}`, duration, 0);
    throw error;
  }
}
```

### Pattern 3: Debounce with Metrics
```typescript
import { debounce } from '@/lib/performance-utils';
import { getMetricsCollector } from '@/lib/performance-metrics';

const collector = getMetricsCollector();

const handleSliderChange = debounce((value) => {
  const startTime = performance.now();

  // Update state
  updateSliderValue(value);

  const duration = performance.now() - startTime;
  collector.recordMetric('slider:change', duration, 'interaction');
}, 100);
```

### Pattern 4: Memoized Component with Custom Comparison
```typescript
import { memo } from 'react';

const ListItem = memo(
  ({ item, onDelete }) => (
    <div>
      {item.name}
      <button onClick={() => onDelete(item.id)}>Delete</button>
    </div>
  ),
  // Custom comparison: only re-render if ID changes
  (prevProps, nextProps) => {
    return prevProps.item.id === nextProps.item.id;
  }
);
```

---

## 📈 Performance Checklist

### When Writing New Components
- [ ] Use `React.memo` if component is expensive (>50 lines)
- [ ] Use `useCallback` for event handlers
- [ ] Use `useMemo` for expensive calculations
- [ ] Consider splitting into smaller sub-components
- [ ] Add metrics tracking for monitoring

### When Writing API Calls
- [ ] Use `fetchWithMetrics()` or manually track timing
- [ ] Consider debouncing high-frequency calls
- [ ] Log errors with full context
- [ ] Add breadcrumb for API operations

### When Rendering Lists
- [ ] Memoize list items
- [ ] Use custom equality comparison (not default shallow)
- [ ] Use unique IDs as keys
- [ ] Track render performance

### When Handling Events
- [ ] Debounce frequent events (typing, scrolling)
- [ ] Throttle scroll/resize events
- [ ] Use RAF debounce for animations
- [ ] Track interaction timing

---

## 🚀 Deployment Checklist

- [ ] Web Vitals tracking enabled
- [ ] Performance dashboard verified
- [ ] Metrics collection working
- [ ] Error tracking configured
- [ ] Alert rules configured
- [ ] Backend endpoints ready
- [ ] Analytics database schema created
- [ ] Metrics export working
- [ ] Bundle size verified (-18% target)
- [ ] Component memoization applied
- [ ] Code splitting verified
- [ ] Load testing completed

---

## 📞 Getting Help

### Check Monitoring Data
1. Open Performance Dashboard (bottom-right 📊 button)
2. View Core Web Vitals and metrics
3. Export JSON for analysis
4. Check error logs for issues

### Review Documentation
- `PHASE_4_IMPLEMENTATION_GUIDE.md` - Overall strategy
- `PHASE_4_WEEK_2_MEMOIZATION_GUIDE.md` - Memoization details
- `PHASE_4_WEEK_3_MONITORING_GUIDE.md` - Monitoring setup
- `PHASE_4_CUMULATIVE_STATUS.md` - Complete status

### Debug Performance
1. Check metrics report for slow components
2. Look for error patterns
3. Compare before/after metrics
4. Use Chrome DevTools for profiling

---

## 💡 Pro Tips

1. **Always use debounce for high-frequency events** (50+ per second)
2. **Profile before optimizing** - Use the dashboard to find real bottlenecks
3. **Memoize expensive components** - Especially in lists
4. **Use useCallback for callbacks** - Always, when passing to memoized children
5. **Export metrics regularly** - Keep historical data for trending
6. **Review error patterns** - Most errors have common root causes
7. **Test on slow networks** - 3G simulation in DevTools
8. **Test on low-end devices** - Target devices with 2GB RAM

---

**Last Updated:** Phase 4 Week 3
**Next Update:** After Week 4 Completion
