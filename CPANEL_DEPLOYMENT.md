# cPanel Deployment Guide

Complete guide to run your Real Estate Scraper on cPanel hosting using cron jobs.

---

## Prerequisites

Your cPanel hosting must have:
- ✅ **Python 3.7+** (most cPanel hosts have this)
- ✅ **SSH access** (for initial setup)
- ✅ **Cron jobs** (standard cPanel feature)
- ✅ **Sufficient storage** (at least 2GB recommended)
- ✅ **Sufficient RAM** (at least 512MB, 1GB+ recommended)

**Popular cPanel Hosts with Python Support:**
- Hostinger (supports Python, affordable)
- A2 Hosting (good Python support)
- InMotion Hosting (Python friendly)
- SiteGround (limited Python support)
- Bluehost (basic Python support)

---

## Step 1: Check Python Availability

1. **Login to cPanel**

2. **Open Terminal** (or use SSH)

3. **Check Python version:**
   ```bash
   python3 --version
   ```

   Should show Python 3.7 or higher.

4. **Check pip:**
   ```bash
   pip3 --version
   ```

---

## Step 2: Upload Project Files

### Option A: Git Clone (Recommended)

```bash
# SSH into your cPanel account
ssh username@yourdomain.com

# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/Tee-David/realtors_practice.git
cd realtors_practice
```

### Option B: File Manager Upload

1. **Compress project locally:**
   - Zip the entire `realtors_practice` folder

2. **Upload via cPanel File Manager:**
   - cPanel → File Manager
   - Navigate to `/home/username/`
   - Upload the zip file
   - Extract it

---

## Step 3: Install Dependencies

```bash
# Navigate to project
cd ~/realtors_practice

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright (if hosting allows)
playwright install chromium
```

**Note**: Some cPanel hosts don't allow Playwright browsers. If this fails, see "Headless Browser Alternatives" below.

---

## Step 4: Upload Firebase Credentials

### Option A: SCP (from your computer)

```bash
scp realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json username@yourdomain.com:~/realtors_practice/
```

### Option B: cPanel File Manager

1. cPanel → File Manager
2. Navigate to `realtors_practice` folder
3. Click "Upload"
4. Upload `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json`

### Option C: Nano Editor (via SSH)

```bash
cd ~/realtors_practice
nano realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
# Paste the JSON content
# Ctrl+X, Y, Enter to save
```

---

## Step 5: Create Wrapper Script

Create a script that cPanel cron will execute:

```bash
cd ~/realtors_practice
nano run_scraper.sh
```

Add this content:

```bash
#!/bin/bash

# Set paths
PROJECT_DIR="/home/USERNAME/realtors_practice"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
LOG_FILE="$PROJECT_DIR/logs/cron_scraper.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Navigate to project
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Set environment variables
export FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json"
export FIRESTORE_ENABLED=1
export RP_GEOCODE=1
export RP_PAGE_CAP=20
export RP_HEADLESS=1
export RP_NO_AUTO_WATCHER=1

# Log start time
echo "================================" >> "$LOG_FILE"
echo "Scrape started: $(date)" >> "$LOG_FILE"
echo "================================" >> "$LOG_FILE"

# Run scraper
$PYTHON main.py >> "$LOG_FILE" 2>&1

# Log completion
echo "Scrape completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Deactivate virtual environment
deactivate
```

**Important**: Replace `USERNAME` with your actual cPanel username!

Save: `Ctrl+X`, `Y`, `Enter`

Make it executable:
```bash
chmod +x run_scraper.sh
```

---

## Step 6: Set Up Cron Job

### Method A: cPanel Cron Jobs Interface (Easier)

1. **Login to cPanel**

2. **Go to**: Advanced → Cron Jobs

3. **Common Settings**: Select frequency
   - Daily (2:00 AM recommended)

4. **Command**:
   ```bash
   /home/USERNAME/realtors_practice/run_scraper.sh
   ```

   Replace `USERNAME` with your cPanel username!

5. **Click "Add New Cron Job"**

### Method B: Advanced Cron Syntax

If you want more control:

