# Workflow Investigation Report
**Date**: 2025-12-15
**Issue**: Frontend API triggers not working properly + Firestore upload failures

---

## 🔍 ROOT CAUSE IDENTIFIED

### **Problem Statement**
When triggering scrapes from the frontend API with specific sites (e.g., 5 sites), the GitHub workflow:
1. **Ignores the custom sites** and scrapes ALL 51 enabled sites instead
2. Creates 17 parallel sessions (instead of 2 sessions for 5 sites)
3. Sessions timeout and get cancelled
4. Firestore uploads are incomplete or fail

### **Root Cause**
The workflow file uses `toJSON()` to receive sites from `repository_dispatch`:
```yaml
CUSTOM_SITES_STR = '${{ toJSON(github.event.client_payload.sites) }}'
```

When the API sends an array like `["site1", "site2", "site3"]`, GitHub Actions has trouble parsing JSON arrays in the YAML context, causing the workflow to fall back to ALL enabled sites.

---

## 📊 Evidence from Workflow Runs

### Recent Workflow Analysis (Last 20 runs):
- **2 Successful**: Both used 1 session (3 sites)
- **9 Cancelled**: All used 17 sessions (51 sites) ❌

### Example Cancelled Run (ID: 20181470669):
- **Sessions**: 17 total
- **Completed**: 14 sessions
- **Cancelled**: 3 sessions (1, 9, 13)
- **Consolidate job**: ✅ Succeeded
- **Firestore upload**: ❌ Failed (data wasn't uploaded)

---

## 🔧 THE FIX

### **Solution: Use Comma-Separated String Instead of JSON Array**

#### 1. API Change (`api_server.py:1843`)
```python
# Convert sites array to comma-separated string
sites_str = ','.join(sites) if sites else ''

payload = {
    'event_type': 'trigger-scrape',
    'client_payload': {
        'max_pages': str(max_pages),
        'geocode': str(geocode),
        'sites': sites_str,  # "site1,site2,site3" instead of ["site1","site2","site3"]
        'triggered_by': 'api',
        'timestamp': datetime.now().isoformat()
    }
}
```

#### 2. Workflow Change (`scrape-production.yml`)
```python
# Receive sites as plain string, not JSON
CUSTOM_SITES_STR = "${{ github.event.client_payload.sites }}"

# Parse comma-separated string
if CUSTOM_SITES_STR and CUSTOM_SITES_STR not in ['null', '', 'None']:
    sites_list = [s.strip() for s in CUSTOM_SITES_STR.split(',') if s.strip()]
    if sites_list:
        custom_sites = sites_list
        print(f"Using {len(custom_sites)} custom sites: {custom_sites}")
```

---

## ⚠️ CURRENT BLOCKER

### **Workflow File Validation Issues**
The workflow file contains **emoji characters** (✅❌⚠️📊) that cause:
1. Python YAML parser failures on Windows (CP1252 encoding)
2. GitHub Actions validation errors
3. Workflow not recognized for manual triggering

### **Attempted Fixes**:
- ✅ Removed emojis → Introduced syntax error
- ✅ Restored to last working commit → File still has validation issues
- ❌ Cannot trigger workflow_dispatch manually

---

## 🎯 RECOMMENDED SOLUTION

### **Option 1: Manual Fix in GitHub Web UI** (SAFEST)
1. Go to: https://github.com/Tee-David/realtors_practice/blob/main/.github/workflows/scrape-production.yml
2. Click "Edit" (pencil icon)
3. Make these changes:

**Line 78-79** - Change from:
```yaml
CUSTOM_SITES_STR = '${{ toJSON(github.event.client_payload.sites) }}'
CUSTOM_SITES_INPUT = '${{ toJSON(github.event.inputs.sites) }}'
```

To:
```yaml
CUSTOM_SITES_STR = "${{ github.event.client_payload.sites }}"
CUSTOM_SITES_INPUT = "${{ github.event.inputs.sites }}"
```

**Lines 114-132** - Change from:
```python
# Try client_payload.sites first (from API trigger)
if CUSTOM_SITES_STR and CUSTOM_SITES_STR not in ['null', '', '[]']:
    try:
        custom_sites = json.loads(CUSTOM_SITES_STR)
        if custom_sites:
            print(f"Using custom sites from API/frontend: {custom_sites}")
    except Exception as e:
        print(f"WARNING: Failed to parse client_payload.sites: {e}")
        print(f"Raw value: {CUSTOM_SITES_STR}")

# Try inputs.sites second (from manual workflow_dispatch)
if not custom_sites and CUSTOM_SITES_INPUT and CUSTOM_SITES_INPUT not in ['null', '', '[]']:
    try:
        custom_sites = json.loads(CUSTOM_SITES_INPUT)
        if custom_sites:
            print(f"Using custom sites from manual input: {custom_sites}")
    except Exception as e:
        print(f"WARNING: Failed to parse inputs.sites: {e}")
        print(f"Raw value: {CUSTOM_SITES_INPUT}")
```

To:
```python
# Try client_payload.sites first (from API trigger - comma-separated)
if CUSTOM_SITES_STR and CUSTOM_SITES_STR not in ['null', '', 'None']:
    sites_list = [s.strip() for s in CUSTOM_SITES_STR.split(',') if s.strip()]
    if sites_list:
        custom_sites = sites_list
        print(f"Using {len(custom_sites)} custom sites from API: {custom_sites}")

# Try inputs.sites second (from manual workflow_dispatch)
if not custom_sites and CUSTOM_SITES_INPUT and CUSTOM_SITES_INPUT not in ['null', '', 'None']:
    # Try parsing as JSON array first
    try:
        parsed = json.loads(CUSTOM_SITES_INPUT)
        if isinstance(parsed, list) and parsed:
            custom_sites = parsed
    except:
        # Fall back to comma-separated
        sites_list = [s.strip() for s in CUSTOM_SITES_INPUT.split(',') if s.strip()]
        if sites_list:
            custom_sites = sites_list
```

4. Commit with message: "fix: Parse sites as comma-separated string for repository_dispatch"

### **Option 2: Use a Fresh Workflow File**
I can provide you with a complete, clean workflow file without emojis that has all the fixes applied.

---

## 🧪 TESTING PLAN

Once the workflow is fixed:

### **Test 1: Frontend API with 5 Sites**
```bash
curl -X POST https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -d '{"event_type":"trigger-scrape","client_payload":{"max_pages":"2","geocode":"1","sites":"adronhomes,castles,npc,propertypro,estateintel"}}'
```

**Expected Result**:
- ✅ 2 scrape sessions (5 sites ÷ 3 sites/session)
- ✅ Total duration: ~10-15 minutes
- ✅ Firestore upload: 5 sites uploaded

### **Test 2: Monitor Workflow Logs**
Check Calculate job logs for:
```
Using 5 custom sites from API: ['adronhomes', 'castles', 'npc', 'propertypro', 'estateintel']
Total sites to scrape: 5
Sites per session: 3
Total sessions: 2
```

### **Test 3: Verify Firestore Upload**
Check Consolidate job logs for:
```
SUCCESS: Firestore upload completed successfully!
Total properties uploaded: [count]
```

---

## 📝 FILES MODIFIED

### ✅ Already Committed:
- `api_server.py` (line 1843) - Sites sent as comma-separated string

### ⚠️ Needs Manual Fix:
- `.github/workflows/scrape-production.yml` (lines 78-79, 114-132) - Parse comma-separated sites

---

## 🚀 NEXT STEPS

1. **Fix the workflow file** using Option 1 or 2 above
2. **Test with 5 sites** from frontend API
3. **Verify Firestore upload** in workflow logs
4. **Update frontend documentation** to reflect the fix

---

## 💡 WHY THIS SOLUTION WORKS

### **Before** (JSON Array):
```
API → ["site1","site2"] → GitHub Actions toJSON() → Parsing fails → Falls back to ALL 51 sites ❌
```

### **After** (Comma-Separated):
```
API → "site1,site2" → GitHub Actions receives plain string → Split by comma → Uses 2 custom sites ✅
```

**Benefits**:
- ✅ No JSON parsing in YAML context
- ✅ Simple string manipulation
- ✅ Works with both repository_dispatch and workflow_dispatch
- ✅ Easy to debug (can see exact string in logs)

---

## 🎯 SUCCESS CRITERIA

- [ ] Frontend API trigger uses ONLY the specified sites
- [ ] Workflow creates correct number of sessions (sites ÷ 3)
- [ ] All sessions complete without cancellation
- [ ] Firestore upload succeeds with all properties
- [ ] Total duration matches estimate (~2-3 min per site)

---

**Report Generated**: 2025-12-15 10:30 UTC
**Status**: Fix identified, awaiting workflow file correction
