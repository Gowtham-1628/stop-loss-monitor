# GitHub Actions Deployment Guide

This guide explains how to set up automated deployment from GitHub to AWS EC2.

## Prerequisites

1. **AWS EC2 Instance** running with the project already deployed (follow AWS_DEPLOYMENT_COMPLETE.md)
2. **GitHub Repository** with this code pushed to main branch
3. **EC2 Key Pair** (.pem file) for SSH access
4. **EC2 Security Group** allows SSH (port 22) from GitHub Actions runners

## Step 1: Prepare Your EC2 Instance

### 1.1 Ensure Git is Installed

```bash
ssh -i /path/to/key.pem ubuntu@YOUR_EC2_IP
sudo apt install -y git
```

### 1.2 Configure Git Credentials (if using HTTPS)

```bash
# Optional: Store GitHub credentials on EC2 for git operations
git config --global credential.helper store
# Enter credentials when prompted by first git pull
```

### 1.3 Give ubuntu User Sudo Access for systemctl

```bash
sudo visudo
# Add this line:
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl
# Save with Ctrl+O, Enter, Ctrl+X
```

This allows the deployment script to restart the service without password.

## Step 2: Set Up GitHub Secrets

GitHub Actions needs credentials to SSH into your EC2 instance.

### 2.1 Generate or Use Existing EC2 Key Pair

If you don't have your .pem key file, generate a new one:

```bash
# On your local machine
aws ec2 create-key-pair --key-name stop-loss-monitor-deploy --query 'KeyMaterial' --output text > ~/.ssh/stop-loss-monitor-deploy.pem
chmod 400 ~/.ssh/stop-loss-monitor-deploy.pem
```

### 2.2 Add SSH Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/Gowtham-1628/stop-loss-monitor
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Create these 3 secrets:

**Secret 1: EC2_SSH_KEY**

- **Name**: `EC2_SSH_KEY`
- **Value**: Copy the entire contents of your `.pem` file
  ```bash
  cat ~/.ssh/your-key.pem
  # Copy everything including -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY-----
  ```

**Secret 2: EC2_HOST**

- **Name**: `EC2_HOST`
- **Value**: Your EC2 instance's public IP (e.g., `54.234.56.78`)
  - Find this in AWS Console → EC2 → Instances → Select your instance → Public IPv4 address

**Secret 3: EC2_USER**

- **Name**: `EC2_USER`
- **Value**: `ubuntu` (default for Ubuntu AMI)

### 2.3 Verify Secrets

Go to **Settings** → **Secrets and variables** → **Actions** and confirm all 3 appear:

- ✅ EC2_SSH_KEY
- ✅ EC2_HOST
- ✅ EC2_USER

## Step 3: Test the Deployment

### 3.1 Manual Trigger (Recommended First Test)

1. Go to **Actions** tab on GitHub
2. Click **Deploy to AWS EC2** on the left
3. Click **Run workflow** → **Run workflow** button
4. Wait for it to complete (should take 1-2 minutes)

### 3.2 Check Logs

- Click the workflow run to see detailed logs
- Look for ✅ green checkmarks or ❌ red X marks

### 3.3 Verify on EC2

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
sudo systemctl status stop-loss-monitor
tail -20 logs/monitor_*.log
```

## Step 4: Automate Deployment

Once testing works, the deployment will automatically run when you push to `main`:

```bash
# Make a change and commit
git add .
git commit -m "Update stop loss validator logic"
git push origin main

# Watch deployment on Actions tab
```

## Troubleshooting

### "Permission denied (publickey)"

- Verify EC2_SSH_KEY secret contains full .pem file content (including BEGIN/END lines)
- Check EC2 security group allows SSH (port 22)

### "sudo: systemctl: command not found"

- The service needs to be set up on EC2 (see AWS_DEPLOYMENT_COMPLETE.md, Phase 7)
- Verify: `sudo systemctl status stop-loss-monitor`

### Deployment script hangs

- GitHub Actions has a 6-hour timeout per job
- Check if EC2 instance is running and reachable
- SSH key might not have proper permissions (should be 600)

### "service not running" after deployment

- Check service logs: `sudo journalctl -u stop-loss-monitor -n 50`
- Verify dependencies installed: `pip list | grep -E "pandas|APScheduler"`
- Check .env file exists: `ls -la /home/ubuntu/stop-loss-monitor/.env`

## Security Best Practices

1. **Restrict SSH access** - Update EC2 security group to only allow GitHub Actions IPs (optional)
2. **Rotate credentials** - Regenerate EC2 key pair if compromised
3. **Never commit secrets** - .env is in .gitignore, keep it that way
4. **Use IAM roles** - Consider using EC2 IAM role instead of hardcoded credentials (advanced)

## Manual Deployment (If Needed)

If GitHub Actions fails, you can still deploy manually:

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
cd /home/ubuntu/stop-loss-monitor
git fetch origin && git reset --hard origin/main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart stop-loss-monitor
```

---

**Next Steps:**

- [ ] Set up the 3 GitHub Secrets
- [ ] Test manual deployment trigger
- [ ] Make a test commit to verify auto-deployment works
- [ ] Monitor service in production
