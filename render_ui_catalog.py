import json
import re

# Load 60 materials
with open('materials_catalog_60.json', 'r', encoding='utf-8') as f:
    materials = json.load(f)

# Calculate stats
stage_counts = {1: 0, 2: 0, 3: 0, 4: 0}
stage_prs = {1: 0, 2: 0, 3: 0, 4: 0}
cat_counts = {'mechanical': 0, 'electrical': 0, 'pneumatic': 0}

total_savings = sum(m['total_savings'] for m in materials)
total_pre = sum(m['total_pre_spend'] for m in materials)
savings_pct = round((total_savings / total_pre) * 100, 1) if total_pre > 0 else 15.1

for m in materials:
    s = m['stage']
    stage_counts[s] += 1
    stage_prs[s] += m['actual_pr_count']
    c = m['cat']
    if c in cat_counts:
        cat_counts[c] += 1

print(f"Stage counts: {stage_counts}")
print(f"Stage PRs: {stage_prs}")
print(f"Cat counts: {cat_counts}")

def render_row(m):
    badge_colors = {
        1: ("bg-amber-50 border-amber-200 text-amber-900", "Stage 1", m['stage_label']),
        2: ("bg-blue-50 border-blue-200 text-blue-900", "Stage 2", m['stage_label']),
        3: ("bg-purple-50 border-purple-200 text-purple-900", "Stage 3", m['stage_label']),
        4: ("bg-emerald-50 border-emerald-200 text-emerald-800", "Stage 4", m['stage_label'])
    }
    
    stage_css, stage_tag, stage_lbl = badge_colors.get(m['stage'], ("bg-slate-50 border-slate-200 text-slate-800", f"Stage {m['stage']}", m['stage_label']))
    
    # Action buttons based on stage
    if m['stage'] == 4:
        action_btn = f'''<button onclick="app.openSignOff('{m['id']}')" class="btn btn-xs btn-primary rounded-lg px-2 text-[11px]"><i data-lucide="file-check-2" class="w-3 h-3 mr-1"></i> ลงนาม</button>'''
    elif m['stage'] == 3:
        action_btn = f'''<button onclick="app.openChatModal('{m['id']}')" class="btn btn-xs btn-info text-white rounded-lg px-2 text-[11px]"><i data-lucide="activity" class="w-3 h-3 mr-1"></i> เจรจาต่อรอง</button>'''
    elif m['stage'] == 2:
        action_btn = f'''<button onclick="app.openRAGModal('{m['id']}')" class="btn btn-xs btn-outline btn-primary rounded-lg px-2 text-[11px]"><i data-lucide="file-search" class="w-3 h-3 mr-1"></i> ดูสัญญาเดิม</button>'''
    else:
        action_btn = f'''<button onclick="app.triggerAggregation('{m['id']}')" class="btn btn-xs btn-primary rounded-lg px-2 text-[11px]"><i data-lucide="layers" class="w-3 h-3 mr-1"></i> รวมยอด PR</button>'''

    return f'''                                <!-- ROW: {m['code']} -->
                                <tr class="hover:bg-blue-50/40 transition-colors job-row" data-category="{m['cat']}" data-stage="{m['stage']}" data-stages="{m['stage']}">
                                    <td class="py-3 px-3 min-w-[170px] max-w-[210px]">
                                        <div class="min-w-0">
                                            <div class="font-bold font-mono text-blue-900 text-xs truncate" title="{m['code']}">{m['code']}</div>
                                            <div class="text-[11px] text-slate-600 truncate mt-0.5" title="{m['name']}">{m['name']}</div>
                                        </div>
                                    </td>
                                    <td class="py-3 px-2 whitespace-nowrap"><span class="badge badge-ghost badge-sm text-[10px] whitespace-nowrap">{m['cat_th']}</span></td>
                                    <td class="py-3 px-2">
                                        <span class="badge badge-warning badge-xs font-mono">{m['stock_type']}</span>
                                        <div class="text-[10px] text-slate-500 mt-0.5">{m['stock_alert']}</div>
                                    </td>
                                    <td class="py-3 px-2 text-right whitespace-nowrap">
                                        <div class="font-bold text-slate-900 font-mono text-xs">{m['total_qty']:,} <span class="text-[10px] text-slate-500 font-normal">{m['unit']}</span></div>
                                        <div class="mt-1 flex justify-end">
                                            <button type="button" onclick="app.openPrModal('{m['id']}')" class="badge badge-sm badge-info badge-outline gap-1 hover:bg-blue-100 cursor-pointer whitespace-nowrap inline-flex items-center px-2 py-0.5 text-[10px]" title="คลิกตรวจสอบใบขอซื้อย่อย (Audit Trail) ในดีลนี้">
                                                <i data-lucide="layers" class="w-3 h-3"></i> รวม {m['actual_pr_count']} PRs
                                            </button>
                                        </div>
                                    </td>
                                    <td class="py-3 px-2 text-right font-mono text-slate-400">฿{m['pre_p']:,.2f}</td>
                                    <td class="py-3 px-2 text-right font-mono font-bold text-blue-700">฿{m['post_p']:,.2f}</td>
                                    <td class="py-3 px-2 text-right font-mono font-bold text-emerald-700">฿{m['total_savings']:,.0f} <span class="text-[9px] font-normal">(-{m['savings_pct']}%)</span></td>
                                    <td class="py-3 px-2 text-center">
                                        <div class="inline-flex flex-col items-center justify-center px-2.5 py-1 rounded-lg {stage_css} shadow-xs">
                                            <span class="font-bold text-[10px] font-mono leading-none">{stage_tag}</span>
                                            <span class="text-[10px] font-medium mt-0.5 leading-tight whitespace-nowrap">{stage_lbl}</span>
                                        </div>
                                    </td>
                                    <td class="py-3 px-3 text-center min-w-[155px]">
                                        <div class="flex items-center justify-center gap-1.5 whitespace-nowrap">
                                            <button onclick="app.openChatModal('{m['id']}')" class="btn btn-xs btn-ghost text-blue-700" title="ห้องแชตเจรจา"><i data-lucide="messages-square" class="w-3.5 h-3.5"></i></button>
                                            <button onclick="app.openReasoningModal('{m['id']}')" class="btn btn-xs btn-ghost text-blue-700" title="AI Reasoning (CoT)"><i data-lucide="brain" class="w-3.5 h-3.5"></i></button>
                                            {action_btn}
                                        </div>
                                    </td>
                                </tr>'''

