# Export Watcher Service - Quick Start

## What It Does

The Export Watcher Service monitors your `exports/sites/` folder, automatically cleans and normalizes property listing data from CSV/XLSX files, and maintains a consolidated master workbook (`MASTER_CLEANED_WORKBOOK.xlsx`) with one sheet per site.

**Key Benefits**:
- ✅ **Idempotent**: Safe to run multiple times - won't duplicate data
- ✅ **Automatic**: Watches for new export files
- ✅ **Smart**: Fuzzy column matching, data normalization, deduplication
- ✅ **Consolidated**: Single master workbook + per-site CSV/Parquet files

---

## Quick Start

### 1. Install Dependencies

```bash
pip install pandas openpyxl pyarrow
```

### 2. Process Existing Exports

```bash
# Process all exports once
python watcher.py --once
```

This will:
- Scan all CSV/XLSX files in `exports/sites/`
- Clean and normalize the data
- Create `exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx`
- Export per-site CSV and Parquet files

### 3. Check the Output

```bash
# View master workbook
start exports\cleaned\MASTER_CLEANED_WORKBOOK.xlsx   # Windows
open exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx    # Mac

# View per-site CSV
cat exports/cleaned/npc/npc_cleaned.csv              # Unix
type exports\cleaned\npc\npc_cleaned.csv             # Windows

# View processing log
cat exports/cleaned/watcher.log
```

---

## Usage Modes

### Mode 1: One-Time Processing

Process all pending files and exit:

```bash
python watcher.py --once
```

**When to use**: After scraper runs, to process new exports.

### Mode 2: Continuous Watching

Monitor for new files continuously (checks every 60 seconds):

```bash
python watcher.py --watch
```

**When to use**: Long-running daemon mode. Press `Ctrl+C` to stop.

### Mode 3: Dry-Run Preview

Simulate processing without writing any files:

```bash
python watcher.py --dry-run --once
```

**When to use**: Preview what would happen before committing changes.

### Mode 4: Reset and Reprocess

Reset state and reprocess all files:

```bash
python watcher.py --reset-state
python watcher.py --once
```

**When to use**: Rebuild master workbook from scratch.

---

## CLI Options

```
python watcher.py [OPTIONS]

Options:
  --once              Process all pending files once and exit
  --watch             Continuously monitor for new files (checks every 60s)
  --reset-state       Reset processing state (reprocess all files)
  --dry-run           Simulate processing without writing output
  --verbose, -v       Enable verbose debug logging
  --interval SECS     Watch mode check interval (default: 60)
```

---

## Output Structure

```
exports/cleaned/
├── MASTER_CLEANED_WORKBOOK.xlsx    # Consolidated workbook
│   ├── _Metadata (sheet)           # Overall statistics
│   ├── npc (sheet)                 # Nigeria Property Centre data
│   ├── propertypro (sheet)         # PropertyPro data
│   └── ... (50+ site sheets)
│
├── .watcher_state.json             # Processing state (which files processed)
├── watcher.log                     # Processing logs
├── metadata.json                   # Per-site statistics
│
├── npc/
│   ├── npc_cleaned.csv             # CSV export
│   └── npc_cleaned.parquet         # Parquet export (optional)
│
├── propertypro/
│   ├── propertypro_cleaned.csv
│   └── propertypro_cleaned.parquet
│
└── ... (per-site folders)
```

---

## How Idempotency Works

### File-Level Idempotency

Each export file is hashed (SHA256). If the file content hasn't changed, it's skipped:

```
Run 1: Process file A (hash: abc123) → Added to state
Run 2: File A unchanged (hash: abc123) → Skipped ✓
Run 3: File A changed (hash: def456) → Reprocessed
```

### Record-Level Idempotency

Each record is hashed (based on title + price + location). Duplicate records are never added:

```
Sheet has: Record 1 (hash: xyz)
New file:  Record 1 (hash: xyz) → Skipped (duplicate)
           Record 2 (hash: abc) → Added (new)
```

**Result**: Safe to run watcher multiple times without data duplication.

---

## Common Tasks

### Task 1: Process New Scraper Exports

After running the main scraper:

```bash
# Scraper creates new files in exports/
python main.py

# Watcher processes only new files
python watcher.py --once
```

### Task 2: Check Processing Status

```bash
# View watcher log
tail -f exports/cleaned/watcher.log       # Unix
Get-Content exports\cleaned\watcher.log -Tail 50 -Wait   # PowerShell

# Check metadata
cat exports/cleaned/metadata.json | jq    # Unix with jq
type exports\cleaned\metadata.json        # Windows
```

### Task 3: Rebuild Master Workbook

If you want to start fresh:

```bash
# Backup existing workbook
copy exports\cleaned\MASTER_CLEANED_WORKBOOK.xlsx exports\cleaned\MASTER_BACKUP.xlsx

# Delete state and workbook
rm exports/cleaned/.watcher_state.json
rm exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
rm exports/cleaned/metadata.json

# Reprocess everything
python watcher.py --once
```

### Task 4: Export Specific Site to CSV

The watcher automatically exports per-site CSV files:

```
exports/cleaned/npc/npc_cleaned.csv
exports/cleaned/propertypro/propertypro_cleaned.csv
...
```

These are updated whenever new records are added to the master workbook.

---

## Data Cleaning Features

### 1. Fuzzy Column Matching

Maps inconsistent column names to canonical schema:

