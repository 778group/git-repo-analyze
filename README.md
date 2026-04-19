# Git Repository Analyzer

Generate a comprehensive engineering-style HTML report analyzing Git repository health and activity patterns.

## Installation

```bash
npx skills add 778group/git-repo-analyze
```

## Usage

After installation, you can use the skill in Claude Code:

```bash
# Analyze current repository
git-repo-analyze

# Analyze specific repository
git-repo-analyze /path/to/repo
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

## Inspiration

This skill is inspired by the WeChat article: [《我在阅读任何代码之前运行的 Git 命令》](https://mp.weixin.qq.com/s/cVCjb246T31eCwmYRORsQw)

## License

MIT
