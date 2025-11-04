# Frontend Page Structure Guide
## Consolidating 68 API Endpoints into 5 Strategic Pages

**Version**: 1.0
**Date**: 2025-11-04
**Target**: Frontend Developer (Next.js/React)

---

## Table of Contents
1. [Overview](#overview)
2. [Page Structure Summary](#page-structure-summary)
3. [Detailed Page Breakdowns](#detailed-page-breakdowns)
4. [API Endpoint Mapping](#api-endpoint-mapping)
5. [Component Architecture](#component-architecture)
6. [Implementation Examples](#implementation-examples)
7. [User Flow Diagrams](#user-flow-diagrams)

---

## Overview

### Current Problem
- 20+ pages = bloated navigation
- Scattered functionality
- Poor user experience
- Difficult to maintain

### Solution
Consolidate 68 API endpoints into **5 strategic pages** that align with user workflows:

1. **Dashboard** (Home/Overview)
2. **Properties** (Browse & Search)
3. **Scraper Control** (Admin/Backend Management)
4. **Saved Searches** (User Preferences)
5. **Settings** (Configuration & System)

---

## Page Structure Summary

| Page | Primary Purpose | Endpoint Count | User Type |
|------|----------------|----------------|-----------|
| **Dashboard** | Overview, stats, quick actions | 12 endpoints | All users |
| **Properties** | Browse, search, view listings | 15 endpoints | End users |
| **Scraper Control** | Manage scraping operations | 20 endpoints | Admin only |
| **Saved Searches** | Manage alerts & preferences | 10 endpoints | End users |
| **Settings** | System config, sites, emails | 11 endpoints | Admin only |

**Total**: 68 endpoints across 5 pages

---

## Detailed Page Breakdowns

### Page 1: Dashboard (Home/Overview)
**Route**: `/` or `/dashboard`
**Purpose**: High-level overview, quick stats, recent activity
**User Type**: All users (different views for admin vs. regular users)

#### What Users See
- **Top Section**: Key metrics in cards
  - Total properties available
  - Properties added today
  - Active saved searches
  - System health status

- **Middle Section**: Quick actions
  - Search properties button
  - View recent listings
  - Create saved search
  - (Admin) Quick scrape button

- **Bottom Section**: Activity feed
  - Recent scrapes (admin)
  - New properties matching saved searches
  - System alerts/notifications

#### API Endpoints Used (12)

**Statistics & Overview**:
```
GET /api/stats/overview
GET /api/stats/trends
GET /api/health
GET /api/scrape/status
```

**Recent Data**:
```
GET /api/data/recent?limit=10
GET /api/data/stats
GET /api/saved-searches/matches/new
```

**Quick Actions**:
```
POST /api/scrape/quick
GET /api/sites/stats
GET /api/sites/enabled
```

**Health Monitoring**:
```
GET /api/github/workflow-status
GET /api/firestore/status
```

#### Component Structure
```
Dashboard/
├── StatsCards (4 cards)
├── QuickActions (button group)
├── RecentActivity (timeline/list)
├── SystemHealth (status badges)
└── AdminQuickPanel (conditional render)
```

---

### Page 2: Properties (Browse & Search)
**Route**: `/properties`
**Purpose**: Main property browsing, searching, and viewing interface
**User Type**: All users (primary end-user interface)

#### What Users See
- **Top Section**: Search & filters
  - Search bar (natural language)
  - Filter dropdowns (price, bedrooms, location, property type)
  - Sort options (price, date, relevance)

- **Main Section**: Property grid/list
  - Property cards with image, price, location
  - Pagination controls
  - View toggle (grid/list/map)

- **Sidebar**: Quick filters & saved searches
  - Popular locations
  - Price ranges
  - Property types
  - Your saved searches (quick apply)

- **Property Detail Modal/Page**: Full property information
  - All details, images, map
  - Price intelligence
  - Similar properties
  - Save search button
  - Contact agent button

#### API Endpoints Used (15)

**Search & Browse**:
```
GET /api/data/all?limit=50&offset=0&sort=price_desc
GET /api/data/search?query=3%20bedroom%20Lekki
POST /api/data/advanced-search (with filters)
GET /api/data/sites/{site}?limit=20
```

**Filters & Aggregations**:
```
GET /api/data/stats (for filter options - locations, price ranges)
GET /api/stats/sites (for site-specific filtering)
```

**Property Details**:
```
GET /api/data/property/{property_id}
GET /api/prices/analyze (price intelligence for selected property)
GET /api/prices/similar?location=Lekki&bedrooms=3
```

**Map View**:
```
GET /api/data/geocoded?limit=100
```

**Saved Search Integration**:
```
POST /api/saved-searches/create (when user saves current filters)
GET /api/saved-searches/matches?search_id={id}
```

**Export**:
```
GET /api/data/export/csv?filters=...
GET /api/data/export/excel?filters=...
```

**Similar Properties**:
```
GET /api/prices/trends?location=Lekki
GET /api/prices/history?property_id={id}
```

#### Component Structure
```
Properties/
├── SearchBar (with autocomplete)
├── FilterPanel (collapsible sidebar)
│   ├── PriceFilter
│   ├── LocationFilter
│   ├── BedroomFilter
│   └── PropertyTypeFilter
├── PropertyGrid/List (main view)
│   ├── PropertyCard (repeating)
│   └── Pagination
├── MapView (toggle view)
└── PropertyDetailModal
    ├── ImageGallery
    ├── PropertyInfo
    ├── PriceIntelligence
    ├── SimilarProperties
    └── SaveSearchButton
```

---

### Page 3: Scraper Control (Admin Panel)
**Route**: `/admin/scraper` or `/scraper`
**Purpose**: Backend management - control scraping operations
**User Type**: Admin only (protected route)

#### What Users See
- **Top Section**: Control panel
  - Start/Stop/Pause scraping buttons
  - Site selector (scrape specific sites or all)
  - Quick settings (max pages, headless mode)

- **Main Section**: Active scraping status
  - Progress bars for each site being scraped
  - Real-time logs (scrolling console)
  - Current status messages
  - Time elapsed/estimated completion

- **Bottom Section**: Scraping history
  - Table of past scrapes
  - Success/failure indicators
  - Duration, properties found
  - Download exports

- **Right Sidebar**: Site management
  - List of all sites (82+)
  - Enable/disable toggles
  - Site health indicators
  - Test individual site button

#### API Endpoints Used (20)

**Scrape Control**:
```
POST /api/scrape/start (with options: sites, max_pages)
POST /api/scrape/stop
GET /api/scrape/status (poll every 2-5 seconds)
POST /api/scrape/quick
POST /api/scrape/validate
```

**Real-time Monitoring**:
```
GET /api/scrape/progress (detailed progress per site)
GET /api/logs?level=info&site=npc&lines=100
GET /api/logs/recent?lines=50
```

**Scraping History**:
```
GET /api/scrape/history?limit=20
GET /api/scrape/stats
GET /api/stats/sites (site-specific statistics)
```

**Site Management** (used in sidebar):
```
GET /api/sites (list all sites)
GET /api/sites/enabled
POST /api/sites/enable (enable specific sites)
POST /api/sites/disable
GET /api/sites/{site}/test
GET /api/sites/stats
```

**Export Downloads**:
```
GET /api/data/export/csv?site={site}&timestamp={ts}
GET /api/data/export/excel?site={site}&timestamp={ts}
```

**GitHub Actions Integration**:
```
POST /api/github/workflow-dispatch (trigger automated scrape)
GET /api/github/workflow-status
GET /api/github/runs/latest
```

#### Component Structure
```
ScraperControl/
├── ControlPanel
│   ├── StartButton (with options modal)
│   ├── StopButton
│   ├── SiteSelector
│   └── QuickSettings
├── ActiveStatus
│   ├── ProgressBars (per site)
│   ├── LiveLogs (scrolling console)
│   └── StatusMessages
├── HistoryTable
│   ├── ScrapeRow (repeating)
│   └── ExportButtons
└── SiteSidebar
    ├── SiteList
    │   ├── SiteItem (82+ items)
    │   └── EnableToggle
    └── SiteHealthBadges
```

---

### Page 4: Saved Searches (User Preferences)
**Route**: `/saved-searches` or `/alerts`
**Purpose**: Manage user's saved search criteria and email alerts
**User Type**: End users (authenticated)

#### What Users See
- **Top Section**: Create new saved search
  - Quick create form
  - Import from current Property page filters button
  - Templates (e.g., "3BR in Lekki", "Under 50M in Victoria Island")

- **Main Section**: List of saved searches
  - Card view of each saved search
  - Shows criteria (location, price, bedrooms, etc.)
  - Number of new matches since last check
  - Email notification toggle
  - Edit/Delete buttons
  - "View Matches" button

- **Matches View**: Properties matching saved search
  - Similar to Properties page but pre-filtered
  - Highlights new properties (since last view)
  - Quick access to property details

#### API Endpoints Used (10)

**Saved Search Management**:
```
POST /api/saved-searches/create
GET /api/saved-searches (list user's searches)
PUT /api/saved-searches/{id}/update
DELETE /api/saved-searches/{id}
GET /api/saved-searches/{id}
```

**Matches & Alerts**:
```
GET /api/saved-searches/matches?search_id={id}
GET /api/saved-searches/matches/new (new matches since last check)
POST /api/saved-searches/{id}/notify (trigger email notification)
```

**Email Management**:
```
PUT /api/saved-searches/{id}/settings (enable/disable email alerts)
POST /api/email/test (test email notification for this search)
```

#### Component Structure
```
SavedSearches/
├── CreateSearchPanel
│   ├── QuickCreateForm
│   ├── ImportFromFiltersButton
│   └── Templates
├── SavedSearchList
│   ├── SearchCard (repeating)
│   │   ├── CriteriaDisplay
│   │   ├── NewMatchesBadge
│   │   ├── EmailToggle
│   │   └── ActionButtons
│   └── EmptyState
└── MatchesView (modal or separate section)
    ├── PropertyList (filtered)
    └── NewPropertyHighlight
```

---

### Page 5: Settings (System Configuration)
**Route**: `/admin/settings` or `/settings`
**Purpose**: System configuration, site management, email settings
**User Type**: Admin only (protected route)

#### What Users See
- **Tab 1: Sites Configuration**
  - Table of all 82+ sites
  - Enable/disable column
  - Edit site settings (max pages, overrides)
  - Test site button
  - Add new site form
  - Delete site button

- **Tab 2: Email Notifications**
  - SMTP settings form
  - Email recipients management
  - Test email button
  - Notification templates
  - Schedule settings (when to send alerts)

- **Tab 3: Firestore Integration**
  - Connection status
  - Upload data to Firestore button
  - Sync settings
  - Collection browser

- **Tab 4: System Settings**
  - Global scraping defaults (page cap, retry settings)
  - Geocoding settings
  - Export format preferences
  - Cache management
  - Debug mode toggle

- **Tab 5: Authentication** (if enabled)
  - API key management
  - User management
  - JWT settings

#### API Endpoints Used (11)

**Sites Configuration**:
```
GET /api/sites (all sites with details)
POST /api/sites/add
PUT /api/sites/{site}/update
DELETE /api/sites/{site}
POST /api/sites/{site}/test
```

**Email Settings**:
```
GET /api/email/settings
PUT /api/email/settings
POST /api/email/test
POST /api/email/send-notification
```

**Firestore Integration**:
```
GET /api/firestore/status
POST /api/firestore/upload
GET /api/firestore/collections
```

#### Component Structure
```
Settings/
├── TabNavigation
├── SitesTab
│   ├── SitesTable
│   │   ├── SiteRow (82+ rows)
│   │   └── ActionButtons
│   └── AddSiteForm
├── EmailTab
│   ├── SMTPSettingsForm
│   ├── RecipientsManager
│   └── TestEmailButton
├── FirestoreTab
│   ├── ConnectionStatus
│   ├── UploadButton
│   └── CollectionBrowser
└── SystemTab
    ├── GlobalSettingsForm
    ├── CacheManager
    └── DebugToggle
```

---

## API Endpoint Mapping

### Complete Endpoint Distribution

#### Dashboard (12 endpoints)
```
✓ GET  /api/stats/overview
✓ GET  /api/stats/trends
✓ GET  /api/health
✓ GET  /api/scrape/status
✓ GET  /api/data/recent
✓ GET  /api/data/stats
✓ GET  /api/saved-searches/matches/new
✓ POST /api/scrape/quick
✓ GET  /api/sites/stats
✓ GET  /api/sites/enabled
✓ GET  /api/github/workflow-status
✓ GET  /api/firestore/status
```

#### Properties (15 endpoints)
```
✓ GET  /api/data/all
✓ GET  /api/data/search
✓ POST /api/data/advanced-search
✓ GET  /api/data/sites/{site}
✓ GET  /api/data/stats
✓ GET  /api/stats/sites
✓ GET  /api/data/property/{id}
✓ GET  /api/prices/analyze
✓ GET  /api/prices/similar
✓ GET  /api/data/geocoded
✓ POST /api/saved-searches/create
✓ GET  /api/saved-searches/matches
✓ GET  /api/data/export/csv
✓ GET  /api/data/export/excel
✓ GET  /api/prices/trends
```

#### Scraper Control (20 endpoints)
```
✓ POST /api/scrape/start
✓ POST /api/scrape/stop
✓ GET  /api/scrape/status
✓ POST /api/scrape/quick
✓ POST /api/scrape/validate
✓ GET  /api/scrape/progress
✓ GET  /api/logs
✓ GET  /api/logs/recent
✓ GET  /api/scrape/history
✓ GET  /api/scrape/stats
✓ GET  /api/stats/sites
✓ GET  /api/sites
✓ GET  /api/sites/enabled
✓ POST /api/sites/enable
✓ POST /api/sites/disable
✓ GET  /api/sites/{site}/test
✓ GET  /api/sites/stats
✓ POST /api/github/workflow-dispatch
✓ GET  /api/github/workflow-status
✓ GET  /api/github/runs/latest
```

#### Saved Searches (10 endpoints)
```
✓ POST   /api/saved-searches/create
✓ GET    /api/saved-searches
✓ PUT    /api/saved-searches/{id}/update
✓ DELETE /api/saved-searches/{id}
✓ GET    /api/saved-searches/{id}
✓ GET    /api/saved-searches/matches
✓ GET    /api/saved-searches/matches/new
✓ POST   /api/saved-searches/{id}/notify
✓ PUT    /api/saved-searches/{id}/settings
✓ POST   /api/email/test
```

#### Settings (11 endpoints)
```
✓ GET    /api/sites
✓ POST   /api/sites/add
✓ PUT    /api/sites/{site}/update
✓ DELETE /api/sites/{site}
✓ POST   /api/sites/{site}/test
✓ GET    /api/email/settings
✓ PUT    /api/email/settings
✓ POST   /api/email/test
✓ GET    /api/firestore/status
✓ POST   /api/firestore/upload
✓ GET    /api/firestore/collections
```

**Total: 68 endpoints** ✓

---

## Component Architecture

### Shared Components (used across multiple pages)

```typescript
// components/shared/

PropertyCard.tsx           // Used in: Properties, Saved Searches, Dashboard
LoadingSpinner.tsx         // Used in: All pages
ErrorBoundary.tsx          // Used in: All pages
StatsCard.tsx             // Used in: Dashboard, Scraper Control
FilterPanel.tsx           // Used in: Properties
SearchBar.tsx             // Used in: Properties, Dashboard
Pagination.tsx            // Used in: Properties, Scraper Control
StatusBadge.tsx           // Used in: Dashboard, Scraper Control, Settings
ActionButton.tsx          // Used in: All pages
Modal.tsx                 // Used in: Properties, Saved Searches, Settings
Toast/Notification.tsx    // Used in: All pages
```

### Custom Hooks (reusable logic)

```typescript
// hooks/

useApi.ts                 // Generic API fetch wrapper
useScraper.ts            // Scraping operations (start/stop/status)
useProperties.ts         // Property data fetching & filtering
useSavedSearches.ts      // Saved search management
useSites.ts              // Site configuration
usePolling.ts            // Real-time status polling
usePagination.ts         // Pagination logic
useFilters.ts            // Filter state management
useAuth.ts               // Authentication (if enabled)
```

---

## Implementation Examples

### Example 1: Dashboard Page Implementation

```typescript
// pages/dashboard.tsx

import { useEffect } from 'react';
import { useApi } from '@/hooks/useApi';
import { useScraper } from '@/hooks/useScraper';
import StatsCard from '@/components/shared/StatsCard';
import QuickActions from '@/components/dashboard/QuickActions';
import RecentActivity from '@/components/dashboard/RecentActivity';
import SystemHealth from '@/components/dashboard/SystemHealth';

export default function Dashboard() {
  // Fetch overview statistics
  const { data: overview, loading: overviewLoading } = useApi('/api/stats/overview');
  const { data: trends } = useApi('/api/stats/trends');
  const { data: health } = useApi('/api/health');
  const { data: recentData } = useApi('/api/data/recent?limit=10');

  // Scraper status (for admin users)
  const { status, isScraperRunning } = useScraper();

  return (
    <div className="dashboard">
      {/* Top: Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Properties"
          value={overview?.total_properties || 0}
          icon="home"
          loading={overviewLoading}
        />
        <StatsCard
          title="Added Today"
          value={overview?.added_today || 0}
          icon="calendar"
          trend={trends?.daily_growth}
        />
        <StatsCard
          title="Active Searches"
          value={overview?.active_searches || 0}
          icon="search"
        />
        <StatsCard
          title="System Health"
          value={health?.status || 'Unknown'}
          icon="activity"
          variant={health?.status === 'healthy' ? 'success' : 'warning'}
        />
      </div>

      {/* Middle: Quick Actions */}
      <QuickActions isAdmin={true} isScraperRunning={isScraperRunning} />

      {/* Bottom: Recent Activity */}
      <div className="dashboard-grid">
        <RecentActivity data={recentData} />
        <SystemHealth healthData={health} scraperStatus={status} />
      </div>
    </div>
  );
}
```

### Example 2: Properties Page with Filters

```typescript
// pages/properties.tsx

import { useState } from 'react';
import { useProperties } from '@/hooks/useProperties';
import { useFilters } from '@/hooks/useFilters';
import SearchBar from '@/components/shared/SearchBar';
import FilterPanel from '@/components/shared/FilterPanel';
import PropertyGrid from '@/components/properties/PropertyGrid';
import PropertyDetailModal from '@/components/properties/PropertyDetailModal';
import Pagination from '@/components/shared/Pagination';

export default function Properties() {
  const [selectedProperty, setSelectedProperty] = useState(null);
  const { filters, updateFilters, clearFilters } = useFilters();
  const {
    properties,
    loading,
    error,
    totalCount,
    currentPage,
    setPage
  } = useProperties(filters);

  const handleSearch = (query: string) => {
    updateFilters({ search: query });
  };

  return (
    <div className="properties-page">
      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} placeholder="Search properties..." />

      <div className="properties-layout">
        {/* Left Sidebar: Filters */}
        <FilterPanel
          filters={filters}
          onFilterChange={updateFilters}
          onClear={clearFilters}
        />

        {/* Main Content: Property Grid */}
        <div className="properties-main">
          <div className="properties-header">
            <h2>{totalCount} Properties Found</h2>
            <div className="view-toggles">
              {/* Grid/List/Map view toggles */}
            </div>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : error ? (
            <ErrorMessage error={error} />
          ) : (
            <>
              <PropertyGrid
                properties={properties}
                onPropertyClick={setSelectedProperty}
              />

              <Pagination
                currentPage={currentPage}
                totalItems={totalCount}
                itemsPerPage={50}
                onPageChange={setPage}
              />
            </>
          )}
        </div>
      </div>

      {/* Property Detail Modal */}
      {selectedProperty && (
        <PropertyDetailModal
          property={selectedProperty}
          onClose={() => setSelectedProperty(null)}
        />
      )}
    </div>
  );
}
```

### Example 3: Scraper Control with Real-time Updates

```typescript
// pages/scraper.tsx

import { useState, useEffect } from 'react';
import { useScraper } from '@/hooks/useScraper';
import { usePolling } from '@/hooks/usePolling';
import { useSites } from '@/hooks/useSites';
import ControlPanel from '@/components/scraper/ControlPanel';
import ActiveStatus from '@/components/scraper/ActiveStatus';
import HistoryTable from '@/components/scraper/HistoryTable';
import SiteSidebar from '@/components/scraper/SiteSidebar';

export default function ScraperControl() {
  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const [maxPages, setMaxPages] = useState(30);

  // Scraper operations
  const {
    status,
    progress,
    history,
    startScrape,
    stopScrape,
    isRunning
  } = useScraper();

  // Site management
  const { sites, enabledSites, toggleSite } = useSites();

  // Poll for status updates every 3 seconds when scraper is running
  const { data: liveStatus } = usePolling(
    '/api/scrape/status',
    { enabled: isRunning, interval: 3000 }
  );

  // Poll for logs every 5 seconds when scraper is running
  const { data: logs } = usePolling(
    '/api/logs/recent?lines=50',
    { enabled: isRunning, interval: 5000 }
  );

  const handleStartScrape = () => {
    startScrape({
      sites: selectedSites.length > 0 ? selectedSites : undefined,
      max_pages: maxPages
    });
  };

  return (
    <div className="scraper-control">
      {/* Top: Control Panel */}
      <ControlPanel
        isRunning={isRunning}
        selectedSites={selectedSites}
        onSitesChange={setSelectedSites}
        maxPages={maxPages}
        onMaxPagesChange={setMaxPages}
        onStart={handleStartScrape}
        onStop={stopScrape}
      />

      <div className="scraper-layout">
        {/* Main Content */}
        <div className="scraper-main">
          {/* Active Status */}
          {isRunning && (
            <ActiveStatus
              status={liveStatus}
              progress={progress}
              logs={logs}
            />
          )}

          {/* History Table */}
          <HistoryTable history={history} />
        </div>

        {/* Right Sidebar: Site Management */}
        <SiteSidebar
          sites={sites}
          enabledSites={enabledSites}
          onToggleSite={toggleSite}
        />
      </div>
    </div>
  );
}
```

### Example 4: Custom Hook - useProperties

```typescript
// hooks/useProperties.ts

import { useState, useEffect } from 'react';
import { useApi } from './useApi';

interface Filters {
  search?: string;
  location?: string;
  minPrice?: number;
  maxPrice?: number;
  bedrooms?: number;
  propertyType?: string;
  site?: string;
}

export function useProperties(filters: Filters, limit = 50) {
  const [currentPage, setCurrentPage] = useState(1);
  const offset = (currentPage - 1) * limit;

  // Build query params from filters
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
    ...(filters.search && { query: filters.search }),
    ...(filters.site && { site: filters.site })
  });

  // Fetch properties
  const {
    data: response,
    loading,
    error,
    refetch
  } = useApi(`/api/data/all?${params.toString()}`);

  // For advanced filters, use POST endpoint
  const fetchAdvanced = async () => {
    if (hasAdvancedFilters(filters)) {
      const res = await fetch('/api/data/advanced-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters, limit, offset })
      });
      return res.json();
    }
    return null;
  };

  const properties = response?.properties || [];
  const totalCount = response?.total || 0;

  return {
    properties,
    loading,
    error,
    totalCount,
    currentPage,
    setPage: setCurrentPage,
    refetch
  };
}

function hasAdvancedFilters(filters: Filters) {
  return !!(
    filters.location ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.bedrooms ||
    filters.propertyType
  );
}
```

---

## User Flow Diagrams

### Flow 1: End User Looking for Property

```
1. User lands on Dashboard
   ↓
2. Sees stats: "1,234 properties available"
   ↓
3. Clicks "Search Properties" button
   ↓
4. Goes to Properties page
   ↓
5. Uses search bar: "3 bedroom Lekki"
   ↓
6. Applies filters: Price ₦40M-₦80M
   ↓
7. Browses results in grid view
   ↓
8. Clicks property card
   ↓
9. Property detail modal opens
   ↓
10. Views price intelligence, similar properties
    ↓
11. Clicks "Save this search"
    ↓
12. Redirected to Saved Searches page
    ↓
13. Enables email alerts for this search
    ↓
14. Done! User will be notified of new matches
```

### Flow 2: Admin Running a Scrape

```
1. Admin lands on Dashboard
   ↓
2. Sees "Last scrape: 2 days ago" warning
   ↓
3. Clicks "Scraper Control" in nav
   ↓
4. Goes to Scraper Control page
   ↓
5. Selects sites to scrape (or "All")
   ↓
6. Sets max_pages to 40
   ↓
7. Clicks "Start Scraping" button
   ↓
8. ActiveStatus component appears
   ↓
9. Sees real-time progress bars per site
   ↓
10. Watches live logs scrolling
    ↓
11. Scrape completes after 30 minutes
    ↓
12. Success message: "Found 450 new properties"
    ↓
13. Clicks "View New Properties" button
    ↓
14. Redirected to Properties page with filter: "Added today"
    ↓
15. Reviews new properties
    ↓
16. Done!
```

### Flow 3: Admin Configuring Email Alerts

```
1. Admin goes to Settings page
   ↓
2. Clicks "Email Notifications" tab
   ↓
3. Fills SMTP settings form
   - Host: smtp.gmail.com
   - Port: 587
   - Username: admin@example.com
   - Password: ***
   ↓
4. Adds email recipients
   - admin@example.com
   - sales@example.com
   ↓
5. Clicks "Test Email" button
   ↓
6. Receives test email successfully
   ↓
7. Clicks "Save Settings"
   ↓
8. Email notifications now active
   ↓
9. Users with saved searches will receive daily alerts
```

---

## Navigation Structure

### Primary Navigation (All Users)
```
┌─────────────────────────────────────────┐
│  [Logo]  Dashboard  Properties  Saved   │
│                                 Searches │
└─────────────────────────────────────────┘
```

### Admin Navigation (Additional Items)
```
┌──────────────────────────────────────────────────────┐
│  [Logo]  Dashboard  Properties  Saved   Scraper      │
│                                 Searches Control      │
│                                          Settings     │
└──────────────────────────────────────────────────────┘
```

### Mobile Navigation (Hamburger Menu)
```
☰ Menu
  ├─ Dashboard
  ├─ Properties
  ├─ Saved Searches
  ├─ ─────────────── (Admin only below)
  ├─ Scraper Control
  └─ Settings
```

---

## Implementation Roadmap

### Phase 1: Core Pages (Week 1)
1. **Dashboard** - Basic stats and quick actions
2. **Properties** - Simple listing with search
3. **Set up routing** - Next.js pages, navigation

### Phase 2: Enhanced Features (Week 2)
4. **Properties** - Add filters, pagination, detail modal
5. **Saved Searches** - Basic CRUD operations
6. **Dashboard** - Add recent activity, system health

### Phase 3: Admin Features (Week 3)
7. **Scraper Control** - Start/stop, basic status
8. **Settings** - Sites configuration tab
9. **Scraper Control** - Add real-time logs, history

### Phase 4: Polish & Advanced (Week 4)
10. **Properties** - Price intelligence, map view
11. **Saved Searches** - Email alerts, match notifications
12. **Settings** - Email config, Firestore integration
13. **All pages** - Error handling, loading states, responsive design

---

## Technical Recommendations

### State Management
```typescript
// Option 1: Context API (simple, built-in)
// Good for: Filters, user preferences, theme

// Option 2: Zustand (recommended)
// Good for: Complex state, scraper status, cached data

// Option 3: React Query / SWR (highly recommended)
// Good for: API data fetching, caching, real-time updates
```

### Data Fetching Strategy
```typescript
// Use SWR for automatic caching and revalidation
import useSWR from 'swr';

function useProperties() {
  const { data, error, mutate } = useSWR('/api/data/all', fetcher, {
    refreshInterval: 30000, // Refresh every 30 seconds
    revalidateOnFocus: true,
    dedupingInterval: 5000
  });

  return { properties: data, loading: !data && !error, error, refresh: mutate };
}
```

### Real-time Updates
```typescript
// For Scraper Control page, use polling with SWR
import useSWR from 'swr';

function useScraperStatus() {
  const { data: status } = useSWR(
    '/api/scrape/status',
    fetcher,
    {
      refreshInterval: 3000, // Poll every 3 seconds
      refreshWhenHidden: false, // Stop polling when tab is hidden
      refreshWhenOffline: false
    }
  );

  return status;
}
```

### Responsive Design Breakpoints
```css
/* Tailwind CSS breakpoints (recommended) */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */

/* Page-specific considerations */
Properties: 3 columns (lg), 2 columns (md), 1 column (sm)
Dashboard: 4 cards (lg), 2 cards (md), 1 card (sm)
Scraper Control: Hide sidebar on mobile, show as modal
```

---

## Common Pitfalls to Avoid

### ❌ Don't: Create separate pages for every endpoint
```
/properties/search
/properties/filter
/properties/advanced-search
/properties/export
```

### ✅ Do: Use one page with component composition
```
/properties (handles all search, filter, export via components)
```

---

### ❌ Don't: Poll too frequently
```typescript
// This will hammer your API
const { data } = useSWR('/api/scrape/status', fetcher, {
  refreshInterval: 500 // Every 0.5 seconds - TOO MUCH!
});
```

### ✅ Do: Poll at reasonable intervals
```typescript
// Much better
const { data } = useSWR('/api/scrape/status', fetcher, {
  refreshInterval: 3000, // Every 3 seconds
  refreshWhenHidden: false // Stop when user is on different tab
});
```

---

### ❌ Don't: Load all properties at once
```typescript
// Will crash browser with 10,000+ properties
const { data } = await fetch('/api/data/all');
```

### ✅ Do: Use pagination
```typescript
const { data } = await fetch('/api/data/all?limit=50&offset=0');
```

---

## Summary Checklist

### For Your Frontend Developer

- [ ] Read this entire guide (bookmark for reference)
- [ ] Set up 5 pages: Dashboard, Properties, Scraper Control, Saved Searches, Settings
- [ ] Create shared components (PropertyCard, FilterPanel, etc.)
- [ ] Create custom hooks (useProperties, useScraper, useSites, etc.)
- [ ] Implement navigation with admin-only protection
- [ ] Use SWR or React Query for data fetching
- [ ] Implement polling for real-time updates (Scraper Control page)
- [ ] Add loading states and error handling to all pages
- [ ] Make responsive (mobile, tablet, desktop)
- [ ] Test user flows (end user property search, admin scraping)

---

## Quick Reference

| When you need to... | Use this page | Endpoints |
|---------------------|---------------|-----------|
| Show overview stats | Dashboard | `/api/stats/overview`, `/api/health` |
| Browse properties | Properties | `/api/data/all`, `/api/data/search` |
| Start a scrape | Scraper Control | `POST /api/scrape/start` |
| Monitor scrape progress | Scraper Control | `/api/scrape/status`, `/api/logs` |
| Save a search | Properties → Saved Searches | `POST /api/saved-searches/create` |
| Manage email alerts | Saved Searches | `/api/saved-searches/{id}/settings` |
| Configure SMTP | Settings | `/api/email/settings` |
| Add/remove sites | Settings | `/api/sites/add`, `/api/sites/{site}` |
| Export data | Properties | `/api/data/export/csv` |

---

## Support & Questions

If your frontend developer has questions:
1. Refer to `docs/FRONTEND_INTEGRATION.md` for detailed API documentation
2. Refer to `docs/POSTMAN_GUIDE.md` for API testing examples
3. Check the Postman collection: `docs/Nigerian_Real_Estate_API.postman_collection.json`
4. Test endpoints using curl (examples in API_QUICKSTART.md)

---

**End of Guide**

This structure consolidates 68 endpoints into 5 intuitive, user-focused pages that align with real-world workflows. Your frontend developer should be able to reduce from 20+ pages to 5 pages easily while maintaining all functionality and improving user experience.