```bash
# Daily at 2:00 AM
0 2 * * * /home/USERNAME/realtors_practice/run_scraper.sh

# Every 6 hours
0 */6 * * * /home/USERNAME/realtors_practice/run_scraper.sh

# Every Monday at 3:00 AM
0 3 * * 1 /home/USERNAME/realtors_practice/run_scraper.sh

# Twice daily (2 AM and 2 PM)
0 2,14 * * * /home/USERNAME/realtors_practice/run_scraper.sh
```

**Cron Syntax:**
```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-6, Sunday=0)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

---

## Step 7: Configure Email Notifications (Optional)

cPanel sends cron output via email by default.

### To receive notifications:

Add to the **top** of your crontab:
```bash
MAILTO="your-email@example.com"
```

### To disable emails:

Add to the **top** of your crontab:
```bash
MAILTO=""
```

Or redirect output in the cron command:
```bash
0 2 * * * /home/USERNAME/realtors_practice/run_scraper.sh > /dev/null 2>&1
```

---

## Step 8: Test the Setup

### Manual Test (via SSH):

```bash
cd ~/realtors_practice
./run_scraper.sh
```

Watch for:
- ✅ Script executes without errors
- ✅ Properties are scraped
- ✅ Firestore uploads confirmed
- ✅ Log file created

### Check Logs:

```bash
tail -f ~/realtors_practice/logs/cron_scraper.log
```

---

## Important: Headless Browser on cPanel

### Issue: Playwright May Not Work

Some cPanel hosts block Playwright/Chromium for security reasons.

### Solutions:

#### Solution 1: Use Requests-Only Mode

Modify `config.yaml`:
```yaml
fallback_order:
  - requests  # Remove playwright from fallback chain
```

Many sites work fine with just `requests`.

#### Solution 2: Use Selenium with Chrome Binary

If Playwright fails, install Selenium:

```bash
pip install selenium
```

Update `config.yaml`:
```yaml
browser:
  use_selenium: true  # Add this option
```

#### Solution 3: Contact Host Support

Ask if they support:
- Playwright browsers
- Chrome/Chromium installation
- Increased resource limits

#### Solution 4: Hybrid Approach

- Use cPanel cron for **scheduling** only
- Trigger a webhook on your local machine
- Local machine does the actual scraping

---

## Monitoring

### View Recent Cron Executions:

```bash
# View cron log
cat ~/realtors_practice/logs/cron_scraper.log

# View last 50 lines
tail -50 ~/realtors_practice/logs/cron_scraper.log

# Watch live (if running)
tail -f ~/realtors_practice/logs/cron_scraper.log
```

### Check Firestore:

From your local machine:
```bash
python verify_full_scrape.py
```

Or Firebase Console:
https://console.firebase.google.com/project/realtor-s-practice/firestore

---

## Resource Management

### Issue: Script Times Out

cPanel hosts often have execution time limits (30-300 seconds).

**Solutions:**

1. **Enable only essential sites** (reduce from 51 to 10-20)
2. **Reduce pages per site** (`RP_PAGE_CAP=5`)
3. **Split into multiple cron jobs**:

```bash
# Job 1: Sites 1-17 (2 AM)
0 2 * * * /home/USERNAME/realtors_practice/run_scraper_batch1.sh

# Job 2: Sites 18-34 (3 AM)
0 3 * * * /home/USERNAME/realtors_practice/run_scraper_batch2.sh

# Job 3: Sites 35-51 (4 AM)
0 4 * * * /home/USERNAME/realtors_practice/run_scraper_batch3.sh
```

4. **Use `nohup`** to run in background:

```bash
nohup /home/USERNAME/realtors_practice/run_scraper.sh &
```

### Issue: Out of Memory

Modify `run_scraper.sh` to limit sites:

```bash
# Enable only high-priority sites
export RP_SITES="npc,jiji,propertypro,lamudi"
```

---

## Advanced: Split Scraping Across Multiple Cron Jobs

Create 3 scripts for batching:

### run_scraper_batch1.sh
```bash
#!/bin/bash
# ... (same setup as run_scraper.sh)

# Enable only batch 1 sites
python scripts/enable_sites.py adronhomes ashproperties brokerfield buyletlive castles cuddlerealty cwlagos edenoasis estateintel facibus giddaa gtexthomes houseafrica hutbay jaat_properties jiji lagosproperty lamudi

