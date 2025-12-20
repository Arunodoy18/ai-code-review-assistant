# Demo Guide & Screenshots

This guide walks through the key features of the AI Code Review Assistant with visual examples.

## 🎯 Quick Overview

**AI Code Review Assistant** is an intelligent code review platform that automatically analyzes pull requests using:
- 24+ built-in rules across 6 categories
- AI-powered analysis with GPT-4 or Claude
- Real-time GitHub webhook integration
- Customizable rule configuration per project

---

## 📸 Screenshots

### 1. Dashboard

**Main dashboard showing recent analysis runs**

Features visible:
- Real-time status updates (auto-refreshes every 10 seconds)
- Summary statistics cards with gradients
- Filter by status (All, Pending, Running, Completed, Failed)
- Filter by time period (24h, 7d, 30d, All)
- Quick access to individual run details
- Dark/Light mode toggle

**Key Metrics:**
- Total runs
- Completed runs
- Failed runs
- Average findings per run

### 2. Run Detail View

**Detailed analysis results for a specific PR**

Features visible:
- PR metadata (title, author, timestamps)
- Severity breakdown cards with counts
- Category filters (Security, Bug, Performance, etc.)
- Findings grouped by file
- Code snippets with syntax highlighting
- Line numbers for precise location
- AI-generated suggestions
- Re-run analysis button

**Finding Card Elements:**
- Severity badge (Critical/High/Medium/Low/Info)
- Category icon and label
- Rule ID
- Description and suggestion
- Code snippet with context

### 3. Projects View

**Repository management and configuration**

Features visible:
- Project cards in grid layout
- Repository name and GitHub link
- Recent analysis count
- Status indicators
- "View on GitHub" buttons
- Last updated timestamps

### 4. Configuration UI

**Rule customization per project**

Features visible:
- Project selector dropdown
- Search and filter rules
- Toggle switches for enable/disable
- Severity override dropdowns
- Category-based filtering
- Analysis settings (max findings, file extensions)
- Rule descriptions and IDs
- Category icons

**Rule Categories:**
- 🔒 Security (8 rules)
- 🐛 Bug (3 rules)
- ⚡ Performance (3 rules)
- ✨ Best Practice (6 rules)
- 🎨 Style (3 rules)
- 📝 Documentation (1 rule)

### 5. Dark Mode

**Seamless theme switching**

Features:
- Persists to localStorage
- Smooth transitions
- All components adapted
- Toggle in header

---

## 🎬 Demo Workflow

### Step 1: Install GitHub App

1. Create GitHub App in your organization
2. Configure webhook URL: `https://your-backend.com/api/webhooks/github`
3. Set permissions:
   - Pull requests: Read & Write
   - Repository contents: Read
   - Webhooks: Read & Write
4. Subscribe to events:
   - Pull request opened
   - Pull request synchronized
   - Pull request closed
5. Generate and save private key

### Step 2: Add Project

Projects are automatically created when the GitHub App receives webhooks. Alternatively:

```bash
POST /api/projects
{
  "name": "my-repo",
  "github_repo_full_name": "owner/my-repo",
  "github_installation_id": 123456
}
```

### Step 3: Configure Rules

1. Navigate to Configuration page
2. Select your project
3. Enable/disable rules as needed
4. Override severities
5. Adjust analysis settings

### Step 4: Open a Pull Request

When you open a PR in the configured repository:

1. GitHub sends webhook to backend
2. Backend creates new AnalysisRun
3. Celery task starts background analysis
4. Dashboard shows "Running" status
5. Analysis completes in 30-60 seconds
6. Dashboard updates to "Completed"
7. Findings appear in Run Detail view

### Step 5: Review Findings

1. Click on completed run
2. Review findings by severity
3. Filter by category
4. See code snippets with line numbers
5. Read AI suggestions
6. Address issues in your code

### Step 6: Re-run Analysis

After fixing issues:

1. Click "Re-run Analysis" button
2. Analysis runs again on same PR
3. Verify issues are resolved
4. Compare finding counts

---

## 🔧 Technical Demo

### API Endpoints Demo

```bash
# Health check
curl http://localhost:8000/api/health/liveness
curl http://localhost:8000/api/health/readiness

# List analysis runs
curl http://localhost:8000/api/analysis/runs?limit=10

# Get run details
curl http://localhost:8000/api/analysis/runs/1

# Get findings
curl http://localhost:8000/api/analysis/runs/1/findings?severity=high

# List projects
curl http://localhost:8000/api/projects/

# Get available rules
curl http://localhost:8000/api/config/rules

# Get project configuration
curl http://localhost:8000/api/config/projects/1

# Enable a rule
curl -X POST http://localhost:8000/api/config/projects/1/rules/security-sql-injection/enable

# Update severity
curl -X POST http://localhost:8000/api/config/projects/1/rules/security-sql-injection/severity \
  -H "Content-Type: application/json" \
  -d '{"severity": "critical"}'
```

### Webhook Testing

Use the built-in webhook tester:

```python
from backend.tests.test_webhooks import WebhookTester

tester = WebhookTester()

# Simulate PR opened event
response = await tester.simulate_pr_opened(
    repo_name="owner/repo",
    pr_number=123,
    pr_title="Add new feature",
    files_changed=5
)
```

### Database Query Examples

```python
from app.database import SessionLocal
from app.models import AnalysisRun, Finding, Project

db = SessionLocal()

# Get critical findings
critical = db.query(Finding).filter(
    Finding.severity == "critical"
).all()

# Get recent runs
recent = db.query(AnalysisRun).order_by(
    AnalysisRun.started_at.desc()
).limit(10).all()

# Get findings by category
security_findings = db.query(Finding).filter(
    Finding.category == "security"
).count()
```

