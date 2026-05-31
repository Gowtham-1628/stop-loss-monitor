# Health Check Endpoints

The Stop Loss Monitor includes a built-in HTTP health check server that exposes several endpoints for monitoring the application status. This is useful for:

- **Load Balancers**: Keep the service alive and healthy
- **Monitoring Services**: Track uptime and performance
- **Kubernetes/Container Orchestration**: Liveness and readiness probes
- **CI/CD Pipelines**: Verify deployment health

## Starting the Monitor

The health check server starts automatically when you run the monitor:

```bash
python run_monitor.py
```

The server listens on `http://localhost:5000` (or `http://0.0.0.0:5000` from external hosts).

## Endpoints

### 1. Basic Health Check

```
GET /health
```

Returns the basic health status.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T10:30:45.123456",
  "uptime": 1234567.89,
  "version": "1.0.0"
}
```

**Use for:** Simple "is it alive" checks

---

### 2. Detailed Health Check

```
GET /health/detailed
```

Returns detailed status including the last position check results.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T10:30:45.123456",
  "monitor": {
    "last_check_time": "2026-05-31T10:30:15.000000",
    "last_check_status": {
      "total": 5,
      "safe": 3,
      "at_risk": 1,
      "hit": 1
    }
  }
}
```

**Use for:** Detailed monitoring and alerting

---

### 3. Readiness Probe

```
GET /health/ready
```

Returns 200 if the monitor is ready to run checks, 503 if still initializing.

**Response (200 OK):**

```json
{
  "ready": true
}
```

**Response (503 Service Unavailable):**

```json
{
  "ready": false
}
```

**Use for:** Kubernetes readiness probes, load balancer health checks

---

### 4. Liveness Probe

```
GET /health/live
```

Returns 200 if the process is alive and responding.

**Response (200 OK):**

```json
{
  "live": true
}
```

**Use for:** Kubernetes liveness probes, process monitoring

---

## Example Usage

### Manual Testing

```bash
# Basic health check
curl http://localhost:5000/health

# Detailed status
curl http://localhost:5000/health/detailed

# Check if ready
curl http://localhost:5000/health/ready

# Check if alive
curl http://localhost:5000/health/live
```

### Kubernetes Configuration

**Deployment manifest with health checks:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stop-loss-monitor
spec:
  template:
    spec:
      containers:
        - name: monitor
          image: stop-loss-monitor:latest
          ports:
            - containerPort: 5000
              name: health

          # Readiness probe: Only send traffic when ready
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3

          # Liveness probe: Restart if not responding
          livenessProbe:
            httpGet:
              path: /health/live
              port: 5000
            initialDelaySeconds: 60
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
```

### Docker Compose Example

```yaml
version: "3.8"
services:
  monitor:
    build: .
    ports:
      - "5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Monitoring with Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "stop-loss-monitor"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["localhost:5000"]
```

---

## Configuration

The health check server runs on port `5000` by default. To change this, edit [monitor.py](../monitor.py):

```python
self.health_server = HealthCheckServer(host="0.0.0.0", port=8080)  # Change port here
```

Or set via environment variable (future enhancement).

---

## Error Responses

All endpoints return appropriate HTTP status codes:

| Status                  | Meaning                             |
| ----------------------- | ----------------------------------- |
| 200 OK                  | Health check passed                 |
| 503 Service Unavailable | Monitor not ready (readiness probe) |
| 404 Not Found           | Invalid endpoint                    |

---

## Troubleshooting

### Port already in use

```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Health endpoint not responding

```bash
# Check if monitor is running
ps aux | grep run_monitor.py

# Check logs
tail -f logs/*.log

# Test endpoint manually
curl -v http://localhost:5000/health
```

---

## See Also

- [README.md](../README.md) - Main documentation
- [modules/health_check.py](../modules/health_check.py) - Health check implementation
- [monitor.py](../monitor.py) - Monitor configuration
