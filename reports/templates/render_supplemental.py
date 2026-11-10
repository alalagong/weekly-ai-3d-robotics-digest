"""Render complete, locally usable Supplemental browsers from audited ledgers.

Usage: python render_supplemental.py --ledger LEDGER --presentation JSON --report HTML
Existing report details are retained verbatim; coverage/evidence files are not rewritten.
"""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re

from lxml import html

WINDOWS = {
    'new': '本期新文', 'revised': '旧文更新',
    'historical_backfill': '历史补漏',
    'historical_revision_backfill': '历史版本补跟踪',
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def inner(element):
    return escape(element.text or '') + ''.join(
        html.tostring(child, encoding='unicode') for child in element
    )


def build(ledger, presentation, old_section=None):
    papers = [p for p in ledger['papers'] if p['disposition'] in ('supplemental', 'revision_tracking')]
    categories = presentation['categories']
    category_ids = [c['id'] for c in categories]
    notes = presentation['papers']
    note_ids = [n['id'] for n in notes]
    ids = {p['id'] for p in papers}
    if len(set(note_ids)) != len(note_ids) or set(note_ids) != ids:
        raise ValueError('Presentation IDs must match Supplemental/revision IDs exactly, once each')
    if len(set(category_ids)) != len(category_ids) or any(not re.fullmatch(r'[a-z][a-z0-9-]*', c) for c in category_ids):
        raise ValueError('Category IDs must be unique lowercase slugs')
    by_id = {n['id']: n for n in notes}
    if any(n['category'] not in category_ids or not n.get('takeaway', '').strip() for n in notes):
        raise ValueError('Every paper needs a valid category and a nonempty one-sentence takeaway')
    old_details = {}
    if old_section is not None:
        for row in old_section.xpath('.//tr[@id]'):
            cells = row.xpath('./td')
            if len(cells) == 7:
                old_details[row.get('id')] = [inner(cell) for cell in cells]
        for article in old_section.xpath('.//details[contains(concat(" ",normalize-space(@class)," ")," tracking-paper ")]'):
            body = article.xpath('./div[@class="tracking-paper-body"]')
            if body:
                old_details[article.get('id')] = inner(body[0])
    totals = Counter(by_id[p['id']]['category'] for p in papers)
    nav = '<button type="button" data-tracking-category="all" aria-pressed="true"><span>全部方向</span><span class="tracking-count">'+str(len(papers))+'</span></button>'
    groups = []
    for category in categories:
        cid = category['id']
        group_papers = [p for p in papers if by_id[p['id']]['category'] == cid]
        if not group_papers:
            continue
        nav += '<button type="button" data-tracking-category="'+cid+'" aria-pressed="false"><span>'+escape(category['label'])+'</span><span class="tracking-count">'+str(totals[cid])+'</span></button>'
        windows = Counter(p['window_class'] for p in group_papers)
        counts = ' · '.join(WINDOWS[k]+str(windows[k]) for k in WINDOWS if windows[k])
        group = '<details class="tracking-group" id="tracking-category-'+cid+'" data-category="'+cid+'"><summary><span class="tracking-group-name">'+escape(category['label'])+'</span><span class="tracking-group-count"><span data-group-visible>'+str(len(group_papers))+'</span> / '+str(len(group_papers))+' 篇</span></summary><p class="tracking-group-description">'+escape(category['description'])+' 本组总计：'+counts+'。</p>'
        # Editorial relevance first, then new/revised/history; never truncate the set.
        group_papers.sort(key=lambda p: (not by_id[p['id']].get('priority', False), list(WINDOWS).index(p['window_class']), p['id']))
        for paper in group_papers:
            note = by_id[paper['id']]
            anchor = paper['report_anchor']
            prior = old_details.get(anchor)
            detail_fields = [paper.get(k, '') for k in ('direction', 'problem', 'method', 'insight_math', 'experiments')]
            reused = paper.get('evidence_level') == 'reused_abstract'
            evidence_badge = '摘要未变 · 复用原分析' if reused else '仅摘要 · 未深读全文'
            follow = str(paper.get('follow_up') or '')
            if not reused:
                follow = '仅摘要；未深读全文、未运行。' + follow
            if paper.get('original_report'):
                follow += ' 原报告：'+paper['original_report']+'。'+str(paper.get('legacy_report_inspection') or '')
            detail_fields.append(follow)
            labels = ['方向关系', '解决的问题', '方法 / 结构', 'Insight 与数学', '实验与限制', '证据与后续动作']
            version_label = 'v'+str(paper['version']) if paper.get('version') is not None else ''
            if re.fullmatch(r'\d{4}\.\d{4,5}', paper['id']):
                url = 'https://arxiv.org/abs/'+paper['id']+version_label
            else:
                url = paper.get('canonical_url') or ('https://doi.org/'+paper['doi'] if paper.get('doi') else next((u for u in paper.get('source_urls', []) if u.startswith('https://')), ''))
                if not url:
                    raise ValueError('Non-arXiv paper requires canonical_url, DOI or HTTPS source')
            if isinstance(prior, str):
                body = prior
            else:
                citation = prior[0] if prior else '<a href="'+escape(url)+'">原文 '+escape(paper['id'])+version_label+'</a><br>v1 '+escape(str(paper.get('v1_utc')))+' · updated '+escape(str(paper.get('updated_utc')))
                values = prior[1:] if prior else [escape(str(value)) for value in detail_fields]
                if reused and paper.get('original_report'):
                    prior_path = Path(paper['original_report']).name
                    prior_anchor = paper.get('original_report_anchor')
                    href = './' + prior_path + ('#' + prior_anchor if prior_anchor else '')
                    citation += ' · <a href="' + escape(href) + '">原报告</a>'
                body = '<p>'+citation+'</p><dl>'+''.join('<dt>'+label+'</dt><dd>'+value+'</dd>' for label, value in zip(labels, values))+'</dl>'
            if note.get('priority'):
                body += '<p class="small tracking-priority-reason">优先关注原因：'+escape(note.get('priority_reason', '与核心 SLAM/3D 研究问题直接相关'))+'；仍为摘要级证据。</p>' if 'tracking-priority-reason' not in body else ''
            group += '<details class="tracking-paper" id="'+escape(anchor)+'" data-category="'+cid+'" data-window="'+paper['window_class']+'" data-priority="'+str(bool(note.get('priority'))).lower()+'"><summary><span class="tracking-paper-heading">'+escape(paper['title'])+'</span><span class="tracking-paper-takeaway">'+escape(note['takeaway'])+'</span><span class="tracking-paper-badges"><span class="tag">'+WINDOWS[paper['window_class']]+'</span><span class="tag">'+escape(paper['id'])+version_label+'</span><span class="tag">'+evidence_badge+'</span>'+('<span class="tag priority-tag">优先关注</span>' if note.get('priority') else '')+'</span></summary><div class="tracking-paper-body">'+body+'</div></details>'
        groups.append(group+'</details>')
    return nav, '\n'.join(groups), {'total': len(papers), 'categories': dict(totals), 'priority': sum(bool(n.get('priority')) for n in notes)}


def update_report(ledger_path, presentation_path, report_path, template_path):
    ledger = read_json(ledger_path)
    presentation = read_json(presentation_path)
    report_path = Path(report_path)
    source = report_path.read_text(encoding='utf-8-sig')
    tree = html.fromstring(source)
    sections = tree.xpath('//section[h2[normalize-space()="Supplemental Tracking Papers"]]')
    if len(sections) != 1:
        raise ValueError('Expected exactly one Supplemental section')
    nav, groups, stats = build(ledger, presentation, sections[0])
    template = Path(template_path).read_text(encoding='utf-8-sig')
    component = re.search(r'    <section id="supplemental-tracking".*?</section>', template, flags=re.S).group()
    component = component.replace('{{SUPPLEMENTAL_COUNT}}', str(stats['total'])).replace('{{SUPPLEMENTAL_CATEGORY_NAV}}', nav).replace('{{SUPPLEMENTAL_CATEGORY_GROUPS}}', groups)
    section_pattern = r'    <section[^>]*>\s*<h2>Supplemental Tracking Papers</h2>.*?</section>'
    output, count = re.subn(section_pattern, lambda _: component, source, flags=re.S)
    if count != 1:
        raise ValueError('Could not uniquely replace old section')
    css = re.search(r'    /\* supplemental-browser:start \*/.*?/\* supplemental-browser:end \*/', template, flags=re.S).group()
    if '/* supplemental-browser:start */' in output:
        output = re.sub(r'    /\* supplemental-browser:start \*/.*?/\* supplemental-browser:end \*/', lambda _: css, output, flags=re.S)
    else:
        output = output.replace('    .links { columns: 2; }', css+'\n    .links { columns: 2; }')
    if '{{SUPPLEMENTAL_' in output:
        raise ValueError('Unfilled Supplemental placeholder')
    report_path.write_bytes(output.encode('utf-8'))
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--presentation', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--template', default=str(Path(__file__).with_name('slam-3d-weekly-template.html')))
    args = parser.parse_args()
    print(json.dumps(update_report(args.ledger, args.presentation, args.report, args.template), ensure_ascii=False, indent=2))
