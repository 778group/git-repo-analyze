---
name: git-repo-analyze
description: Generate a comprehensive engineering-style HTML report analyzing Git repository health and activity patterns.
---

# Git Repository Analysis

Generate a comprehensive engineering-style HTML report analyzing Git repository health and activity patterns.

## Usage

### As a Claude Skill

```bash
# Install the skill
npx skills add git-repo-analyze

# Then use in Claude Code
git-analyze

# Analyze specific repository
git-analyze /path/to/repo
```

### Direct Script Usage

```bash
# Using npm script
npm run analyze

# Or run directly with Python
python3 scripts/analyze.py

# Analyze specific repository
python3 scripts/analyze.py /path/to/repo
```

## Output

Generates an HTML file with:

- **Change Hotspots**: Most frequently modified files
- **Bus Factor**: Contributor distribution and risk analysis
- **Bug Clusters**: Files with most bug-related commits (supports English and Chinese keywords like "修复", "重构")
- **Commit Rhythm**: Monthly commit velocity trends
- **Crisis Mode**: Revert/hotfix frequency indicators
- **Commit Quality**: Message clarity analysis detecting vague commits ("fix", "ttt", "更新") and semantic commit patterns

## Implementation

When invoked:

1. Check if we're in a git repository or use provided path
2. Run git analysis commands
3. Generate Flat Engineering Blueprint style HTML report
4. Save to `git-analysis-report.html` and open it

### Commands to run:

```bash
# Change hotspots (top 20 files)
git log --name-only --pretty=format: | sort | uniq -c | sort -nr | head -20

# Bus factor (contributor stats)
git shortlog -sn --all

# Recent contributors (last 6 months)
git shortlog -sn --all --since="6 months ago"

# Bug clusters (English and Chinese keywords)
git log --all --grep="bug" --grep="fix" --grep="broken" --grep="修复" --grep="重构" -i --name-only --pretty=format:

# Commit rhythm by month (current year)
for month in $(date +%Y)-{01..12}; do
  count=$(git rev-list --count --all --since="${month}-01" --until="${month}-31" 2>/dev/null || echo 0)
  echo "$month: $count"
done

# Crisis mode (reverts/hotfixes)
git log --all --grep="revert" --grep="hotfix" --grep="rollback" --grep="emergency" -i --oneline

# Commit quality analysis
# Detects vague commits: "fix", "update", "test", "ttt", "ok", "done"
# Detects Chinese vague commits: "修复", "更新", "测试", "重构", "优化", "临时", "搞定"
# Detects semantic patterns: "feat:", "fix:", "docs:", "重构:", "新增:", "修复:"
```

### Commit Quality Analysis

The tool analyzes commit message quality by detecting:

**Low Quality Patterns:**

- Too short: "fix", "f", "update", "u", "test", "t"
- Vague: "wip", "temp", "ok", "done", "debug"
- Chinese vague: "修复", "修", "更新", "重构", "优化", "调整", "搞定"

**Semantic Patterns (Positive):**

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Chinese semantic: `新增:`, `修复:`, `文档:`, `重构:`, `测试:`, `性能:`

**Quality Grade:**

- A: Excellent (>90% well-formed commits)
- B: Good (70-90%)
- C: Needs Improvement (50-70%)
- D: Poor (<50%)

### HTML Report Structure

Follow Flat Engineering Blueprint design:

- No shadows, gradients, glassmorphism
- 1px or 2px solid borders
- Monospace for code/data, system font for UI
- CSS variables for consistent coloring
- Grid/Flex strict alignment
- Information-dense layout

Sections:

1. **Header**: Repository name, analysis date, summary stats
2. **Change Hotspots**: Bar chart of top 20 files by change frequency
3. **Bug Clusters**: Files with bug-related commits (English + Chinese)
4. **High Risk Files**: Intersection of hotspots and bug clusters
5. **Bus Factor**: Contributor distribution table, risk indicators
6. **Crisis Indicators**: Revert/hotfix list and frequency metrics
7. **Commit Quality**: Grade, semantic commit percentage, vague message examples
8. **Commit Rhythm**: Monthly commit velocity chart
