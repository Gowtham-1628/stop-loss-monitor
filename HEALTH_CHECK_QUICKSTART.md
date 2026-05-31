# Health Check Quick Start

## Run the Monitor

```bash
python run_monitor.py
```

The health check server automatically starts and listens on `http://localhost:5000`

## Test the Endpoints

### 1. Basic Health Check

```bash
curl http://localhost:5000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T10:30:45.123456",
  "uptime": 1234567.89,
  "version": "1.0.0"
}
```

### 2. Detailed Status

```bash
curl http://localhost:5000/health/detailed
```

Shows last check time and position summary.

### 3. Ready Check

```bash
curl http://localhost:5000/health/ready
```

Returns `200` when monitor is ready, `503` if still initializing.

### 4. Liveness Check

```bash
curl http://localhost:5000/health/live
```

Always returns `200` if process is running.

## Demo Script

Run the automated health check test:

```bash
python test_health_endpoints.py
```

This tests all endpoints and shows their responses.

## Docker Health Check

Add this to your Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

## Kubernetes Probes

See [docs/HEALTH_CHECK.md](docs/HEALTH_CHECK.md) for Kubernetes configuration examples.

## Troubleshooting

- **Port 5000 already in use?** → Change port in `monitor.py` line where `HealthCheckServer` is created
- **Health endpoint not responding?** → Check monitor logs, ensure it's running
- **Requests failing?** → Make sure `Flask` is installed: `pip install Flask==3.0.0`

---

For more details, see [docs/HEALTH_CHECK.md](docs/HEALTH_CHECK.md)
