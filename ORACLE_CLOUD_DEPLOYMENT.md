# Oracle Cloud Free Tier Deployment Guide

Complete guide to deploy your Real Estate Scraper on Oracle Cloud's always-free tier.

---

## Why Oracle Cloud?

- ✅ **Free Forever** (not a trial)
- ✅ **Always Online** (24/7 cloud server)
- ✅ **Unlimited Execution Time**
- ✅ **No Credit Card Required** (after initial verification)
- ✅ **2 Free VMs** or 1 VM with 2GB RAM
- ✅ **200GB Storage**
- ✅ **Unlimited Bandwidth**

---

## Step 1: Create Oracle Cloud Account

1. Go to: https://www.oracle.com/cloud/free/

2. Click **"Start for free"**

3. Fill in:
   - Email
   - Country
   - Cloud Account Name (e.g., "realestate-scraper")

4. Verify email

5. Add payment method (required for verification, but won't be charged)
   - Oracle requires this to prevent abuse
   - You'll only be charged if you manually upgrade
   - Always-free resources remain free forever

6. Complete registration

---

## Step 2: Create Ubuntu VM Instance

1. **Login to Oracle Cloud Console**
   - https://cloud.oracle.com

2. **Create Compute Instance**
   - Click **"Create Instance"**
   - Name: `realestate-scraper`
   - Image: **Ubuntu 22.04** (recommended)
   - Shape: **VM.Standard.E2.1.Micro** (always-free)
     - 1 OCPU
     - 1 GB RAM
     - This is sufficient for the scraper

3. **Configure Networking**
   - Virtual Cloud Network: Use default
   - Subnet: Use default
   - Public IP: **Assign a public IPv4 address**

4. **Add SSH Key**
   - Generate SSH keys (if you don't have them):
     ```bash
     ssh-keygen -t rsa -b 4096 -f oracle_cloud_key
     ```
   - Upload the **public key** (oracle_cloud_key.pub)
   - Save the **private key** (oracle_cloud_key) - you'll need this to connect

5. **Boot Volume**
   - Size: 50GB (more than enough)

6. Click **"Create"**

7. **Wait 2-3 minutes** for instance to provision

8. **Note the Public IP** (you'll need this)

---

## Step 3: Configure Firewall

1. **In Oracle Cloud Console**:
   - Go to: Networking → Virtual Cloud Networks
   - Click your VCN
   - Click "Security Lists"
   - Click "Default Security List"
   - Click "Add Ingress Rules"

2. **Add Rule for SSH**:
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `22`
   - Description: "SSH access"

3. **Add Rule for API** (optional, if you want to access the API):
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `5000`
   - Description: "Flask API"

---

## Step 4: Connect to Your Server

### On Windows (using PuTTY):

1. Download PuTTY: https://www.putty.org/

2. Convert private key to PuTTY format:
   - Open PuTTYgen
   - Load your private key
   - Save as `.ppk` file

3. Connect:
   - Host: Your public IP
   - Port: 22
   - Connection → SSH → Auth → Browse to your `.ppk` file
   - Click "Open"
   - Login as: `ubuntu`

### On Windows (using PowerShell):

```powershell
ssh -i oracle_cloud_key ubuntu@YOUR_PUBLIC_IP
```

### On Linux/Mac:

```bash
chmod 600 oracle_cloud_key
ssh -i oracle_cloud_key ubuntu@YOUR_PUBLIC_IP
```

---

## Step 5: Install Dependencies

Once connected to your server:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3-pip python3.11-venv -y

# Install Playwright dependencies
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Install Git
sudo apt install git -y
```

---

## Step 6: Deploy Your Project

```bash
# Clone your repository
git clone https://github.com/Tee-David/realtors_practice.git
cd realtors_practice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## Step 7: Upload Firebase Credentials

**Option A: Direct Upload (SCP)**

From your local machine:

```bash
scp -i oracle_cloud_key realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json ubuntu@YOUR_PUBLIC_IP:~/realtors_practice/
```

**Option B: Manual Copy**

1. On your local machine, open the JSON file
2. Copy its contents
3. On the server:
   ```bash
   nano realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
   ```
4. Paste the contents
5. Press `Ctrl+X`, then `Y`, then `Enter` to save

---

## Step 8: Configure Environment

```bash
# Create .env file
nano .env
```

Add:
```
FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
FIRESTORE_ENABLED=1
RP_GEOCODE=1
RP_PAGE_CAP=20
RP_HEADLESS=1
RP_NO_AUTO_WATCHER=1
```

Save: `Ctrl+X`, `Y`, `Enter`

---

## Step 9: Test the Scraper

```bash
# Run a test scrape (1 site, 1 page)
python scripts/enable_one_site.py npc
python main.py
```

If successful, you should see:
- Properties scraped
- Firestore uploads confirmed

---

## Step 10: Set Up Automated Daily Scraping

### Option A: Cron Job (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM UTC):
0 2 * * * cd /home/ubuntu/realtors_practice && /home/ubuntu/realtors_practice/venv/bin/python main.py >> /home/ubuntu/scraper.log 2>&1

# Save and exit
```

### Option B: Systemd Service (Advanced)

Create service file:
```bash
sudo nano /etc/systemd/system/realestate-scraper.service
```

Add:
```ini
[Unit]
Description=Real Estate Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/realtors_practice
Environment="FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json"
Environment="FIRESTORE_ENABLED=1"
Environment="RP_GEOCODE=1"
Environment="RP_PAGE_CAP=20"
Environment="RP_HEADLESS=1"
ExecStart=/home/ubuntu/realtors_practice/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable realestate-scraper.timer
sudo systemctl start realestate-scraper.timer
```

---

## Step 11: Monitor the Scraper

### View Logs:

```bash
# Cron job logs
tail -f ~/scraper.log

# Systemd service logs
sudo journalctl -u realestate-scraper -f
```

### Check Firestore:

From your local machine:
```bash
python verify_full_scrape.py
```

Or visit Firebase Console:
https://console.firebase.google.com/project/realtor-s-practice/firestore

---

## Optional: Run API Server

If you want to expose the API:

```bash
# Run API server in background
nohup python api_server.py > api.log 2>&1 &

# Access API at:
http://YOUR_PUBLIC_IP:5000/api/health
```

**Better: Use systemd service**:

```bash
sudo nano /etc/systemd/system/realestate-api.service
```

Add:
```ini
[Unit]
Description=Real Estate API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/realtors_practice
Environment="FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json"
ExecStart=/home/ubuntu/realtors_practice/venv/bin/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable realestate-api
sudo systemctl start realestate-api
```

---

## Troubleshooting

### Issue: Out of Memory

**Solution**: Enable swap

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Issue: Playwright Crashes

**Solution**: Run in headless mode (already configured)

Make sure `RP_HEADLESS=1` is set

### Issue: Can't Connect via SSH

**Solution**: Check security rules

1. Go to Oracle Cloud Console
2. Networking → Security Lists
3. Ensure port 22 is open

### Issue: Scraper Stops

**Solution**: Use systemd service instead of cron

Systemd automatically restarts on failure

---

## Cost Monitoring

Even though the always-free tier is free, monitor your usage:

1. **Oracle Cloud Console** → Billing → Cost Analysis

2. **Set Up Budget Alerts**:
   - Go to Billing → Budgets
   - Create budget: $0.10
   - Get alerts if you accidentally use paid resources

---

## Updating the Scraper

```bash
# Connect to server
ssh -i oracle_cloud_key ubuntu@YOUR_PUBLIC_IP

# Navigate to project
cd realtors_practice

# Pull latest changes
git pull origin main

# Restart services
sudo systemctl restart realestate-scraper
sudo systemctl restart realestate-api  # if running
```

---

## Summary

Once set up, your scraper will:

- ✅ Run automatically daily at 2 AM
- ✅ Scrape all 51 sites
- ✅ Upload to Firestore in real-time
- ✅ Run 24/7 on cloud server
- ✅ Cost: $0.00 (free forever)
- ✅ No minute limits
- ✅ No manual intervention needed

---

## Quick Commands Reference

```bash
# Connect to server
ssh -i oracle_cloud_key ubuntu@YOUR_PUBLIC_IP

# View scraper logs
tail -f ~/scraper.log

# Manual scrape
cd ~/realtors_practice && source venv/bin/activate && python main.py

# Check cron jobs
crontab -l

# Restart API
sudo systemctl restart realestate-api

# Check system resources
htop
```

---

**Next Steps**: Follow steps 1-10 to get your scraper running on Oracle Cloud!

**Estimated Setup Time**: 30-45 minutes (one-time)

**Result**: Fully automated, always-online scraping with zero ongoing costs!
