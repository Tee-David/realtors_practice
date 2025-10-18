# Tasks - Dynamic Configuration Implementation

## Milestone 1: Config Schema & Validation ✅ Foundation

### 1.1 Review Current Config Structure
- [x] Audit existing config.yaml for completeness
- [x] Identify gaps between config.yaml and main.py SITES dict
- [x] Document current vs. desired config schema

### 1.2 Design Enhanced Config Schema
- [x] Define complete YAML structure for site definitions
- [x] Add validation rules (required fields, URL formats, enabled flag)
- [x] Design global settings section (geocoding, pagination, fallback_order)
- [x] Document config schema in config.example.yaml

### 1.3 Implement Config Loader
- [x] Create `core/config_loader.py` module
- [x] Implement YAML parsing with error handling
- [x] Add schema validation (check required fields per site)
- [x] Validate URLs, parser references, selector syntax
- [x] Provide clear error messages for invalid configs

### 1.4 Config Validation Tests
- [x] Test with valid complete config
- [ ] Test with missing required fields
- [ ] Test with invalid URLs
- [ ] Test with malformed YAML
- [ ] Test with empty/missing config file

---

## Milestone 2: Main.py Refactoring 🔄 Migration

### 2.1 Migrate SITES Dict to Config
- [x] Remove hard-coded SITES dict from main.py
- [x] Load sites from config.yaml via config_loader
- [x] Ensure all 50 sites present in config.yaml
- [x] Verify each site has required fields (name, url, parser)

### 2.2 Dynamic Site Filtering
- [x] Read `enabled` flag from config for each site
- [x] Remove ENABLED_SITES hard-coded list
- [x] Filter sites dynamically based on config.yaml
- [x] Log count of enabled vs. total sites on startup

### 2.3 Global Settings Integration
- [x] Replace env-based fallback_order with config.yaml
- [x] Allow env vars to override config (precedence: env > config > defaults)
- [x] Load geocoding settings from config
- [x] Load pagination settings from config
- [x] Document precedence rules in CLAUDE.md

### 2.4 Backward Compatibility
- [x] Ensure existing environment variables still work
- [x] Maintain existing export folder structure
- [x] Preserve log file format
- [x] Confirm geocache.json compatibility

---

## Milestone 3: Parser Integration 🔌 Dynamic Dispatch

### 3.1 Update Dispatcher for Config-Driven Parsing
- [x] Modify `core/dispatcher.py` to accept site config dict
- [x] Pass full site config to ParserAdapter
- [x] Remove hard-coded SPECIAL dict (read from config instead)
- [x] Support parser type selection: specials, generic, custom

### 3.2 Enhance Specials Parser
- [x] Accept config dict instead of hard-coded CONFIGS
- [x] Support per-site selector overrides from config
- [x] Allow per-site pagination strategy from config
- [x] Fallback to generic selectors if site config incomplete

### 3.3 Generic Parser Improvements
- [x] Make scraper_engine.py fully config-driven
- [x] Accept custom list_ready_selectors from config
- [x] Accept custom next_selectors from config
- [x] Support per-site page_cap and scroll_steps

---

## Milestone 4: Enhanced Site Configuration ⚙️ Advanced Features ✅ COMPLETE

### 4.1 Per-Site Overrides ✅
- [x] Add per-site retry_seconds setting
- [x] Add per-site timeout overrides
- [x] Add per-site geocoding enable/disable flag
- [x] Add per-site export format preferences (csv, xlsx, both)

### 4.2 Site Metadata ✅
- [x] Add site category field (aggregator, agency, developer)
- [x] Add site priority field (for parallel scraping order)
- [x] Add site notes/description field
- [x] Add last_successful_scrape timestamp tracking

### 4.3 Advanced Selectors
- [ ] Support multiple selector fallbacks per field
- [ ] Add regex extraction patterns in config
- [ ] Support JSON-LD schema extraction hints
- [ ] Add per-site location hint (Lagos paths)

---

## Milestone 5: Error Handling & Logging 🛡️ Robustness ✅ COMPLETE