all_rows_html = "\n\n".join(render_row(m) for m in materials)

def update_html_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Top Stats Cards
    html = re.sub(
        r'<div class="text-xs font-bold text-slate-800 font-mono truncate">10 ดีลหลัก</div>',
        f'<div class="text-xs font-bold text-slate-800 font-mono truncate">{len(materials)} ดีล MRO</div>',
        html
    )
    html = re.sub(
        r'<div class="text-xs font-bold text-emerald-700 font-mono truncate">฿[\d,]+ \(-[\d\.]+%\)</div>',
        f'<div class="text-xs font-bold text-emerald-700 font-mono truncate">฿{total_savings:,.0f} (-{savings_pct}%)</div>',
        html
    )
    
    # 2. Update Stage Step Filter Counters
    html = re.sub(
        r'<span id="stage-count-1">\d+ ดีล</span> / <span id="stage-prs-1">\d+ PRs</span>',
        f'<span id="stage-count-1">{stage_counts[1]} ดีล</span> / <span id="stage-prs-1">{stage_prs[1]} PRs</span>',
        html
    )
    html = re.sub(
        r'<span id="stage-count-2">\d+ ดีล</span> / <span id="stage-prs-2">[\d,]+ PRs</span>',
        f'<span id="stage-count-2">{stage_counts[2]} ดีล</span> / <span id="stage-prs-2">{stage_prs[2]} PRs</span>',
        html
    )
    html = re.sub(
        r'<span id="stage-count-3">\d+ ดีล</span> / <span id="stage-prs-3">[\d,]+ PRs</span>',
        f'<span id="stage-count-3">{stage_counts[3]} ดีล</span> / <span id="stage-prs-3">{stage_prs[3]} PRs</span>',
        html
    )
    html = re.sub(
        r'<span id="stage-count-4">\d+ ดีล</span> / <span id="stage-prs-4">[\d,]+ PRs</span>',
        f'<span id="stage-count-4">{stage_counts[4]} ดีล</span> / <span id="stage-prs-4">{stage_prs[4]} PRs</span>',
        html
    )

    # 3. Update Category Tabs text
    html = re.sub(
        r'<a role="tab" id="tab-cat-all" onclick="app\.filterCat\(\'all\'\)" class="tab tab-active text-xs font-medium">[^<]+</a>',
        f'<a role="tab" id="tab-cat-all" onclick="app.filterCat(\'all\')" class="tab tab-active text-xs font-medium">ทั้งหมด ({len(materials)} ดีล)</a>',
        html
    )
    html = re.sub(
        r'<a role="tab" id="tab-cat-mechanical" onclick="app\.filterCat\(\'mechanical\'\)" class="tab text-xs font-medium gap-1"><i data-lucide="cog" class="w-3.5 h-3.5"></i> เครื่องกล &amp; ส่งกำลัง \(\d+\)</a>',
        f'<a role="tab" id="tab-cat-mechanical" onclick="app.filterCat(\'mechanical\')" class="tab text-xs font-medium gap-1"><i data-lucide="cog" class="w-3.5 h-3.5"></i> เครื่องกล &amp; ส่งกำลัง ({cat_counts["mechanical"]})</a>',
        html
    )
    html = re.sub(
        r'<a role="tab" id="tab-cat-pneumatic" onclick="app\.filterCat\(\'pneumatic\'\)" class="tab text-xs font-medium gap-1"><i data-lucide="wind" class="w-3.5 h-3.5"></i> นิวเมติกส์ &amp; ไฮดรอลิกส์ \(\d+\)</a>',
        f'<a role="tab" id="tab-cat-pneumatic" onclick="app.filterCat(\'pneumatic\')" class="tab text-xs font-medium gap-1"><i data-lucide="wind" class="w-3.5 h-3.5"></i> นิวเมติกส์ &amp; ไฮดรอลิกส์ ({cat_counts["pneumatic"]})</a>',
        html
    )
    html = re.sub(
        r'<a role="tab" id="tab-cat-electrical" onclick="app\.filterCat\(\'electrical\'\)" class="tab text-xs font-medium gap-1"><i data-lucide="zap" class="w-3.5 h-3.5"></i> ไฟฟ้า &amp; เซนเซอร์ \(\d+\)</a>',
        f'<a role="tab" id="tab-cat-electrical" onclick="app.filterCat(\'electrical\')" class="tab text-xs font-medium gap-1"><i data-lucide="zap" class="w-3.5 h-3.5"></i> ไฟฟ้า &amp; เซนเซอร์ ({cat_counts["electrical"]})</a>',
        html
    )

    # 4. Replace entire table tbody
    html = re.sub(
        r'<th class="py-3 px-3 min-w-\[\d+px\]">รหัส & รายการอะไหล่ MRO</th>',
        '<th class="py-3 px-3 min-w-[170px] max-w-[210px]">รหัส & รายการอะไหล่ MRO</th>',
        html
    )

    tbody_pattern = re.compile(r'(<tbody class="divide-y divide-slate-100">)(.*?)(</tbody>)', re.DOTALL)
    html = tbody_pattern.sub(f'\\1\n{all_rows_html}\n                            \\3', html, count=1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {path} with {len(materials)} material rows successfully.")

update_html_file('index.html')
update_html_file('webapp/web/templates/index.html')