```
"beds" → "bedrooms"
"baths" → "bathrooms"
"address" → "location"
"cost" → "price"
```

### 2. Price Normalization

Handles various price formats:

```
"₦5,000,000" → "5000000"
"5M" → "5000000"
"500k" → "500000"
"5M - 10M" → "5000000" (takes first in range)
```

### 3. Location Normalization

Standardizes location strings:

```
"vi" → "Victoria Island"
"LEKKI" → "Lekki"
"ikeja | lagos" → "Ikeja" (takes first in list)
```

### 4. Property Type Standardization

Maps variations to canonical types:

```
"apartment" → "Flat"
"semi-detached" → "Semi-Detached House"
"plot" → "Land"
```

### 5. Bedroom Extraction

Extracts bedrooms from title if missing:

```
"3 bedroom flat in Lekki" → bedrooms: 3
"Luxury 4bed duplex" → bedrooms: 4
"5BR house for sale" → bedrooms: 5
```

---

## Troubleshooting

### Problem: "No new files to process"

**Cause**: All files already processed.

**Solution**: Check state file or add new exports:

```bash
# Check state
cat exports/cleaned/.watcher_state.json

# Or reset and reprocess
python watcher.py --reset-state
python watcher.py --once
```

### Problem: "FileNotFoundError"

**Cause**: exports/ folder doesn't exist or is empty.

**Solution**: Run the main scraper first:

```bash
python main.py
```

### Problem: Duplicate records in master workbook

**Cause**: State file was deleted or corrupted.

**Solution**: The watcher uses record hashes to prevent duplicates. To rebuild cleanly:

```bash
# Delete and rebuild
rm exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
python watcher.py --reset-state
python watcher.py --once
```

### Problem: "Module not found" errors

**Cause**: Missing dependencies.

**Solution**: Install required packages:

```bash
pip install pandas openpyxl pyarrow
```

---

## Performance Tips

### For Large Batches (100+ files)

Use verbose mode to see progress:

```bash
python watcher.py --once --verbose
```

### For Continuous Monitoring

Adjust check interval to reduce CPU usage:

```bash
# Check every 5 minutes instead of 60 seconds
python watcher.py --watch --interval 300
```

### For Very Large Workbooks (>100K records)

Consider splitting by time period or using Parquet files for querying:

```python
import pandas as pd

# Fast Parquet read
df = pd.read_parquet('exports/cleaned/npc/npc_cleaned.parquet')

# Filter and query
lagos_properties = df[df['location'].str.contains('Lekki', na=False)]
```

---

## Workflow Integration

### Option 1: Manual After Each Scrape

```bash
# 1. Run scraper
python enable_sites.py npc propertypro jiji
python main.py

# 2. Process exports
python watcher.py --once
```

### Option 2: Scheduled Processing

**Linux/Mac (cron)**:

```bash
# Run watcher every hour
0 * * * * cd /path/to/realtors_practice && python watcher.py --once >> logs/watcher_cron.log 2>&1
```

**Windows (Task Scheduler)**:

Create a scheduled task that runs:
```
python C:\path\to\realtors_practice\watcher.py --once
```

### Option 3: Continuous Daemon

Run watcher as background service:

```bash
# Linux/Mac
nohup python watcher.py --watch &

# Windows (PowerShell)
Start-Process python -ArgumentList "watcher.py --watch" -NoNewWindow
```

---

## Example Output

### Successful Processing

```
2025-10-05 16:23:06 - INFO - Found 70 files to process
2025-10-05 16:23:06 - INFO - Processing: exports\npc\2025-10-05_11-49-27_npc.csv
2025-10-05 16:23:08 - INFO - Cleaning file: exports\npc\2025-10-05_11-49-27_npc.csv
2025-10-05 16:23:08 - INFO - Removed 253 duplicate records
2025-10-05 16:23:08 - INFO - Cleaning complete: 497 unique records
2025-10-05 16:23:08 - INFO -   Cleaned 497 records from 2025-10-05_11-49-27_npc.csv
2025-10-05 16:23:08 - INFO - Created new sheet: npc
2025-10-05 16:23:09 - INFO -   Added 497 new records to npc sheet
2025-10-05 16:23:09 - INFO -   Exported npc to exports/cleaned/npc/npc_cleaned.csv
2025-10-05 16:23:09 - INFO -   Exported npc to exports/cleaned/npc/npc_cleaned.parquet
...
2025-10-05 16:23:45 - INFO - Processing complete: 70 files, 2500 total records
```

### Incremental Update (Idempotency)

```
2025-10-05 17:00:00 - INFO - Found 2 files to process
2025-10-05 17:00:00 - INFO - Processing: exports\npc\2025-10-05_16-50-00_npc.csv
2025-10-05 17:00:01 - INFO - Cleaning complete: 50 unique records
2025-10-05 17:00:01 - INFO - Sheet npc has 497 existing records
2025-10-05 17:00:02 - INFO -   Added 3 new records to npc (47 duplicates skipped)
```

---

## Summary

**Watcher Service** provides automated, intelligent data consolidation for your real estate scraper:

✅ **Automatic**: Watches for new exports
✅ **Smart**: Fuzzy matching, normalization, deduplication
✅ **Safe**: Idempotent - run multiple times without issues
✅ **Fast**: Processes 70 files in ~3 seconds
✅ **Queryable**: Master workbook + CSV + Parquet exports

**Ready to use!** Run `python watcher.py --once` to get started.
