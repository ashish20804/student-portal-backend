# Report Generation - Year-wise Data Fix

## Changes Made

### Backend (report_routes.py)

#### 1. Placement Reports
**Added year filtering to placement-stats endpoint:**
- Now accepts `year` parameter
- Filters placed students by year
- Department distribution pie chart filtered by year
- Year-wise trend bar chart shows actual placement years from database

**Routes:**
- `GET /admin/reports/placement-stats?year=2026` - Department distribution for specific year
- `GET /admin/reports/placement/year-wise` - Year-wise trend data
- `GET /admin/reports/placement?year=2026` - Detailed placement records

#### 2. Higher Studies Reports
**Added year filtering and new stats endpoint:**
- Extracts year from `applicationDate` field
- New endpoint: `/admin/reports/higher-studies-stats?year=2026`
- Department distribution filtered by application year
- Year-wise trend based on actual application dates

**Routes:**
- `GET /admin/reports/higher-studies-stats?year=2026` - Department distribution
- `GET /admin/reports/higher-studies/year-wise` - Year-wise trend
- `GET /admin/reports/higher-studies?year=2026` - Detailed records with actual years

#### 3. Activity Reports
**Added category-based grouping (no date field in Activity model):**
- Bar chart shows category-wise distribution (Sports, Cultural, Technical, etc.)
- Pie chart shows department-wise participation
- New endpoint: `/admin/reports/activity-stats`

**Routes:**
- `GET /admin/reports/activity-stats` - Department distribution
- `GET /admin/reports/activity/year-wise` - Category-wise distribution
- `GET /admin/reports/activity?year=2026` - Detailed records

### Frontend (reports.js)

#### 1. Separate API Calls
**Changed from single stats call to two separate calls:**
- **Trend Data:** Year-wise or category-wise for bar chart
- **Stats Data:** Department distribution for pie chart

#### 2. Year Parameter Passing
- Year filter now passed to stats endpoints
- Ensures pie chart shows data for selected year only

#### 3. Dynamic Chart Titles
- Bar chart title changes based on report type:
  - Placement/Higher Studies: "Year-wise Distribution"
  - Activities: "Category-wise Distribution"
- Pie chart always shows: "Department-wise Distribution"

#### 4. Enhanced Chart Options
- Added proper titles to both charts
- Y-axis starts at zero with step size of 1
- Legend positioned at bottom for pie chart
- Better color palette for multiple departments

#### 5. Generated Date Display
- Automatically shows current date when page loads
- Updates when report type changes
- Format: "Month Day, Year" (e.g., "March 11, 2026")

## How It Works Now

### Placement Reports:
1. Select "Placement Records" and year "2026"
2. Click "Generate"
3. **Bar Chart:** Shows placements per year (2024, 2025, 2026, etc.)
4. **Pie Chart:** Shows department distribution for 2026 only
5. **Table:** Lists all placements from 2026

### Higher Studies Reports:
1. Select "Higher Studies" and year "2026"
2. Click "Generate"
3. **Bar Chart:** Shows applications per year based on applicationDate
4. **Pie Chart:** Shows department distribution for 2026 applications
5. **Table:** Lists all higher studies records from 2026

### Activity Reports:
1. Select "Student Activities" and year "2026"
2. Click "Generate"
3. **Bar Chart:** Shows activities by category (Sports, Cultural, Technical, etc.)
4. **Pie Chart:** Shows department-wise participation
5. **Table:** Lists all activities

## Database Fields Used

### Placement:
- `placementYear` - Used for year filtering and trend chart

### HigherStudies:
- `applicationDate` - Extracts year for filtering and trend chart

### Activity:
- `category` - Used for bar chart (no date field available)
- Department from Student table for pie chart

## API Response Format

### Trend Data (Bar Chart):
```json
{
  "labels": ["2024", "2025", "2026"],
  "counts": [15, 23, 31]
}
```

### Stats Data (Pie Chart):
```json
{
  "distLabels": ["CSE", "ECE", "Mechanical"],
  "distData": [45, 30, 25]
}
```

## Benefits

✅ Year filter now properly affects both charts and table
✅ Pie chart shows department distribution for selected year only
✅ Bar chart shows actual year-wise trends from database
✅ Activity reports use category grouping (since no date field)
✅ Charts have proper titles and labels
✅ Generated date automatically displayed
✅ Better visual representation with enhanced chart options

## Testing

### Test Placement Report:
1. Add placements for different years (2024, 2025, 2026)
2. Select year 2026
3. Verify bar chart shows all years
4. Verify pie chart shows only 2026 departments
5. Verify table shows only 2026 records

### Test Higher Studies Report:
1. Add higher studies with different application dates
2. Select year 2026
3. Verify bar chart shows years from applicationDate
4. Verify pie chart shows only 2026 departments
5. Verify table shows only 2026 records

### Test Activity Report:
1. Add activities with different categories
2. Click Generate
3. Verify bar chart shows categories (Sports, Cultural, etc.)
4. Verify pie chart shows department distribution
5. Verify table lists all activities
