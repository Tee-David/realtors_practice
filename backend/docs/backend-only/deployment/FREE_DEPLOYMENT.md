# Free Deployment Options - No Cost Solutions

**💰 Cost: $0.00/month - Completely FREE!**

---

## 🎯 Best Free Options

### 1. ⭐ GitHub Actions (RECOMMENDED)
- ✅ **Completely FREE** (2000 minutes/month)
- ✅ **Scheduled scraping** (cron jobs)
- ✅ **No credit card required**
- ✅ **Easy setup** (15 minutes)
- ✅ **Automatic data storage** (GitHub artifacts or repo)
- ✅ **Best for**: Scheduled daily/weekly scraping

### 2. 🌐 Oracle Cloud Always Free
- ✅ **Completely FREE forever**
- ✅ **Generous limits** (VM with 1GB RAM)
- ✅ **No time limits**
- ✅ **Best for**: 24/7 scraping or API hosting
- ⚠️ Requires credit card (but won't charge)

### 3. 💻 Local Machine with Scheduler
- ✅ **Completely FREE**
- ✅ **Full control**
- ✅ **No setup complexity**
- ❌ Computer must stay on
- ✅ **Best for**: Development and testing

### 4. 🚀 Railway.app Free Tier
- ✅ **$5 free credit/month**
- ✅ **Easy deployment**
- ⚠️ Limited to ~500 hours/month
- ✅ **Best for**: Light usage

### 5. 📦 Render.com Free Tier
- ✅ **Completely FREE**
- ⚠️ Web services sleep after inactivity
- ⚠️ 750 hours/month limit
- ✅ **Best for**: API hosting with occasional scraping

---

## 🏆 Option 1: GitHub Actions (RECOMMENDED)

### Why GitHub Actions?

**Perfect for this scraper because**:
- ✅ Runs on schedule (daily, weekly, etc.)
- ✅ 2000 free minutes/month (enough for 100+ scraping runs)
- ✅ Stores data in GitHub (git commits or artifacts)
- ✅ No server needed
- ✅ No credit card needed
- ✅ Built-in logging

### Setup Time: 15 minutes

### How It Works

```
1. Push your code to GitHub
2. Create workflow file (.github/workflows/scrape-production.yml)
3. GitHub runs scraper on schedule
4. Exports saved to GitHub repo or artifacts
5. Download data anytime from GitHub
```

### Step-by-Step Setup

#### Step 1: Create GitHub Repository

```bash
# If you don't have git initialized
cd C:\Users\DELL\Desktop\Dynamic realtors_practice
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/realtors_practice.git
git branch -M main
git push -u origin main
```

#### Step 2: Create Workflow File

Create `.github/workflows/scrape-production.yml`:

```yaml
name: Daily Property Scraper

on:
  # Run daily at 3 AM UTC
  schedule:
    - cron: '0 3 * * *'

  # Allow manual trigger
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          # Install playwright browser
          playwright install chromium
          # Install system dependencies for playwright
          playwright install-deps

      - name: Run scraper
        env:
          RP_HEADLESS: 1
          RP_GEOCODE: 1
          RP_PAGE_CAP: 20
        run: |
          python main.py

      - name: Process exports with watcher
        run: |
          python watcher.py --once

      - name: Upload exports as artifacts
        uses: actions/upload-artifact@v3
        with:
          name: scraper-exports-${{ github.run_number }}
          path: |
            exports/sites/
            exports/cleaned/
          retention-days: 30

      - name: Commit and push data to repo (optional)
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add exports/cleaned/
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto: Update scraped data $(date '+%Y-%m-%d')"
          git push
```

#### Step 3: Configure Sites

Edit `config.yaml` to enable only the sites you want:

```yaml
sites:
  npc:
    enabled: true
  propertypro:
    enabled: true
  jiji:
    enabled: true
  # ... disable others or keep as needed
```

#### Step 4: Test Workflow

1. **Push workflow file**:
   ```bash
   git add .github/workflows/scrape-production.yml
   git commit -m "Add GitHub Actions workflow"
   git push
   ```

2. **Manual trigger** (to test before waiting for schedule):
   - Go to your GitHub repo
   - Click **"Actions"** tab
   - Select **"Daily Property Scraper"**
   - Click **"Run workflow"** → **"Run workflow"**
   - Wait 5-10 minutes for completion

3. **Check results**:
   - Click on the workflow run
   - See logs in each step
   - Download artifacts (exported data)

#### Step 5: Download Scraped Data

**Option A: Download Artifacts**
1. Go to **Actions** tab
2. Click on completed workflow run
3. Scroll down to **Artifacts**
4. Download `scraper-exports-XX.zip`
5. Extract to see your data

**Option B: Pull from Git** (if you enabled commit step)
```bash
git pull
# Data will be in exports/cleaned/
```

### GitHub Actions Limitations

- **2000 minutes/month free** (enough for ~100 runs at 20 min each)
- **Storage**: 500MB for artifacts (on free plan)
- **Concurrency**: 20 concurrent jobs
- **Artifact retention**: 30 days (configurable)

**Optimizations**:
- Set `RP_PAGE_CAP=15` to reduce run time
- Enable only 5-10 sites instead of all 50
- Run weekly instead of daily to save minutes

### Cost Calculation

**Example Usage**:
- 1 scrape/day × 30 days = 30 scrapes
- 20 minutes per scrape × 30 = 600 minutes
- **FREE** (well under 2000 minute limit)

---

## 🌐 Option 2: Oracle Cloud Always Free

### Why Oracle Cloud?

- ✅ **Forever FREE** (not a trial)
- ✅ **Generous resources** (1-4 ARM CPUs, 6-24GB RAM)
- ✅ **No time limits**
- ✅ **Can run 24/7**
- ⚠️ Requires credit card verification (but never charges)

### What You Get Free

- 2 AMD Compute VMs (1/8 OCPU, 1GB RAM each) OR
- 4 ARM Ampere A1 cores, 24GB RAM (shared across instances)
- 200GB block storage
- 10TB outbound data transfer/month

### Setup Time: 30-60 minutes

### Step-by-Step Setup

#### Step 1: Create Oracle Cloud Account

1. Go to https://www.oracle.com/cloud/free/
2. Click **"Start for free"**
3. Fill in details:
   - Email address
   - Country
   - Cloud account name (choose unique name)
4. **Credit card verification** (required, but won't be charged)
5. Verify email
6. Wait for account activation (~5 minutes)

#### Step 2: Create VM Instance

1. **Login to Oracle Cloud Console**
2. **Click "Create a VM instance"**
3. **Configure**:
   - **Name**: `scraper-vm`
   - **Placement**: Choose availability domain
   - **Image**: Ubuntu 22.04
   - **Shape**:
     - Click "Change shape"
     - Select "Ampere" (ARM)
     - OCPU: 1-4 (free)
     - Memory: 6-24GB (free)
   - **Networking**: Use default VCN
   - **SSH keys**:
     - Download private key (keep safe!)
     - Or upload your public key

4. **Click "Create"**

5. **Note the public IP address** (e.g., 129.xxx.xxx.xxx)

#### Step 3: Connect via SSH

**Windows** (using PuTTY):
1. Download PuTTY: https://www.putty.org/
2. Open PuTTY
3. Host: `ubuntu@YOUR_PUBLIC_IP`
4. Auth: Load your private key (.ppk format)
5. Click "Open"

**Mac/Linux**:
```bash
ssh -i path/to/private-key ubuntu@YOUR_PUBLIC_IP
```

#### Step 4: Setup Scraper

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip git -y

# Clone your project
git clone https://github.com/YOUR_USERNAME/realtors_practice.git
cd realtors_practice

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install playwright
playwright install chromium
playwright install-deps

# Configure
cp config.example.yaml config.yaml
nano config.yaml  # Edit as needed
```

#### Step 5: Schedule with Cron

```bash
# Create run script
nano ~/run_scraper.sh
```

Paste:
```bash
#!/bin/bash
cd /home/ubuntu/realtors_practice
source venv/bin/activate
export RP_HEADLESS=1
export RP_GEOCODE=1
export RP_PAGE_CAP=20
python main.py >> logs/cron.log 2>&1
python watcher.py --once >> logs/cron.log 2>&1
```

Make executable:
```bash
chmod +x ~/run_scraper.sh
```

Add to crontab:
```bash
crontab -e

# Add this line (daily at 3 AM):
0 3 * * * /home/ubuntu/run_scraper.sh
```

#### Step 6: Download Data

**Option A: SCP (Mac/Linux)**
```bash
scp -i private-key ubuntu@YOUR_IP:~/realtors_practice/exports/cleaned/* ./local-folder/
```

**Option B: WinSCP (Windows)**
1. Download WinSCP: https://winscp.net/
2. Connect using IP and private key
3. Navigate to `realtors_practice/exports/cleaned/`
4. Download files

**Option C: Git (if you commit to GitHub)**
```bash
# On VM, after scraping
cd ~/realtors_practice
git add exports/cleaned/
git commit -m "Update data"
git push

# On local machine
git pull
```

### Oracle Cloud Tips

**Keep Instance Active**:
- Oracle may reclaim inactive instances
- Run a simple script to prevent this:
  ```bash
  # Add to crontab (runs every hour)
  0 * * * * echo "keepalive $(date)" >> /home/ubuntu/keepalive.log
  ```

**Firewall** (if you want to host API):
```bash
# Allow HTTP/HTTPS
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

---

## 💻 Option 3: Local Machine with Scheduler

### Windows Task Scheduler

#### Step 1: Create Batch Script

Create `run_scraper.bat`:

```batch
@echo off
cd C:\Users\DELL\Desktop\Dynamic realtors_practice
call venv\Scripts\activate.bat
set RP_HEADLESS=1
set RP_GEOCODE=1
set RP_PAGE_CAP=20
python main.py >> logs\cron.log 2>&1
python watcher.py --once >> logs\cron.log 2>&1
```

#### Step 2: Open Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc`
3. Click **OK**

#### Step 3: Create Task

1. **Click "Create Basic Task"**
2. **Name**: "Daily Property Scraper"
3. **Trigger**: Daily
4. **Time**: 3:00 AM
5. **Action**: Start a program
6. **Program**: `C:\Users\DELL\Desktop\Dynamic realtors_practice\run_scraper.bat`
7. **Finish**

#### Step 4: Test

Right-click task → **Run**

Check `logs\cron.log` for output.

### Mac/Linux Cron

```bash
# Edit crontab
crontab -e

# Add (daily at 3 AM)
0 3 * * * cd ~/Desktop/Dynamic\ realtors_practice && source venv/bin/activate && python main.py && python watcher.py --once >> logs/cron.log 2>&1
```

### Pros & Cons

**Pros**:
- ✅ Completely free
- ✅ Full control
- ✅ Fast (local machine)

**Cons**:
- ❌ Computer must stay on
- ❌ No remote access (unless you set up)
- ❌ Power consumption

---

## 🚀 Option 4: Railway.app Free Tier

### What You Get

- **$5 free credit/month**
- **~500 execution hours/month**
- **512MB RAM**
- **Credit card not required**

### Setup (Quick)

1. **Go to** https://railway.app/
2. **Sign up** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your `realtors_practice` repo
5. **Add** `Procfile`:
   ```
   web: python api_server.py
   worker: python main.py && python watcher.py --once
   ```
6. **Add** cron service (Railway Cron plugin)
7. **Deploy**

**Limitation**: $5 credit runs out if you scrape too frequently.

---

## 📦 Option 5: Render.com Free Tier

### What You Get

- **750 hours/month free**
- **Cron jobs** (scheduled)
- **512MB RAM**

### Setup

1. **Go to** https://render.com/
2. **Sign up** with GitHub
3. **New** → **Cron Job**
4. **Connect** your repo
5. **Schedule**: `0 3 * * *` (daily 3 AM)
6. **Command**: `python main.py && python watcher.py --once`
7. **Deploy**

**Limitation**: Web services sleep after 15 min inactivity.

---

## 📊 Comparison Table

| Option | Cost | Setup Time | Best For | Limitations |
|--------|------|------------|----------|-------------|
| **GitHub Actions** | $0 | 15 min | Scheduled scraping | 2000 min/month |
| **Oracle Cloud** | $0 | 60 min | 24/7 scraping, API | Requires card verification |
| **Local Machine** | $0 | 5 min | Development, testing | PC must stay on |
| **Railway.app** | $0 | 30 min | Light usage | $5 credit limit |
| **Render.com** | $0 | 20 min | Occasional scraping | Services sleep |

---

## 🏆 Recommendation

### For You (No Cost, No cPanel)

**Best Choice: GitHub Actions**

**Why?**
1. ✅ Completely free (no credit card)
2. ✅ Easy setup (15 minutes)
3. ✅ Scheduled scraping (cron)
4. ✅ Reliable (GitHub infrastructure)
5. ✅ Data stored in GitHub (artifacts or commits)
6. ✅ Perfect for daily/weekly scraping

**Second Choice: Oracle Cloud Always Free**
- If you want 24/7 availability
- If you want to host the API too
- More powerful than GitHub Actions
- Requires credit card verification (but never charges)

**Third Choice: Local Machine**
- If you're just testing
- If your computer is always on anyway
- Easiest setup

---

## 🚀 Quick Start (GitHub Actions)

```bash
# 1. Create GitHub repo (if not done)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/realtors_practice.git
git push -u origin main

# 2. Create workflow directory
mkdir -p .github/workflows

# 3. Create workflow file
# (Copy the YAML from Option 1 above to .github/workflows/scrape-production.yml)

# 4. Push workflow
git add .github/workflows/scrape-production.yml
git commit -m "Add scraping workflow"
git push

# 5. Go to GitHub → Actions → Run workflow manually to test

# 6. Done! Scraper runs daily at 3 AM UTC automatically
```

---

## 💡 Cost Optimization Tips

### Reduce GitHub Actions Minutes

```yaml
# config.yaml
global_settings:
  pagination:
    max_pages: 10  # Instead of 30
```

Enable fewer sites:
```bash
python scripts/enable_sites.py npc propertypro jiji
# Only enable 3-5 high-priority sites
```

Run less frequently:
```yaml
# In .github/workflows/scrape-production.yml
schedule:
  - cron: '0 3 * * 0'  # Weekly (Sunday) instead of daily
```

---

## 📞 Need Help?

**GitHub Actions**:
- Docs: https://docs.github.com/en/actions
- Community: https://github.community/

**Oracle Cloud**:
- Docs: https://docs.oracle.com/en-us/iaas/
- Forums: https://community.oracle.com/

**General**:
- Check project docs in `docs/` folder
- Search Stack Overflow
- Open GitHub issue

---

## ✅ Summary

**You have 5 free options**:

1. ⭐ **GitHub Actions** - Best for scheduled scraping (RECOMMENDED)
2. 🌐 **Oracle Cloud** - Best for 24/7 availability
3. 💻 **Local Machine** - Best for testing
4. 🚀 **Railway.app** - Easy but limited
5. 📦 **Render.com** - Good for occasional use

**Start with GitHub Actions** - It's the easiest free option with no credit card required!

---

**Cost**: $0.00/month
**Setup**: 15-60 minutes depending on option
**Status**: Ready to deploy for FREE! 🎉
