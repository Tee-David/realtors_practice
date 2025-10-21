# Branch Protection Setup Guide

## Protecting the Main Branch

To prevent accidental pushes and ensure code quality, follow these steps to protect your main branch on GitHub:

### Step 1: Navigate to Branch Protection Settings

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/realtors_practice`
2. Click **"Settings"** tab (top menu)
3. In left sidebar, click **"Branches"** (under "Code and automation")
4. Under "Branch protection rules", click **"Add branch protection rule"**

### Step 2: Configure Protection Rules

**Branch name pattern:** `main`

**Recommended Settings:**

✅ **Require pull request reviews before merging**
   - Require 1 approval before merging
   - Dismiss stale pull request approvals when new commits are pushed

✅ **Require status checks to pass before merging**
   - Add status checks: `build`, `test` (if you have CI/CD)

✅ **Require branches to be up to date before merging**
   - Ensures branch is synced with main before merge

✅ **Require conversation resolution before merging**
   - All review comments must be resolved

⚠️ **Do not allow force pushes**
   - Prevents rewriting history

⚠️ **Do not allow deletions**
   - Prevents accidental branch deletion

### Step 3: Additional Options (Optional)

- **Require signed commits** - Extra security layer
- **Include administrators** - Apply rules to repository admins too
- **Restrict who can push to matching branches** - Limit to specific users/teams

### Step 4: Save Changes

Click **"Create"** or **"Save changes"**

---

## Working with Protected Branches

### Workflow for Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

3. **Push to GitHub:**
   ```bash
   git push -u origin feature/new-feature
   ```

4. **Create Pull Request:**
   - Go to GitHub repository
   - Click "Compare & pull request"
   - Add description of changes
   - Request review (if required)
   - Click "Create pull request"

5. **Merge after approval:**
   - Once approved and checks pass
   - Click "Merge pull request"
   - Delete feature branch

---

## Quick Commands Reference

```bash
# Check current branch
git branch

# Create new feature branch
git checkout -b feature/your-feature-name

# Switch between branches
git checkout main
git checkout feature/your-feature-name

# Update local main with remote changes
git checkout main
git pull origin main

# Rebase feature branch with latest main
git checkout feature/your-feature-name
git rebase main

# Delete local branch after merge
git branch -d feature/your-feature-name

# Delete remote branch after merge
git push origin --delete feature/your-feature-name
```

---

## For Collaborators

When working with others:

1. **Always create a feature branch**
2. **Never commit directly to main**
3. **Keep pull requests focused** (one feature per PR)
4. **Write clear commit messages**
5. **Request reviews from teammates**
6. **Resolve all comments before merging**

---

## Emergency: Hotfix to Main

If you need to make an urgent fix:

```bash
# Create hotfix branch
git checkout -b hotfix/critical-bug

# Make fix and commit
git add .
git commit -m "hotfix: Fix critical bug"

# Push and create PR
git push -u origin hotfix/critical-bug

# Create PR on GitHub with "hotfix" label
# Get expedited review and merge
```

---

**Note:** Branch protection ensures code quality and prevents accidental changes to production code. Always use pull requests for changes to main branch.