### 5.1 Startup Validation ✅
- [x] Validate config.yaml on main.py startup
- [x] Exit early with clear error if config invalid
- [x] Warn about disabled sites (log count)
- [x] Validate parser references exist

### 5.2 Runtime Error Handling ✅
- [x] Catch and log config-related errors per site
- [x] Continue scraping other sites if one site's config fails
- [x] Track and report sites skipped due to config errors
- [x] Add retry logic for transient config issues (file locks)

### 5.3 Enhanced Logging ✅
- [x] Log loaded config summary on startup
- [x] Log each site's config source (defaults vs. overrides)
- [x] Add structured logging for better parsing
- [x] Include site config hash in logs for debugging

---

## Milestone 6: Testing & Documentation 📋 Quality Assurance

### 6.1 Integration Testing ✅
- [x] Test scraping with config-only (no env vars)
- [x] Test env var overrides work correctly
- [x] Test enabling/disabling sites via config
- [x] Test with minimal config (all defaults)
- [x] Test with maximal config (all overrides)
- [x] Created test_milestone4_5.py with 11 comprehensive tests

### 6.2 Site-Specific Testing ✅
- [x] Verify all 50 existing sites work with new config
- [x] Test adding a new site via config only
- [x] Test removing a site (set enabled: false)
- [x] Test modifying site selectors in config
- [x] Created test_site_specific.py with 12 comprehensive tests

### 6.3 Documentation Updates ✅
- [x] Update CLAUDE.md with config-driven workflow
- [x] Create config.example.yaml with all options documented
- [x] Add troubleshooting section for common config errors
- [x] Document config precedence (env > config > defaults)
- [x] Created MILESTONE_2_COMPLETE.md
- [x] Created MILESTONE_3_COMPLETE.md
- [x] Created MILESTONE_4_5_COMPLETE.md

### 6.4 Code Cleanup ✅
- [x] Remove commented-out old SITES dict code
- [x] Ensure no hard-coded URLs remain in .py files
- [x] Add type hints to config_loader functions
- [x] Run linter/formatter on modified files

---

## Milestone 7: Performance & Monitoring 🚀 Optimization (MOSTLY COMPLETE)

### 7.1 Config Caching ✅
- [x] Cache parsed config in memory (reload on change detection)
- [x] Add clear_config_cache() function
- [ ] Add --reload-config CLI flag (future enhancement)
- [ ] Monitor config.yaml file for changes during long runs (future enhancement)

### 7.2 Parallel Scraping (Future) - SKIPPED (Nice-to-Have)
- [ ] Design thread-safe config access
- [ ] Add site priority field for parallel execution order
- [ ] Implement worker pool with configurable concurrency
- [ ] Add global rate limiting across workers

### 7.3 Status Tracking ✅
- [x] Track per-site success/failure history (in site_metadata.json)
- [x] Export scrape metadata to JSON (automatic)
- [x] Created status.py CLI command to show site health
- [ ] Generate HTML report with site statistics (future enhancement)

---

## Milestone 8: Deployment & Maintenance 🔧 Operations (MOSTLY COMPLETE)

### 8.1 Config Management ✅
- [x] Add config.yaml to .gitignore (use config.example.yaml as template)
- [x] Create config validation CLI tool: `python validate_config.py`
- [ ] Add pre-commit hook to validate config on commit (future enhancement)
- [x] Document config backup/restore procedures (in MIGRATION_GUIDE.md)

### 8.2 Migration Guide ✅
- [x] Write migration guide from old to new config system
- [x] Created MIGRATION_GUIDE.md with complete documentation
- [x] Document breaking changes (none - fully backward compatible)
- [x] Create rollback plan (documented in MIGRATION_GUIDE.md)

### 8.3 CI/CD Integration - SKIPPED (Future)
- [ ] Add config validation to CI pipeline
- [ ] Test with example config in CI
- [ ] Add integration tests for config loader
- [ ] Automate deployment with validated config

---

## Quick Reference: Task Priority

### Must Have (P0) - Core Functionality
- Milestone 1: Config Schema & Validation
- Milestone 2: Main.py Refactoring
- Milestone 3: Parser Integration
- Milestone 6.3: Documentation Updates

