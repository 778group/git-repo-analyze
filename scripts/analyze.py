#!/usr/bin/env python3
"""
Git Repository Analyzer
Generates Flat Engineering Blueprint style HTML report for git repository analysis.
"""

import subprocess
import re
import os
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from html import escape


def run_git_command(cmd, cwd=None):
    """Execute git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return ""


def get_repo_name(cwd=None):
    """Get repository name from remote or directory."""
    remote = run_git_command("git remote get-url origin", cwd)
    if remote:
        # Extract name from URL
        name = remote.split('/')[-1].replace('.git', '')
        return name
    return os.path.basename(cwd or os.getcwd())


def analyze_change_hotspots(cwd=None, since=None):
    """Analyze most frequently changed files."""
    since_flag = f'--since="{since}"' if since else ""
    cmd = f'git log --name-only --pretty=format: {since_flag}'
    output = run_git_command(cmd, cwd)

    files = [f.strip() for f in output.split('\n') if f.strip() and not f.startswith('commit ')]
    file_counts = Counter(files)

    return file_counts.most_common(20)


def analyze_bus_factor(cwd=None):
    """Analyze contributor distribution."""
    # All time contributors
    cmd = 'git shortlog -sn --all --no-merges'
    output = run_git_command(cmd, cwd)

    contributors = []
    total_commits = 0
    for line in output.split('\n'):
        match = re.match(r'\s*(\d+)\s+(.+)', line)
        if match:
            count, name = match.groups()
            contributors.append({'name': name.strip(), 'commits': int(count)})
            total_commits += int(count)

    # Recent contributors (6 months)
    cmd = 'git shortlog -sn --all --no-merges --since="6 months ago"'
    recent_output = run_git_command(cmd, cwd)

    recent_contributors = {}
    for line in recent_output.split('\n'):
        match = re.match(r'\s*(\d+)\s+(.+)', line)
        if match:
            count, name = match.groups()
            recent_contributors[name.strip()] = int(count)

    # Calculate bus factor (how many people account for 50% of commits)
    cumulative = 0
    bus_factor = 0
    for c in contributors:
        cumulative += c['commits']
        bus_factor += 1
        if cumulative >= total_commits * 0.5:
            break

    return {
        'all_time': contributors,
        'recent': recent_contributors,
        'total_commits': total_commits,
        'bus_factor': bus_factor,
        'active_recent': len(recent_contributors)
    }


def analyze_bug_clusters(cwd=None):
    """Analyze files with bug-related commits (including Chinese keywords)."""
    # English and Chinese bug-related keywords
    cmd = 'git log --all --grep="bug" --grep="fix" --grep="broken" --grep="repair" --grep="issue" --grep="error" --grep="crash" --grep="fail" -i --name-only --pretty=format:'
    output = run_git_command(cmd, cwd)

    # Also search for Chinese bug keywords
    cmd_cn = 'git log --all --grep="修复" --grep="bug" --grep="问题" --grep="错误" --grep="崩溃" --grep="失败" --grep="解决" --grep="修正" --grep="调试" --name-only --pretty=format:'
    output_cn = run_git_command(cmd_cn, cwd)

    files = [f.strip() for f in output.split('\n') if f.strip()]
    files_cn = [f.strip() for f in output_cn.split('\n') if f.strip()]

    all_files = files + files_cn
    file_counts = Counter(all_files)

    return file_counts.most_common(20)


def analyze_commit_rhythm(cwd=None):
    """Analyze commit velocity by month."""
    current_year = datetime.now().year
    months = []

    for month in range(1, 13):
        month_str = f"{current_year}-{month:02d}"
        since = f"{month_str}-01"

        # Calculate last day of month
        if month == 12:
            next_month = f"{current_year + 1}-01-01"
        else:
            next_month = f"{current_year}-{month + 1:02d}-01"

        cmd = f'git rev-list --count --all --since="{since}" --until="{next_month}"'
        count = run_git_command(cmd, cwd)

        try:
            count = int(count) if count else 0
        except:
            count = 0

        months.append({
            'month': month_str,
            'count': count
        })

    return months


def analyze_crisis_mode(cwd=None):
    """Analyze revert/hotfix frequency."""
    cmd = 'git log --all --grep="revert" --grep="hotfix" --grep="rollback" --grep="emergency" -i --oneline'
    output = run_git_command(cmd, cwd)

    incidents = []
    for line in output.split('\n'):
        if line.strip():
            # Parse commit hash and message
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                hash_id, message = parts
                incidents.append({
                    'hash': hash_id,
                    'message': message
                })

    # Calculate frequency
    one_year_ago = datetime.now() - timedelta(days=365)
    recent_incidents = len(incidents)  # Simplified - should filter by date

    return {
        'incidents': incidents[:20],  # Last 20
        'total': len(incidents),
        'recent_count': recent_incidents
    }


def analyze_commit_quality(cwd=None):
    """Analyze commit message quality and patterns."""
    # Get all commit messages
    cmd = 'git log --all --format="%H|%s|%an|%ad" --date=short'
    output = run_git_command(cmd, cwd)

    # Low quality patterns (vague, meaningless commits)
    vague_patterns = [
        r'^(fix|fixing|fixed|f)$',  # Just "fix"
        r'^(update|upd|u)$',  # Just "update"
        r'^(test|testing|t|ttt)$',  # Test commits
        r'^(wip|work in progress)$',  # WIP
        r'^(temp|tmp|temporary)$',  # Temporary
        r'^(ok|done|yes|y)$',  # Meaningless acknowledgments
        r'^(debug|dbg)$',  # Debug commits
        r'^(misc|various|stuff)$',  # Vague
        r'^(refactor|r)$',  # Just "refactor"
        r'^(change|modify|adjust|edit)$',  # Generic verbs
        r'^[\.\-]+$',  # Just dots or dashes
        r'^\d+$',  # Just numbers
        r'^test\d*$',  # test1, test2, etc.
        r'^(patch|update|commit)$',  # Generic git words
    ]

    # Chinese vague patterns
    chinese_vague = [
        r'^(修复|修|fix|修改|改)$',  # Just "fix"
        r'^(更新|更|upd)$',  # Just "update"
        r'^(测试|测|试)$',  # Just "test"
        r'^(重构|构)$',  # Just "refactor"
        r'^(优化|化)$',  # Just "optimize"
        r'^(调整|调整一下)$',  # Just "adjust"
        r'^(提交|交|commit)$',  # Just "commit"
        r'^(临时|暂|temp)$',  # Temporary
        r'^(搞定|好了|完成|完)$',  # Done-ish
        r'^(debug|调试|调)$',  # Debug
        r'^ok|好的|行|可以$',  # Acknowledgments
        r'^[\s\.\-]+$',  # Whitespace or punctuation
    ]

    # Good patterns (semantic commits)
    semantic_patterns = [
        r'^(feat|feature)[\(:]',  # feat: or feat(...)
        r'^(fix|bugfix)[\(:]',  # fix: or fix(...)
        r'^(docs|doc)[\(:]',  # docs:
        r'^(style)[\(:]',  # style:
        r'^(refactor)[\(:]',  # refactor:
        r'^(test)[\(:]',  # test:
        r'^(chore)[\(:]',  # chore:
        r'^(perf|performance)[\(:]',  # perf:
        r'^(ci|build|deploy)[\(:]',  # ci:, build:
        r'^(revert)[\(:]',  # revert:
        r'^(安全|新增|修复|文档|样式|重构|测试|构建|性能|回滚)[\(:：]',  # Chinese semantic
    ]

    commits_analyzed = 0
    vague_commits = []
    semantic_commits = 0
    short_commits = 0  # Less than 10 chars
    quality_score = 100

    for line in output.split('\n'):
        if not line.strip():
            continue

        parts = line.split('|', 3)
        if len(parts) < 4:
            continue

        hash_id, subject, author, date = parts
        commits_analyzed += 1
        subject_lower = subject.lower().strip()

        # Check for vague commits
        is_vague = False
        for pattern in vague_patterns:
            if re.match(pattern, subject_lower, re.IGNORECASE):
                is_vague = True
                break

        if not is_vague:
            for pattern in chinese_vague:
                if re.match(pattern, subject_lower):
                    is_vague = True
                    break

        if is_vague:
            vague_commits.append({
                'hash': hash_id[:7],
                'message': subject,
                'author': author,
                'date': date
            })
            quality_score -= 2

        # Check for semantic commits
        is_semantic = False
        for pattern in semantic_patterns:
            if re.match(pattern, subject_lower, re.IGNORECASE):
                is_semantic = True
                break

        if is_semantic:
            semantic_commits += 1

        # Check for very short commits
        if len(subject_lower) < 10:
            short_commits += 1
            if len(subject_lower) < 5:
                quality_score -= 1

    # Calculate percentages
    vague_pct = (len(vague_commits) / commits_analyzed * 100) if commits_analyzed else 0
    semantic_pct = (semantic_commits / commits_analyzed * 100) if commits_analyzed else 0

    # Quality grade
    if quality_score >= 90:
        grade = 'A'
    elif quality_score >= 70:
        grade = 'B'
    elif quality_score >= 50:
        grade = 'C'
    else:
        grade = 'D'

    return {
        'total_commits': commits_analyzed,
        'vague_count': len(vague_commits),
        'vague_pct': round(vague_pct, 1),
        'vague_examples': vague_commits[:10],
        'semantic_count': semantic_commits,
        'semantic_pct': round(semantic_pct, 1),
        'short_commits': short_commits,
        'quality_score': max(0, quality_score),
        'grade': grade
    }


def calculate_risk_score(hotspots, bugs):
    """Calculate risk score by intersecting hotspots and bug clusters."""
    hotspot_files = {f: c for f, c in hotspots}
    bug_files = {f: c for f, c in bugs}

    risk_files = []
    for file in set(hotspot_files.keys()) & set(bug_files.keys()):
        risk_files.append({
            'file': file,
            'changes': hotspot_files[file],
            'bugs': bug_files[file],
            'score': hotspot_files[file] + bug_files[file] * 2  # Bug weight
        })

    return sorted(risk_files, key=lambda x: x['score'], reverse=True)[:10]


def generate_html(report_data):
    """Generate Flat Engineering Blueprint style HTML report."""

    repo_name = report_data['repo_name']
    hotspots = report_data['hotspots']
    bus_factor = report_data['bus_factor']
    bugs = report_data['bugs']
    rhythm = report_data['rhythm']
    crisis = report_data['crisis']
    risks = report_data['risks']
    quality = report_data['commit_quality']

    max_hotspot = hotspots[0][1] if hotspots else 1
    max_rhythm = max(r['count'] for r in rhythm) if rhythm else 1

    # Build contributors table rows
    contributor_rows = ""
    for c in bus_factor['all_time'][:10]:
        recent = bus_factor['recent'].get(c['name'], 0)
        is_active = recent > 0
        status_class = "active" if is_active else "inactive"
        status_text = f"{recent} recent" if is_active else "inactive"

        contributor_rows += f"""
                <tr>
                    <td>{escape(c['name'])}</td>
                    <td class="num">{c['commits']}</td>
                    <td class="num">{(c['commits'] / bus_factor['total_commits'] * 100):.1f}%</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>"""

    # Build hotspots bars
    hotspot_bars = ""
    for file, count in hotspots:
        width = (count / max_hotspot) * 100
        hotspot_bars += f"""
                <div class="bar-row">
                    <div class="bar-label" title="{escape(file)}">{escape(file)}</div>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: {width:.1f}%">
                            <span class="bar-value">{count}</span>
                        </div>
                    </div>
                </div>"""

    # Build bug cluster bars
    bug_bars = ""
    max_bugs = bugs[0][1] if bugs else 1
    for file, count in bugs:
        width = (count / max_bugs) * 100
        bug_bars += f"""
                <div class="bar-row">
                    <div class="bar-label" title="{escape(file)}">{escape(file)}</div>
                    <div class="bar-track">
                        <div class="bar-fill bug-fill" style="width: {width:.1f}%">
                            <span class="bar-value">{count}</span>
                        </div>
                    </div>
                </div>"""

    # Build rhythm chart
    rhythm_bars = ""
    for r in rhythm:
        height = (r['count'] / max_rhythm * 100) if max_rhythm > 0 else 0
        rhythm_bars += f"""
                <div class="rhythm-col">
                    <div class="rhythm-bar" style="height: {height:.1f}%"></div>
                    <div class="rhythm-label">{r['month'][-2:]}</div>
                    <div class="rhythm-value">{r['count']}</div>
                </div>"""

    # Build crisis list
    crisis_items = ""
    for incident in crisis['incidents'][:10]:
        crisis_items += f"""
                <div class="crisis-item">
                    <code class="commit-hash">{incident['hash'][:7]}</code>
                    <span class="crisis-msg">{escape(incident['message'])}</span>
                </div>"""

    if not crisis_items:
        crisis_items = '<div class="empty-state">No revert/hotfix commits found</div>'

    # Build risk table
    risk_rows = ""
    for risk in risks:
        risk_rows += f"""
                <tr>
                    <td class="file-path">{escape(risk['file'])}</td>
                    <td class="num">{risk['changes']}</td>
                    <td class="num">{risk['bugs']}</td>
                    <td class="num risk-score">{risk['score']}</td>
                </tr>"""

    if not risk_rows:
        risk_rows = '<tr><td colspan="4" class="empty-state">No high-risk files identified</td></tr>'

    # Build quality grade badge
    grade_class = ""
    if quality['grade'] == 'A':
        grade_class = "grade-a"
    elif quality['grade'] == 'B':
        grade_class = "grade-b"
    elif quality['grade'] == 'C':
        grade_class = "grade-c"
    else:
        grade_class = "grade-d"

    # Quality grade color for summary
    if quality['grade'] == 'A':
        quality_color = "var(--c-ok)"
    elif quality['grade'] in ['B', 'C']:
        quality_color = "var(--c-warning)"
    else:
        quality_color = "var(--c-accent)"

    # Build vague commits list
    vague_items = ""
    for v in quality['vague_examples'][:8]:
        vague_items += f"""
                <div class="crisis-item">
                    <code class="commit-hash">{v['hash']}</code>
                    <span class="crisis-msg" title="{escape(v['author'])} @ {v['date']}">{escape(v['message'][:50])}</span>
                </div>"""

    if not vague_items:
        vague_items = '<div class="empty-state">All commits appear well-formed</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Analysis - {escape(repo_name)}</title>
    <style>
:root {{
  --c-bg: #f8fafc;
  --c-canvas: #ffffff;
  --c-border: #cbd5e1;
  --c-text-main: #0f172a;
  --c-text-sub: #64748b;
  --c-accent: #dc2626;
  --c-warning: #ea580c;
  --c-ok: #16a34a;
  --font-ui: system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', Monaco, Consolas, monospace;
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font-ui);
  background: var(--c-bg);
  color: var(--c-text-main);
  line-height: 1.5;
  padding: 24px;
}}

.diagram-canvas {{
  max-width: 1400px;
  margin: 0 auto;
  background: var(--c-canvas);
  border: 2px solid var(--c-border);
}}

header {{
  padding: 32px;
  border-bottom: 2px solid var(--c-border);
}}

header h1 {{
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}}

header .subtitle {{
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--c-text-sub);
}}

.summary-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border-bottom: 2px solid var(--c-border);
}}

.summary-cell {{
  padding: 24px;
  border-right: 1px solid var(--c-border);
}}

.summary-cell:last-child {{
  border-right: none;
}}

.summary-cell .value {{
  font-size: 32px;
  font-weight: 600;
  font-family: var(--font-mono);
}}

.summary-cell .label {{
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--c-text-sub);
  margin-top: 4px;
}}

.section {{
  padding: 32px;
  border-bottom: 2px solid var(--c-border);
}}

.section:last-child {{
  border-bottom: none;
}}

.section-header {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24px;
}}

.section-title {{
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

.section-meta {{
  font-size: 12px;
  color: var(--c-text-sub);
}}

.grid-2 {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}}

.bar-chart {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.bar-row {{
  display: flex;
  align-items: center;
  gap: 12px;
}}

.bar-label {{
  width: 200px;
  font-family: var(--font-mono);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}}

.bar-track {{
  flex: 1;
  height: 20px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  position: relative;
}}

.bar-fill {{
  height: 100%;
  background: var(--c-text-main);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  min-width: 30px;
}}

.bar-value {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: white;
  font-weight: 600;
}}

.bug-fill {{
  background: var(--c-accent);
}}

table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}

th, td {{
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--c-border);
}}

th {{
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--c-text-sub);
  border-bottom: 2px solid var(--c-border);
}}

.num {{
  font-family: var(--font-mono);
  text-align: right;
}}

td.num {{
  color: var(--c-text-main);
}}

.active {{
  color: var(--c-ok);
  font-size: 11px;
}}

.inactive {{
  color: var(--c-text-sub);
  font-size: 11px;
}}

.risk-score {{
  color: var(--c-accent);
  font-weight: 600;
}}

.file-path {{
  font-family: var(--font-mono);
  font-size: 11px;
}}

.rhythm-chart {{
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 160px;
  padding: 16px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
}}

.rhythm-col {{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}}

.rhythm-bar {{
  width: 100%;
  background: var(--c-text-main);
  min-height: 2px;
}}

.rhythm-label {{
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--c-text-sub);
}}

.rhythm-value {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
}}

.crisis-list {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.crisis-item {{
  display: flex;
  gap: 12px;
  padding: 10px 12px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  font-size: 12px;
}}

.commit-hash {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--c-text-sub);
  background: var(--c-canvas);
  padding: 2px 6px;
  border: 1px solid var(--c-border);
}}

.crisis-msg {{
  font-family: var(--font-mono);
  color: var(--c-text-main);
}}

.empty-state {{
  color: var(--c-text-sub);
  font-style: italic;
  padding: 24px;
  text-align: center;
  font-size: 13px;
}}

.risk-table {{
  border: 1px solid var(--c-border);
}}

.risk-table th,
.risk-table td {{
  padding: 12px;
}}

.badge {{
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid var(--c-border);
  margin-left: 8px;
}}

.badge-warning {{
  border-color: var(--c-warning);
  color: var(--c-warning);
}}

.badge-danger {{
  border-color: var(--c-accent);
  color: var(--c-accent);
}}

.quality-grid {{
  display: grid;
  grid-template-columns: 160px 280px 1fr;
  gap: 32px;
  align-items: start;
}}

.quality-score {{
  text-align: center;
  padding: 24px;
  background: var(--c-bg);
  border: 2px solid var(--c-border);
}}

.grade {{
  font-size: 48px;
  font-weight: 700;
  font-family: var(--font-mono);
  line-height: 1;
  margin-bottom: 8px;
}}

.grade-a {{ color: var(--c-ok); }}
.grade-b {{ color: #0891b2; }}
.grade-c {{ color: var(--c-warning); }}
.grade-d {{ color: var(--c-accent); }}

.grade-label {{
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--c-text-sub);
}}

.quality-stats {{
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
}}

.stat-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}}

.stat-label {{
  color: var(--c-text-sub);
}}

.stat-value {{
  font-family: var(--font-mono);
  font-weight: 500;
}}

.stat-value.warning {{
  color: var(--c-warning);
}}

.quality-examples {{
  min-height: 200px;
}}

.examples-header {{
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--c-text-sub);
  margin-bottom: 12px;
}}

@media (max-width: 900px) {{
  .grid-2 {{
    grid-template-columns: 1fr;
  }}
  .summary-grid {{
    grid-template-columns: repeat(2, 1fr);
  }}
  .summary-cell:nth-child(2) {{
    border-right: none;
  }}
  .summary-cell:nth-child(1),
  .summary-cell:nth-child(2) {{
    border-bottom: 1px solid var(--c-border);
  }}
  .quality-grid {{
    grid-template-columns: 1fr;
  }}
}}
    </style>
</head>
<body>
    <div class="diagram-canvas">
        <header>
            <h1>{escape(repo_name)}</h1>
            <div class="subtitle">Git Repository Health Analysis / Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </header>

        <div class="summary-grid">
            <div class="summary-cell">
                <div class="value">{bus_factor['total_commits']}</div>
                <div class="label">Total Commits</div>
            </div>
            <div class="summary-cell">
                <div class="value">{len(bus_factor['all_time'])}</div>
                <div class="label">Contributors</div>
            </div>
            <div class="summary-cell">
                <div class="value">{bus_factor['bus_factor']}</div>
                <div class="label">Bus Factor</div>
            </div>
            <div class="summary-cell">
                <div class="value" style="color: {quality_color}">{quality['grade']}</div>
                <div class="label">Commit Quality</div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Change Hotspots</h2>
                <span class="section-meta">Top 20 files by modification frequency</span>
            </div>
            <div class="bar-chart">
                {hotspot_bars}
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Bug Clusters</h2>
                <span class="section-meta">Files with bug-related commits</span>
            </div>
            <div class="bar-chart">
                {bug_bars}
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <h2 class="section-title">High Risk Files</h2>
                <span class="section-meta">Intersection of hotspots and bug clusters</span>
            </div>
            <table class="risk-table">
                <thead>
                    <tr>
                        <th>File Path</th>
                        <th class="num">Changes</th>
                        <th class="num">Bug Fixes</th>
                        <th class="num">Risk Score</th>
                    </tr>
                </thead>
                <tbody>
                    {risk_rows}
                </tbody>
            </table>
        </div>

        <div class="grid-2" style="border-bottom: 2px solid var(--c-border);">
            <div class="section" style="border-right: 1px solid var(--c-border); border-bottom: none;">
                <div class="section-header">
                    <h2 class="section-title">Bus Factor Analysis</h2>
                    <span class="section-meta">{bus_factor['active_recent']} active in last 6 months</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Contributor</th>
                            <th class="num">Commits</th>
                            <th class="num">Share</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contributor_rows}
                    </tbody>
                </table>
            </div>

            <div class="section" style="border-bottom: none;">
                <div class="section-header">
                    <h2 class="section-title">Crisis Mode</h2>
                    <span class="section-meta">Reverts, hotfixes, rollbacks</span>
                </div>
                <div class="crisis-list">
                    {crisis_items}
                </div>
            </div>
        </div>

        <div class="section" style="border-bottom: 2px solid var(--c-border);">
            <div class="section-header">
                <h2 class="section-title">Commit Quality</h2>
                <span class="section-meta">Message clarity and semantic patterns</span>
            </div>
            <div class="quality-grid">
                <div class="quality-score">
                    <div class="grade {grade_class}">{quality['grade']}</div>
                    <div class="grade-label">Quality Grade</div>
                </div>
                <div class="quality-stats">
                    <div class="stat-row">
                        <span class="stat-label">Semantic Commits</span>
                        <span class="stat-value">{quality['semantic_count']} ({quality['semantic_pct']}%)</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Vague Messages</span>
                        <span class="stat-value warning">{quality['vague_count']} ({quality['vague_pct']}%)</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Very Short (&lt;10 chars)</span>
                        <span class="stat-value">{quality['short_commits']}</span>
                    </div>
                </div>
                <div class="quality-examples">
                    <div class="examples-header">Low Quality Examples</div>
                    <div class="crisis-list">
                        {vague_items}
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Commit Rhythm</h2>
                <span class="section-meta">Monthly commit velocity ({datetime.now().year})</span>
            </div>
            <div class="rhythm-chart">
                {rhythm_bars}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html


def main():
    """Main entry point."""
    # Check if path provided
    target_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Verify it's a git repo
    git_check = run_git_command("git rev-parse --git-dir", target_path)
    if not git_check:
        print(f"Error: {target_path} is not a git repository", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing repository: {target_path}")

    # Gather data
    report_data = {
        'repo_name': get_repo_name(target_path),
        'hotspots': analyze_change_hotspots(target_path),
        'bus_factor': analyze_bus_factor(target_path),
        'bugs': analyze_bug_clusters(target_path),
        'rhythm': analyze_commit_rhythm(target_path),
        'crisis': analyze_crisis_mode(target_path),
        'commit_quality': analyze_commit_quality(target_path)
    }

    # Calculate risk scores
    report_data['risks'] = calculate_risk_score(
        report_data['hotspots'],
        report_data['bugs']
    )

    # Generate HTML
    html = generate_html(report_data)

    # Write output
    output_path = os.path.join(os.getcwd(), 'git-analysis-report.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Report generated: {output_path}")

    # Try to open
    try:
        if sys.platform == 'darwin':
            subprocess.run(['open', output_path])
        elif sys.platform == 'linux':
            subprocess.run(['xdg-open', output_path])
        elif sys.platform == 'win32':
            os.startfile(output_path)
    except Exception:
        pass


if __name__ == '__main__':
    main()
