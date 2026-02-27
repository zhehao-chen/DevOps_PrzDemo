# Prometheus + TSDB + Grafana Demo

## 架构说明

```
┌─────────────┐    /metrics     ┌──────────────┐    TSDB存储
│  Demo App   │ ─────────────▶ │  Prometheus  │ ──────────▶ /prometheus/
│  (Flask)    │                 │   :9090      │              (本地磁盘)
└─────────────┘                 └──────┬───────┘
                                       │ PromQL查询
┌─────────────┐    /metrics            ▼
│Node Exporter│ ─────────────▶ ┌──────────────┐
│  (主机指标)  │                │   Grafana    │ ──▶ Dashboard
└─────────────┘                │   :3000      │
                                └──────────────┘
```

## 数据流程

1. **采集 (Scrape)**: Prometheus 每 15 秒主动拉取各 target 的 `/metrics` 端点
2. **存储 (TSDB)**: 数据写入本地 Time Series Database（`/prometheus` 目录）
3. **查询 (PromQL)**: Grafana 通过 PromQL 从 Prometheus 查询数据
4. **展示 (Dashboard)**: Grafana 渲染图表，自动刷新

## 快速启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Demo App | http://localhost:8080 | 示例应用 |
| Demo App Metrics | http://localhost:8080/metrics | 原始指标数据 |
| Prometheus | http://localhost:9090 | 查询界面、Target状态 |
| Node Exporter | http://localhost:9100/metrics | 主机指标 |
| Grafana | http://localhost:3000 | Dashboard（admin/admin123）|

## Demo 指标说明

| 指标名 | 类型 | 含义 |
|--------|------|------|
| `http_requests_total` | Counter | HTTP请求总次数，按method/endpoint/status分组 |
| `active_users` | Gauge | 当前在线用户数（模拟波动） |
| `order_queue_size` | Gauge | 订单队列积压量 |
| `request_duration_seconds` | Histogram | 请求延迟分布，支持计算P50/P95/P99 |

## 常用 PromQL 示例

```promql
# 请求速率（每秒）
rate(http_requests_total[1m])

# P99 延迟
histogram_quantile(0.99, rate(request_duration_seconds_bucket[1m]))

# 错误率
rate(http_requests_total{status=~"5.."}[1m]) / rate(http_requests_total[1m])

# 在线用户数趋势
active_users

# CPU 使用率
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
```

## TSDB 说明

Prometheus TSDB 数据存储在 Docker volume `prometheus_data` 中，对应容器内 `/prometheus` 目录：

```
/prometheus/
├── chunks_head/     # 内存中的最新数据
├── wal/             # Write-Ahead Log，保证数据不丢失
├── 01XXXXX/         # 已压缩的数据块（每2小时一个）
└── lock
```

可以通过以下命令查看：
```bash
docker exec prometheus ls -la /prometheus/
```