### Should Have (P1) - Enhanced Features
- Milestone 4: Enhanced Site Configuration
- Milestone 5: Error Handling & Logging
- Milestone 6.1-6.2: Testing

### Nice to Have (P2) - Future Improvements
- Milestone 7: Performance & Monitoring
- Milestone 8: Deployment & Maintenance

---

## Milestone 9: Export Watcher Service - Foundation 🔍 File Monitoring ✅ COMPLETE

### 9.1 Service Architecture Design ✅
- [x] Design service architecture (daemon vs. on-demand)
- [x] Define input: exports/ folder structure
- [x] Define output: exports/cleaned/ folder structure
- [x] Design state tracking mechanism (track processed files)
- [x] Document service flow diagram

### 9.2 File Watcher Implementation ✅
- [x] Implement file watcher for exports/ folder
- [x] Detect new CSV files in exports/<site>/
- [x] Detect new XLSX files in exports/<site>/
- [x] Track file modification timestamps
- [x] Implement file hash-based change detection

### 9.3 State Management ✅
- [x] Create state file: exports/cleaned/.watcher_state.json
- [x] Track processed files (path, hash, timestamp, record_count)
- [x] Implement idempotent processing (skip already-processed files)
- [x] Handle state file corruption/recovery
- [x] Add state file locking for concurrent access

### 9.4 Service Entry Point ✅
- [x] Create watcher.py service script
- [x] Add CLI arguments (--watch, --once, --reset-state)
- [x] Implement graceful shutdown (SIGINT/SIGTERM handling)
- [x] Add dry-run mode (--dry-run)
- [x] Add verbose logging (--verbose)

---

## Milestone 10: Data Ingestion & Cleaning 🧹 Normalization ✅ COMPLETE

### 10.1 File Ingestion ✅
- [x] Implement CSV parser (handle various encodings)
- [x] Implement XLSX parser (read all sheets)
- [x] Detect and handle semi-structured/jumbled data
- [x] Handle missing columns gracefully
- [x] Validate column headers against expected schema

### 10.2 Data Cleaning Pipeline ✅
- [x] Create core/data_cleaner.py module
- [x] Implement intelligent field mapping (fuzzy column matching)
- [x] Normalize price formats (remove currency, handle "million", "k")
- [x] Normalize location strings (trim, titlecase, Lagos aliases)
- [x] Clean property_type values (standardize variations)
- [x] Extract bedrooms/bathrooms from title if missing
- [x] Handle duplicate column names

### 10.3 Schema Detection & Validation ✅
- [x] Define canonical schema for master workbook
- [x] Auto-detect column types (string, number, date)
- [x] Validate required fields (title, price, location minimum)
- [x] Flag records with missing critical fields
- [x] Create data quality metrics per file

### 10.4 Deduplication Logic ✅
- [x] Implement record deduplication (by hash or key fields)
- [x] Detect duplicates within same file
- [x] Detect duplicates across multiple files
- [x] Detect duplicates across historical data
- [x] Create deduplication report (duplicates found, kept, skipped)

---

## Milestone 11: Master Workbook Management 📊 Consolidated Output ✅ COMPLETE

### 11.1 Master Workbook Creation ✅
- [x] Create exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
- [x] Initialize workbook with metadata sheet
- [x] Create per-site sheets dynamically
- [x] Set column headers and formatting
- [x] Add data validation rules

### 11.2 Per-Site Sheet Management ✅
- [x] Detect existing site sheets in master workbook
- [x] Create new sheet when new site detected
- [x] Append new records to existing site sheets
- [x] Skip appending if no new records found
- [x] Maintain sheet order (alphabetical or by priority)

### 11.3 Append-Only Logic (Idempotency) ✅
- [x] Load existing records from site sheet
- [x] Compare new records against existing (by hash or composite key)
- [x] Append only genuinely new records
- [x] Skip records already present in sheet
- [x] Log append statistics (new, skipped, total)

### 11.4 Workbook Optimization ✅
- [x] Implement efficient row append (avoid full reload)
- [x] Add freeze panes (header row)
- [x] Add auto-filter to headers
- [x] Set column widths for readability
- [x] Handle large workbooks (>1M rows strategies)

