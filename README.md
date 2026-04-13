# Git Repository Analyzer

Generate a comprehensive engineering-style HTML report analyzing Git repository health and activity patterns.

## Installation

```bash
npx skills add git-repo-analyze
```

## Usage

After installation, you can use the skill in Claude Code:

```bash
# Analyze current repository
git-analyze

# Analyze specific repository
git-analyze /path/to/repo
```

## Features

- **Change Hotspots**: Most frequently modified files
- **Bus Factor**: Contributor distribution and risk analysis
- **Bug Clusters**: Files with most bug-related commits (supports English and Chinese keywords)
- **Commit Rhythm**: Monthly commit velocity trends
- **Crisis Mode**: Revert/hotfix frequency indicators
- **Commit Quality**: Message clarity analysis detecting vague commits and semantic commit patterns

## Requirements

- Python 3.x
- Git repository

## Output

Generates an HTML file (`git-analysis-report.html`) with:

- Repository overview and summary stats
- Change hotspots visualization
- Bug clusters identification
- High-risk files (intersection of hotspots and bug clusters)
- Bus factor analysis with contributor distribution
- Crisis indicators (reverts/hotfixes)
- Commit quality grading
- Monthly commit velocity chart

## License

MIT
