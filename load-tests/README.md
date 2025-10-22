# K6 Load Testing Suite

Comprehensive load testing scripts for RaptorFlow 2.0 using k6.

## Installation

### Prerequisites
- k6 installed: https://k6.io/docs/getting-started/installation/
- Node.js 14+ (for running application)
- Development server running on localhost:3000

### Install k6
```bash
# macOS with Homebrew
brew install k6

# Linux with apt
sudo apt-get install k6

# Windows with chocolatey
choco install k6

# Or download from: https://github.com/grafana/k6/releases
```

## Test Scripts

### 1. Baseline Test (`baseline.js`)
**Purpose:** Establish performance baseline with moderate load
**Load Pattern:**
- 0-10 users (2 min)
- 10-50 users (5 min)
- 50 users sustained (5 min)
- 50-0 users ramp down (2 min)

**Thresholds:**
- 95% of requests < 500ms
- 99% of requests < 1000ms
- Error rate < 10%

**Run:**
```bash
k6 run baseline.js
k6 run baseline.js --vus 50 --duration 10m  # Override defaults
BASE_URL=https://production.com k6 run baseline.js  # Custom URL
```

**Expected Results:**
- Response times: 100-500ms average
- Error rate: < 5%
- Success rate: > 95%

---

### 2. Spike Test (`spike.js`)
**Purpose:** Test behavior under sudden traffic spikes
**Load Pattern:**
- 5 users normal (1 min)
- Jump to 100 users (30 sec)
- 100 users sustained (1 min)
- Back to 5 users (30 sec)
- 0 users wind down (1 min)

**Thresholds:**
- 95% of requests < 1000ms (more lenient than baseline)
- 99% of requests < 2000ms
- Error rate < 15%

**Run:**
```bash
k6 run spike.js
k6 run spike.js --vus 100  # Override VU count
```

**Expected Results:**
- Response times increase during spike: 500-2000ms
- Error rate spikes: 10-15%
- System recovers after spike

---

### 3. Stress Test (`stress.js`)
**Purpose:** Find breaking point and system limits
**Load Pattern:**
- 10 users normal (2 min)
- Gradual increase to 300 users (15 min)
- Ramp down (3 min)

**Thresholds:**
- 99% of requests < 3000ms
- Error rate < 30%

**Run:**
```bash
k6 run stress.js
k6 run stress.js --insecure-skip-tls-verify  # For self-signed certs
```

**Expected Results:**
- Breaking point likely around 200-300 concurrent users
- Errors increase with load
- System should degrade gracefully

---

### 4. Workflow Test (`workflow.js`)
**Purpose:** Simulate realistic user journeys
**User Flow:**
1. Login
2. Load workspace
3. Load strategy data
4. Submit analysis
5. Fetch results

**Load Pattern:**
- 20 users warm up (2 min)
- 20-50 users ramp up (10 min)
- 50 users sustained (5 min)
- 50-0 users ramp down (2 min)

**Custom Metrics:**
- `workflow_duration` - Total time to complete workflow
- `login_success` - Login success rate
- `analysis_success` - Analysis success rate
- `active_users` - Current active users

**Run:**
```bash
k6 run workflow.js
k6 run workflow.js --vus 50 --duration 30m  # Longer test
```

**Expected Results:**
- Workflow completion: < 8 seconds
- Login success: > 95%
- Analysis success: > 90%

---

## Running Tests

### Quick Start
```bash
# Run baseline test
k6 run baseline.js

# View results
# k6 automatically outputs summary at end
```

### With Grafana Cloud Integration
```bash
# Set cloud token
export K6_CLOUD_TOKEN=your_token_here

# Run test and send to cloud
k6 run --out cloud baseline.js
```

### With HTML Report
```bash
# Install reporter
npm install -D @k6/html-reporter

# Run test with HTML output
k6 run baseline.js --out json=results.json
# Convert to HTML manually or use custom script
```

### Parallel Execution
```bash
# Run multiple tests in sequence
k6 run baseline.js
k6 run spike.js
k6 run stress.js

# Or in separate terminals for parallel
k6 run baseline.js &
k6 run workflow.js &
wait
```

### Environment Variables
```bash
# Custom base URL
BASE_URL=https://staging.example.com k6 run baseline.js

# Custom VUs and duration
k6 run --vus 100 --duration 5m baseline.js

# Custom thresholds
k6 run --threshold 'http_req_duration<500' baseline.js
```

---

## Performance Benchmarks

### Expected Baselines (Post Phase 4 Optimization)