---

## Milestone 12: Canonical Output Formats 📁 Multi-Format Export ✅ COMPLETE

### 12.1 Per-Site CSV Export ✅
- [x] Create exports/cleaned/<site>/<site>_cleaned.csv
- [x] Write canonical CSV with consistent schema
- [x] Update CSV file incrementally (append new records)
- [x] Handle CSV encoding (UTF-8 with BOM for Excel compatibility)
- [x] Add CSV metadata header (generation timestamp, record count)

### 12.2 Per-Site Parquet Export ✅
- [x] Install pyarrow/fastparquet dependency
- [x] Create exports/cleaned/<site>/<site>_cleaned.parquet
- [x] Write Parquet with optimized schema (typed columns)
- [x] Support Parquet append/merge operations
- [x] Add Parquet metadata (schema version, source files)

### 12.3 Metadata Generation ✅
- [x] Create exports/cleaned/metadata.json
- [x] Track per-site statistics (total_records, last_updated, source_files)
- [x] Track data quality metrics (missing_fields, duplicates_removed)
- [x] Track processing history (files_processed, records_added)
- [x] Add schema version tracking

### 12.4 Error Reporting ✅
- [x] Create exports/cleaned/errors.log
- [x] Log file parsing errors (malformed CSV, corrupted XLSX)
- [x] Log data validation errors (missing required fields)
- [x] Log deduplication conflicts (same hash, different data)
- [x] Create error summary report per run

---

## Milestone 13: Service Operations & Testing 🧪 Quality & Reliability ✅ COMPLETE

### 13.1 Logging & Monitoring ✅
- [x] Add structured logging to watcher service
- [x] Log file processing start/end with timing
- [x] Log record counts (read, cleaned, appended, skipped)
- [x] Create processing summary report
- [ ] Add progress indicators for large files (future enhancement)

### 13.2 Error Handling & Recovery ✅
- [x] Handle file access errors (locks, permissions)
- [x] Handle corrupted/malformed export files
- [x] Recover from partial processing (resume on crash)
- [x] Add retry logic for transient errors
- [ ] Implement rollback on critical errors (future enhancement)

### 13.3 Performance Optimization ✅
- [x] Benchmark processing speed (records/second)
- [x] Optimize large file handling (chunked reading)
- [ ] Implement parallel file processing (future enhancement)
- [x] Add caching for expensive operations
- [x] Profile memory usage for large datasets

### 13.4 Testing & Validation ✅
- [x] Create test_watcher_integration.py with integration tests
- [x] Test with sample exports (various formats)
- [x] Test idempotency (re-run with same files)
- [x] Test incremental updates (new files added)
- [x] Test error scenarios (corrupted files, missing columns)
- [x] Test master workbook with 25+ site sheets

### 13.5 Documentation ✅
- [x] Create WATCHER_QUICKSTART.md with usage guide
- [x] Create WATCHER_COMPLETE.md with full documentation
- [x] Create MILESTONE_9_10_11_COMPLETE.md
- [x] Document usage: python watcher.py --watch
- [x] Document configuration options
- [x] Document output folder structure
- [x] Add troubleshooting guide
- [x] Update CLAUDE.md with watcher service info

---

## Next Steps (Immediate)

### Phase 1 (Completed) ✅
1. ~~Start with Milestone 1.2: Design complete config.yaml schema~~
2. ~~Create config.example.yaml: Template with all options documented~~
3. ~~Implement core/config_loader.py: Basic YAML parsing with validation~~
4. ~~Test with subset of sites: Validate approach before full migration~~
5. ~~Iterate: Refine schema based on real-world testing~~

### Phase 2 (Current) - Export Watcher Service
1. **Start with Milestone 9.1**: Design watcher service architecture
2. **Create watcher.py**: Basic file monitoring script
3. **Implement core/data_cleaner.py**: Data cleaning and normalization
4. **Test with existing exports/**: Validate with real scraper output
5. **Iterate**: Refine cleaning logic based on actual data patterns
