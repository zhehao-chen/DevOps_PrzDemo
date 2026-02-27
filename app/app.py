"""
Demo 应用 - 模拟业务指标，暴露给 Prometheus 采集
"""
import time
import random
import threading
from flask import Flask
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ── 定义业务指标 ──────────────────────────────────────────
# Counter: 只增不减，适合请求次数、错误次数
http_requests_total = Counter(
    'http_requests_total',
    'HTTP 请求总次数',
    ['method', 'endpoint', 'status']
)

# Gauge: 可增可减，适合当前连接数、内存使用等
active_users = Gauge(
    'active_users',
    '当前在线用户数'
)

order_queue_size = Gauge(
    'order_queue_size',
    '订单队列积压数量'
)

# Histogram: 统计分布，适合请求延迟、响应大小
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP 请求处理时长',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# ── 模拟业务数据变化 ─────────────────────────────────────
def simulate_metrics():
    """后台线程：模拟真实业务的指标波动"""
    endpoints = ['/api/users', '/api/orders', '/api/products']
    methods = ['GET', 'POST', 'PUT']
    statuses = ['200', '200', '200', '404', '500']  # 故意加权，200 更多

    while True:
        # 模拟 HTTP 请求
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        status = random.choice(statuses)
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

        # 模拟请求延迟
        latency = random.expovariate(1 / 0.2)  # 平均 200ms
        request_duration_seconds.labels(endpoint=endpoint).observe(latency)

        # 模拟用户数波动（白天多，夜晚少）
        hour = time.localtime().tm_hour
        base_users = 100 + 50 * abs(12 - hour)  # 中午用户最多
        active_users.set(base_users + random.randint(-20, 20))

        # 模拟订单队列
        order_queue_size.set(random.randint(0, 500))

        time.sleep(2)

# ── HTTP 端点 ────────────────────────────────────────────
@app.route('/metrics')
def metrics():
    """Prometheus 采集端点"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

@app.route('/')
def index():
    return '''
    <h2>🚀 Prometheus Demo App</h2>
    <p>指标端点: <a href="/metrics">/metrics</a></p>
    <p>健康检查: <a href="/health">/health</a></p>
    <hr>
    <p>该应用模拟以下业务指标：</p>
    <ul>
      <li><b>http_requests_total</b> - HTTP 请求计数（Counter）</li>
      <li><b>active_users</b> - 在线用户数（Gauge）</li>
      <li><b>order_queue_size</b> - 订单队列积压（Gauge）</li>
      <li><b>request_duration_seconds</b> - 请求延迟分布（Histogram）</li>
    </ul>
    '''

if __name__ == '__main__':
    # 启动后台模拟线程
    t = threading.Thread(target=simulate_metrics, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=8080)