| Metric | Baseline | Spike | Stress |
|--------|----------|-------|--------|
| **Response Time (p95)** | < 500ms | < 1s | < 3s |
| **Response Time (p99)** | < 1s | < 2s | < 5s |
| **Error Rate** | < 5% | < 15% | < 30% |
| **Throughput (req/s)** | 100+ | 50+ | 10+ |
| **Concurrent Users** | 50 | 100 | 300 |

### Performance Targets (Acceptable)
```
✅ Baseline: 50 concurrent users @ 95% < 500ms
✅ Spike: 100 concurrent users @ 95% < 1s
✅ Stress: 200 concurrent users @ < 30% error
✅ Workflow: Avg 6-8 second completion
```

### Red Flags (Need Optimization)
```
❌ Response times > 2s at baseline load
❌ Error rate > 10% at baseline
❌ Workflow completion > 15 seconds
❌ Memory leaks (response time increases over time)
```

---

## Analysis & Interpretation

### Key Metrics

**Duration (p95/p99)**
- p95: 95% of requests complete in this time
- p99: 99% of requests complete in this time
- *Interpretation:* p95 should be <500ms, p99 <1000ms

**Error Rate**
- Percentage of failed requests
- *Interpretation:* Should be <5% at baseline, <15% at spike

**Throughput**
- Requests per second the system can handle
- *Interpretation:* Should be >100 req/s at baseline load

**Active VUs**
- Number of concurrent virtual users
- *Interpretation:* Should handle 50+ for normal operation

### Identifying Issues

**High Response Times**
- Check server CPU/memory usage
- Look for slow database queries
- Review code for blocking operations
- Check network latency

**High Error Rates**
- Check application logs
- Verify database connectivity
- Check for connection pool exhaustion
- Review rate limiting

**Memory Leaks**
- Response times increase over time
- Check for event listener cleanup
- Review object allocation patterns
- Look for circular references

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Load Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: grafana/setup-k6-action@v1
      - run: k6 run load-tests/baseline.js
      - uses: actions/upload-artifact@v2
        with:
          name: k6-results
          path: results/
```

### GitLab CI Example
```yaml
load_test:
  image: grafana/k6:latest
  script:
    - k6 run load-tests/baseline.js
  artifacts:
    paths:
      - results/
```

---

## Best Practices

### ✅ Do
- Run tests on staging environment first
- Use realistic user loads (based on analytics)
- Monitor system resources during tests
- Document baselines and track over time
- Run tests before production deployments
- Test during expected peak times
- Use custom metrics for business logic

### ❌ Don't
- Run stress tests on production
- Use hardcoded credentials
- Create too many network connections
- Ignore error messages
- Run tests without alerting team
- Test without understanding results
- Assume tests are representative of production

---

## Troubleshooting

### Script Won't Run
```bash
# Check k6 version
k6 version

# Try simple test
k6 run -i 1 baseline.js

# Check JavaScript syntax
k6 inspect baseline.js
```

### High Error Rates
```bash
# Enable verbose logging
k6 run --http-debug=full baseline.js

# Check specific endpoint
# Modify script to add console.log statements
```

### Connection Refused
```bash
# Ensure dev server is running
npm run dev

# Check port
lsof -i :3000

# Verify BASE_URL
echo $BASE_URL
```

---

## Performance Recommendations

### If Baseline Test Fails

1. **Response times > 500ms (p95)**
   - Profile application code
   - Check database query performance
   - Optimize bundle size
   - Enable caching

2. **Error rate > 5%**
   - Check server logs for errors
   - Verify database connections
   - Check rate limiting settings
   - Review error handling

### If Spike Test Fails

1. **System can't handle 100 concurrent users**
   - Increase server resources
   - Implement load balancing
   - Optimize database queries
   - Add caching layer

### If Stress Test Shows Low Limits

1. **Breaking point < 200 users**
   - Horizontal scaling needed
   - Database optimization required
   - API redesign consideration
   - Caching strategy implementation

---

## Next Steps

1. **Establish Baseline**
   - Run baseline.js weekly
   - Track metrics over time
   - Document any degradation

2. **Continuous Testing**
   - Run spike and stress tests quarterly
   - Monitor for regressions
   - Optimize based on results

3. **Production Monitoring**
   - Use Real User Monitoring (RUM)
   - Compare RUM vs load test results
   - Adjust tests based on production behavior

---

## Resources

- K6 Documentation: https://k6.io/docs/
- Best Practices: https://k6.io/docs/misc/best-practices/
- API Reference: https://k6.io/docs/javascript-api/
- Community: https://community.k6.io/

---

**Last Updated:** Phase 5 Week 2
**Test Suite Version:** 1.0
