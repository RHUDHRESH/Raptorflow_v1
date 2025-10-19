from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
import logging

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

AI_TOKEN_USAGE = Counter(
    'ai_tokens_used_total',
    'Total AI tokens used',
    ['business_id', 'api_type']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Structured logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

class MonitoringMiddleware:
    """Monitoring and observability"""
    
    @staticmethod
    async def track_request(request: Request, call_next):
        """Track all requests"""
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Log request
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                endpoint=request.url.path
            ).inc()
            
            # Log error
            logger.error(
                f"{request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Duration: {duration:.3f}s",
                exc_info=True
            )
            
            raise
    
    @staticmethod
    def track_ai_usage(business_id: str, api_type: str, tokens: int):
        """Track AI token usage"""
        AI_TOKEN_USAGE.labels(
            business_id=business_id,
            api_type=api_type
        ).inc(tokens)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check with detailed status"""
    
    # Check dependencies
    checks = {
        'supabase': await check_supabase(),
        'gemini': await check_gemini(),
        'perplexity': await check_perplexity(),
        'redis': await check_redis()
    }
    
    all_healthy = all(checks.values())
    
    return {
        'status': 'healthy' if all_healthy else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks,
        'version': os.getenv('APP_VERSION', 'dev')
    }

async def check_supabase():
    try:
        supabase = get_supabase_client()
        supabase.table('businesses').select('id').limit(1).execute()
        return True
    except:
        return False

async def check_gemini():
    try:
        gemini = get_gemini_client()
        gemini.generate_content("test")
        return True
    except:
        return False