$PYTHON main.py >> "$LOG_FILE" 2>&1
```

### run_scraper_batch2.sh
```bash
#!/bin/bash
# Enable batch 2 sites
python scripts/enable_sites.py landmall landng lodges myproperty naijahouses naijalandlord nazaprimehive nigerianpropertymarket nigeriapropertyzone npc olist oparahrealty ownahome privateproperty pwanhomes propertieslinkng property24 propertyguru

$PYTHON main.py >> "$LOG_FILE" 2>&1
```

### run_scraper_batch3.sh
```bash
#!/bin/bash
# Enable batch 3 sites
python scripts/enable_sites.py propertylisthub propertypro quicktellerhomes ramos realestatenigeria realtorintl realtorng rentsmallsmall spleet takooka_props thinkmint tradebanq trovit ubosieleh vconnect

$PYTHON main.py >> "$LOG_FILE" 2>&1
```

**Cron jobs:**
```bash
0 2 * * * /home/USERNAME/realtors_practice/run_scraper_batch1.sh
0 3 * * * /home/USERNAME/realtors_practice/run_scraper_batch2.sh
0 4 * * * /home/USERNAME/realtors_practice/run_scraper_batch3.sh
```

---

## Troubleshooting

### Cron Job Not Running

**Check:**
1. File permissions: `chmod +x run_scraper.sh`
2. Shebang line: `#!/bin/bash` at top of script
3. Full absolute paths used (not relative)
4. cPanel user has permission

**Debug:**
```bash
# Check cron logs
grep CRON /var/log/syslog  # if accessible
```

### Python Command Not Found

**Fix**: Use full path to Python:

```bash
# Find Python location
which python3
# Output: /usr/bin/python3

# Use in script
/usr/bin/python3 main.py
```

### Permission Denied

```bash
chmod +x run_scraper.sh
chmod -R 755 ~/realtors_practice
```

### Import Errors

Virtual environment not activated correctly.

**Fix**: Ensure `source venv/bin/activate` is in script

---

## Cost Considerations

**cPanel Hosting Costs:**
- Shared hosting: $3-10/month
- VPS hosting: $10-30/month (more resources)

**Recommended Hosts for This Project:**
1. **Hostinger** - $2.99/mo, good Python support
2. **A2 Hosting** - $2.99/mo, developer-friendly
3. **InMotion** - $2.49/mo, good resources

---

## Comparison: cPanel vs Oracle Cloud

| Feature | cPanel | Oracle Cloud |
|---------|--------|--------------|
| **Cost** | $3-10/mo | **FREE forever** |
| **Setup** | Easy (GUI) | Medium (CLI) |
| **Resources** | Limited | 1GB RAM, 1 CPU |
| **Browser Support** | May be limited | Full Playwright |
| **Execution Time** | 30-300s limits | **Unlimited** |
| **Best For** | Simple scrapes | Heavy scraping |

**Recommendation**:
- **cPanel**: If you already have hosting
- **Oracle Cloud**: For new setup (more powerful, free)

---

## Quick Start Checklist

- [ ] Upload project files to cPanel
- [ ] Install Python dependencies
- [ ] Upload Firebase credentials
- [ ] Create `run_scraper.sh` script
- [ ] Make script executable (`chmod +x`)
- [ ] Test script manually
- [ ] Set up cron job in cPanel
- [ ] Wait for first scheduled run
- [ ] Check logs
- [ ] Verify Firestore uploads

---

## Summary

**Pros of cPanel:**
- ✅ Easy to use (GUI interface)
- ✅ No server management needed
- ✅ Email notifications built-in
- ✅ Works if you already have hosting

**Cons of cPanel:**
- ⚠️ Execution time limits (may need batching)
- ⚠️ Resource limits (RAM, CPU)
- ⚠️ May not support Playwright
- ⚠️ Monthly cost

**Best Use Case:**
- Small to medium scrapes (10-20 sites)
- 1-5 pages per site
- Sites that work with `requests` library
- Already have cPanel hosting

For heavy scraping (all 51 sites, 20 pages each), **Oracle Cloud Free Tier** is recommended.

---

**Next Steps**:
1. Follow steps 1-8 to deploy on cPanel
2. Test with a small subset of sites first
3. Expand gradually based on resource availability
