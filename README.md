# Prometheus + TSDB + Grafana Demo

## Architecture Overview

```
┌─────────────┐    /metrics     ┌──────────────┐    TSDB Storage
│  Demo App   │ ─────────────▶ │  Prometheus  │ ──────────▶ /prometheus/
│  (Flask)    │                 │   :9090      │              (Local Disk)
└─────────────┘                 └──────┬───────┘
                                       │ PromQL Query
┌─────────────┐    /metrics            ▼
│Node Exporter│ ─────────────▶ ┌──────────────┐
│(Host Metrics)│                │   Grafana    │ ──▶ Dashboard
└─────────────┘                │   :3000      │
                                └──────────────┘
```

## Data Flow

1. **Scrape**: Prometheus actively pulls `/metrics` endpoint from each target every 15 seconds
2. **Storage (TSDB)**: Data is written to local Time Series Database (`/prometheus` directory)
3. **Query (PromQL)**: Grafana queries data from Prometheus using PromQL
4. **Visualization (Dashboard)**: Grafana renders charts with auto-refresh

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Demo App | http://localhost:8080 | Sample application |
| Demo App Metrics | http://localhost:8080/metrics | Raw metrics data |
| Prometheus | http://localhost:9090 | Query interface, Target status |
| Node Exporter | http://localhost:9100/metrics | Host metrics |
| Grafana | http://localhost:3000 | Dashboard (admin/admin123)|

## Demo Metrics Explained

| Metric Name | Type | Description |
|-------------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests, grouped by method/endpoint/status |
| `active_users` | Gauge | Current online users (simulated fluctuation) |
| `order_queue_size` | Gauge | Order queue backlog |
| `request_duration_seconds` | Histogram | Request latency distribution, supports P50/P95/P99 calculation |

## Common PromQL Examples

```promql
# Request rate (per second)
rate(http_requests_total[1m])

# P99 latency
histogram_quantile(0.99, rate(request_duration_seconds_bucket[1m]))

# Error rate
rate(http_requests_total{status=~"5.."}[1m]) / rate(http_requests_total[1m])

# Active users trend
active_users

# CPU usage percentage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
```

## TSDB Details

Prometheus TSDB data is stored in Docker volume `prometheus_data`, corresponding to `/prometheus` directory in the container:

```
/prometheus/
├── chunks_head/     # Latest data in memory
├── wal/             # Write-Ahead Log, ensures no data loss
├── 01XXXXX/         # Compressed data blocks (one per 2 hours)
└── lock
```

You can view the contents with:
```bash
docker exec prometheus ls -la /prometheus/
```

## Architecture Components

### Prometheus
- **Role**: Metrics collection and storage engine
- **Port**: 9090
- **Data Retention**: 15 days (configurable)
- **Scrape Interval**: 15 seconds

### Demo App (Flask)
- **Role**: Sample application exposing custom metrics
- **Port**: 8080
- **Metrics**: Business metrics (requests, users, orders, latency)

### Node Exporter
- **Role**: System and hardware metrics collector
- **Port**: 9100
- **Metrics**: CPU, memory, disk, network stats

### Grafana
- **Role**: Visualization and dashboarding
- **Port**: 3000
- **Default Credentials**: admin/admin123
- **Data Source**: Pre-configured Prometheus connection

## Useful Commands

```bash
# Check service health
docker-compose ps

# View Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query metrics via API
curl 'http://localhost:9090/api/v1/query?query=up'

# Check TSDB disk usage
docker exec prometheus du -sh /prometheus/

# Restart specific service
docker-compose restart prometheus

# Remove all data and restart fresh
docker-compose down -v
docker-compose up -d
```

## Troubleshooting

### Prometheus not scraping targets
```bash
# Check target status in Prometheus UI
http://localhost:9090/targets

# Verify network connectivity
docker exec prometheus wget -O- http://demo-app:8080/metrics
```

### Grafana dashboard not loading
```bash
# Verify Prometheus data source
curl http://localhost:3000/api/datasources

# Check Grafana logs
docker-compose logs grafana
```

### High TSDB disk usage
```bash
# Check retention settings in prometheus.yml
# Default: 15 days

# Manually compact old data
docker exec prometheus promtool tsdb analyze /prometheus/
```

## Next Steps

1. **Explore Metrics**: Visit http://localhost:8080/metrics to see raw Prometheus format
2. **Run Queries**: Use Prometheus UI at http://localhost:9090 to test PromQL
3. **Create Dashboards**: Log into Grafana and build custom visualizations
4. **Add Alerts**: Configure alert rules in Prometheus for proactive monitoring
5. **Scale Up**: Add more exporters (Redis, MySQL, nginx) to monitor full stack

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [TSDB Format Specification](https://prometheus.io/docs/prometheus/latest/storage/)