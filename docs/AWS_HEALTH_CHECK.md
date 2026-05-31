# AWS Health Check Configuration

## Security Group Setup (Required)

To access the health check endpoints from your load balancer, monitoring service, or externally, you need to update the EC2 Security Group to allow inbound traffic on port 5000.

### Option 1: Open to Specific IP (Recommended for Security)

**When:** You're accessing from a fixed IP (home/office)

1. Go to **AWS Console** → **EC2** → **Security Groups**
2. Select your `stop-loss-monitor` security group
3. Click **Edit inbound rules**
4. Add new rule:
   - **Type**: Custom TCP
   - **Port Range**: 5000
   - **Source**: Your IP (e.g., `203.0.113.42/32`) or CIDR block
   - **Description**: Health check endpoint
5. Click **Save rules**

```
Protocol: TCP
Port: 5000
Source: YOUR_IP/32
```

### Option 2: Open to Load Balancer (Recommended for Production)

**When:** You have an AWS load balancer checking health

1. Go to **AWS Console** → **EC2** → **Security Groups**
2. Select your `stop-loss-monitor` security group
3. Add new rule:
   - **Type**: Custom TCP
   - **Port Range**: 5000
   - **Source**: Select security group of your load balancer
   - **Description**: Health check from load balancer
4. Click **Save rules**

### Option 3: Open to Anywhere (Not Recommended)

⚠️ **Only for testing/development**

```
Protocol: TCP
Port: 5000
Source: 0.0.0.0/0
```

---

## Testing from Your Local Machine

Once the security group is updated:

```bash
# Get your EC2 instance's public IP
# Then test the endpoints:

# Basic health check
curl http://EC2_PUBLIC_IP:5000/health

# Detailed status
curl http://EC2_PUBLIC_IP:5000/health/detailed

# Readiness probe
curl http://EC2_PUBLIC_IP:5000/health/ready
```

Example:

```bash
curl http://54.234.56.78:5000/health
```

---

## AWS Load Balancer Integration

If you're using an Application Load Balancer (ALB) or Network Load Balancer (NLB):

### ALB Health Check Configuration

1. Go to **EC2** → **Target Groups**
2. Create/Edit target group
3. Set **Health check settings**:
   - **Protocol**: HTTP
   - **Path**: `/health/ready`
   - **Port**: 5000
   - **Healthy threshold**: 2
   - **Unhealthy threshold**: 3
   - **Timeout**: 5 seconds
   - **Interval**: 30 seconds
4. Click **Save**

The load balancer will automatically check `/health/ready` every 30 seconds and remove the instance if it becomes unhealthy.

---

## CloudWatch Monitoring

You can create a CloudWatch alarm that checks the health endpoint:

```bash
# Using AWS CLI to create an alarm
aws cloudwatch put-metric-alarm \
  --alarm-name stop-loss-monitor-health \
  --alarm-description "Monitor health check endpoint" \
  --metric-name HealthCheckStatus \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 1
```

---

## Docker Container (Optional)

If you're running in a container on EC2:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "run_monitor.py"]
```

---

## Kubernetes (EKS) Configuration

If running on AWS EKS:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stop-loss-monitor
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: monitor
          image: stop-loss-monitor:latest
          ports:
            - containerPort: 5000
              name: health

          readinessProbe:
            httpGet:
              path: /health/ready
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3

          livenessProbe:
            httpGet:
              path: /health/live
              port: 5000
            initialDelaySeconds: 60
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
```

---

## Troubleshooting

### Can't access health endpoint from outside

```bash
# 1. Check security group allows port 5000
# 2. Check monitor is running
ssh -i /path/to/key.pem ubuntu@YOUR_IP
ps aux | grep run_monitor.py

# 3. Check port is listening
ss -tlnp | grep 5000

# 4. Check logs
tail -f /home/ubuntu/stop-loss-monitor/logs/*.log

# 5. Test locally on EC2
curl http://localhost:5000/health
```

### Getting connection timeout

- EC2 is likely **not running** or health check **failed to start**
- Check logs: `tail -f logs/monitor.log`
- Restart monitor: `python run_monitor.py`

### Getting 503 (Service Unavailable)

- Monitor is **running but not ready yet** (still initializing)
- Wait 30-60 seconds for initialization to complete
- Then try again

---

## Summary

✅ Health check server runs on port 5000  
✅ Binding to `0.0.0.0` makes it externally accessible  
✅ AWS security group must allow inbound port 5000  
✅ Perfect for load balancers, monitoring, and alerting

**Next Steps:**

1. Update security group to allow port 5000
2. Deploy monitor to EC2
3. Test endpoints from your local machine
4. Configure load balancer/monitoring integration (optional)