---

## 📊 Performance Benchmarks

### Analysis Speed

- **Small PR** (1-3 files): 10-20 seconds
- **Medium PR** (4-10 files): 20-40 seconds
- **Large PR** (10+ files): 40-90 seconds

### API Response Times (with caching)

- **Dashboard load**: < 100ms
- **Run detail**: < 50ms
- **Projects list**: < 30ms
- **Configuration**: < 200ms

### Database Performance

With indexes:
- **Find by run_id**: < 5ms
- **Group by severity**: < 10ms
- **Recent runs query**: < 15ms

---

## 🎥 Creating Demo Video

### Recommended Tools

- **Screen Recording**: 
  - OBS Studio (free, all platforms)
  - ScreenFlow (Mac)
  - Camtasia (paid, professional)
  - ShareX (Windows, free)

- **GIF Creation**:
  - LICEcap (free, lightweight)
  - ScreenToGif (Windows, free)
  - Gifox (Mac, $14)

### Demo Script (3-5 minutes)

1. **Intro** (15 sec)
   - Show landing page
   - Explain purpose

2. **Dashboard** (30 sec)
   - Show real-time updates
   - Highlight key metrics
   - Demonstrate filters

3. **Open PR** (45 sec)
   - Switch to GitHub
   - Open a test PR with intentional issues
   - Return to dashboard
   - Show run appearing

4. **Analysis Results** (60 sec)
   - Click into completed run
   - Show findings breakdown
   - Filter by severity
   - Demonstrate code snippets
   - Read AI suggestion

5. **Configuration** (30 sec)
   - Navigate to config
   - Toggle a rule
   - Change severity
   - Save changes

6. **Re-run** (20 sec)
   - Return to run detail
   - Click re-run
   - Show status update

7. **Projects** (15 sec)
   - Show projects view
   - Quick overview

8. **Dark Mode** (10 sec)
   - Toggle theme
   - Show adaptability

9. **Outro** (15 sec)
   - Recap features
   - Show documentation links

---

## 📷 Screenshot Checklist

For README and documentation:

- [ ] Dashboard with multiple runs
- [ ] Run detail showing findings
- [ ] Critical severity finding example
- [ ] Configuration UI with rules
- [ ] Projects page
- [ ] Dark mode comparison
- [ ] GitHub App installation page
- [ ] API documentation (/docs endpoint)

### Screenshot Tips

1. **Use realistic data**: Seed database with meaningful examples
2. **Show variety**: Different severities, categories, and statuses
3. **Clean UI**: Remove test data, ensure consistent styling
4. **Highlight features**: Use arrows/boxes to point out key elements
5. **Consistent size**: 1920x1080 or 1440x900 for consistency
6. **Proper naming**: `dashboard-overview.png`, `finding-detail.png`

---

## 🚀 Live Demo Sites

### For Potential Deployments

**Option 1: Railway**
- Deploy in < 5 minutes
- Automatic HTTPS
- Custom domain support
- URL: `ai-code-review.up.railway.app`

**Option 2: Render**
- Free tier available
- PostgreSQL included
- URL: `ai-code-review.onrender.com`

**Option 3: Vercel (Frontend) + Railway (Backend)**
- Optimal performance
- Global CDN for frontend
- URLs: `ai-code-review.vercel.app` + `api.railway.app`

### Demo Data Script

```bash
cd backend
python seed_demo_data.py
```

This creates:
- 5 sample projects
- 20 analysis runs (various statuses)
- 100+ findings across all categories
- Realistic PR metadata

---

## 🎨 Visual Assets

### Logo Ideas

Create a logo that represents:
- Code review (magnifying glass + code symbol)
- AI/ML (brain, neural network)
- Automation (gear, lightning bolt)

Recommended tools:
- Figma (free for basics)
- Canva (templates available)
- LogoMakr (simple, free)

### Color Scheme

Current theme:
```css
Primary Blue: #0ea5e9
Success Green: #10b981
Warning Yellow: #f59e0b
Error Red: #ef4444
Neutral Gray: #64748b
Dark Background: #0f172a
```

---

## 📝 Documentation Videos

Consider creating separate shorts for:
1. GitHub App setup (3 min)
2. Installation & configuration (5 min)
3. Using the configuration UI (3 min)
4. Understanding findings (4 min)
5. Custom rule creation (5 min)

---

## 🎬 Example Demo Scenarios

### Scenario 1: Security Issues

1. Open PR with SQL injection vulnerability
2. Show critical security finding
3. Explain the issue
4. Show AI suggestion
5. Fix the code
6. Re-run analysis
7. Verify issue resolved

### Scenario 2: Performance Problems

1. Open PR with inefficient database queries
2. Show performance findings
3. Highlight N+1 query problem
4. Show suggestion to use joins
5. Compare before/after

### Scenario 3: Code Quality

1. Open PR with style violations
2. Show multiple low-severity findings
3. Demonstrate bulk review
4. Configure rule to ignore certain patterns
5. Re-run with updated config

---

## 💡 Tips for Effective Demos

1. **Practice**: Run through several times
2. **Prepare data**: Pre-create interesting PRs
3. **Clear narration**: Explain what you're doing
4. **Show value**: Emphasize time savings
5. **Keep it short**: 3-5 minutes max for attention
6. **End with CTA**: Link to docs, repo, or demo

---

## 📦 Demo Package

Create a demo package including:
- README with screenshots
- DEMO.md (this file)
- Sample PRs in `/demo` branch
- Test webhook payloads
- Postman collection
- Video links
- Docker compose for instant setup

This enables anyone to run a full demo in < 10 minutes.
