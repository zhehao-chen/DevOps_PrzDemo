"""
Demo App - Simulates business metrics for Prometheus scraping
"""
import time
import random
import threading
from flask import Flask
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ── Define Business Metrics ──────────────────────────────────────
# Counter: Monotonically increasing; ideal for request/error counts.
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

# Gauge: Can go up or down; ideal for concurrent users, memory usage, etc.
active_users = Gauge(
    'active_users',
    'Current number of online users'
)

order_queue_size = Gauge(
    'order_queue_size',
    'Current backlog in the order queue'
)

# Histogram: Samples observations; ideal for request latency or response sizes.
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request processing duration',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# ── Simulate Business Data Fluctuations ─────────────────────────
def simulate_metrics():
    """Background thread: Simulates realistic business metric behavior."""
    endpoints = ['/api/users', '/api/orders', '/api/products']
    methods = ['GET', 'POST', 'PUT']
    # Weighted statuses: more 200s than errors
    statuses = ['200', '200', '200', '404', '500']  

    while True:
        # Simulate HTTP requests
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        status = random.choice(statuses)
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

        # Simulate request latency
        # Exponential distribution with a mean of 0.2s (200ms)
        latency = random.expovariate(1 / 0.2)  
        request_duration_seconds.labels(endpoint=endpoint).observe(latency)

        # Simulate user fluctuation (higher during "midday")
        hour = time.localtime().tm_hour
        base_users = 100 + 50 * abs(12 - hour)  
        active_users.set(base_users + random.randint(-20, 20))

        # Simulate order queue backlog
        order_queue_size.set(random.randint(0, 500))

        time.sleep(2)

# ── HTTP Endpoints ────────────────────────────────────────────
@app.route('/metrics')
def metrics():
    """Prometheus scraping endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}, 200

@app.route('/')
def index():
    """Simple Web UI"""
    return '''
    <h2>🚀 Prometheus Demo App</h2>
    <p>Metrics Endpoint: <a href="/metrics">/metrics</a></p>
    <p>Health Check: <a href="/health">/health</a></p>
    <hr>
    <p>This application simulates the following business metrics:</p>
    <ul>
      <li><b>http_requests_total</b> - HTTP Request Count (Counter)</li>
      <li><b>active_users</b> - Online Users (Gauge)</li>
      <li><b>order_queue_size</b> - Order Queue Backlog (Gauge)</li>
      <li><b>request_duration_seconds</b> - Request Latency Distribution (Histogram)</li>
    </ul>
    '''

if __name__ == '__main__':
    # Start the background simulation thread
    t = threading.Thread(target=simulate_metrics, daemon=True)
    t.start()
    # Run the Flask app on port 8080
    app.run(host='0.0.0.0', port=8080)
