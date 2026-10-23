// AUTO-EXTRACTED from index.html by Phase-F refactor. Do not add server-rendered values here.

        const app = {

            // ================= REAL-TIME EVENT STREAM CONTROLLER =================

            pushLiveEvent(text, highlight = false) {

                const now = new Date();

                const timeStr = now.toTimeString().split(' ')[0];

                const formatted = `[${timeStr}] ${text}`;

                const el = document.getElementById('ticker-msg');

                if (el) {

                    el.style.opacity = '0';

                    setTimeout(() => {

                        el.innerText = formatted;

                        if (highlight) {

                            el.className = 'text-emerald-300 font-bold transition-all duration-300';

                        } else {

                            el.className = 'text-slate-300 transition-all duration-300';

                        }

                        el.style.opacity = '1';

                    }, 150);

                }

            },

            currentPrList: [],



                        async openEmailModal(dealKey) {

                if (!dealKey) dealKey = 'festo_cyl';

                this.currentEmailDealKey = dealKey;

                const modal = document.getElementById('email_sim_modal');

                if (!modal) return;



                const deal = this.getDeal(dealKey);

                const skuEl = document.getElementById('modal-email-deal-sku');

                if (skuEl) skuEl.innerText = deal.part_code || deal.sku || dealKey.toUpperCase();



                const vendors = deal.vendors || [];

                const countBadge = document.getElementById('modal-vendor-count-badge');

                if (countBadge) countBadge.innerText = `${vendors.length} บริษัท`;



                // Render dynamic vendors table with editable email inputs

                const tbody = document.getElementById('modal-vendors-tbody');

                if (tbody) {

                    if (vendors.length === 0) {

                        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-slate-500">ไม่พบคู่ค้าในรายการ Approved Vendor List</td></tr>`;

                    } else {

                        tbody.innerHTML = vendors.map((v, idx) => {

                            const vId = v.id || `v${idx+1}`;

                            const token = `tok_sec_${dealKey}_${vId}_verified`;

                            const portalUrl = `${window.location.origin}/portal/negotiate/${dealKey}?vendor=${vId}&token=${token}`;

                            const emailVal = v.email || 'teeranonn124@gmail.com';

                            return `

                                <tr class="hover:bg-slate-800/80 transition-colors">

                                    <td class="font-mono text-slate-400 text-xs">#${idx + 1}</td>

                                    <td class="min-w-[170px]">

                                        <div class="font-bold text-slate-100 text-xs">${v.name}</div>

                                        <div class="text-[10px] text-slate-400 font-mono mt-0.5">ID: ${vId} · สัญญา: Blanket 1 ปี</div>

                                    </td>

                                    <td class="min-w-[220px]">

                                        <div class="flex items-center gap-1.5">

                                            <input type="email" id="vendor-email-input-${idx}" 

                                                   value="${emailVal}" 

                                                   onchange="app.updateVendorEmail('${dealKey}', '${vId}', ${idx}, this.value)"

                                                   class="input input-xs bg-slate-900 border-slate-700 text-slate-100 rounded-lg w-full font-mono text-xs focus:border-blue-500 placeholder:text-slate-600" 

                                                   placeholder="ระบุอีเมลผู้รับ..." />

                                            <button type="button" onclick="app.updateVendorEmail('${dealKey}', '${vId}', ${idx}, document.getElementById('vendor-email-input-${idx}').value)" 

                                                    class="btn btn-xs btn-ghost text-slate-400 hover:text-white p-1" title="บันทึกอีเมล">

                                                <i data-lucide="save" class="w-3.5 h-3.5"></i>

                                            </button>

                                        </div>

                                    </td>

                                    <td class="text-right whitespace-nowrap">

                                        <div class="flex items-center justify-end gap-1.5">

                                            <button type="button" onclick="app.sendSingleVendorInvite('${dealKey}', ${idx})" id="btn-send-vendor-${idx}"

                                                    class="btn btn-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg px-2.5 py-1 h-auto flex items-center gap-1 shadow-xs transition-all">

                                                <i data-lucide="send" class="w-3 h-3"></i>

                                                <span>ยิง SES</span>

                                            </button>

                                            <a href="${portalUrl}" target="_blank" class="btn btn-xs btn-ghost text-indigo-400 hover:text-indigo-300 hover:bg-slate-800 rounded-lg p-1" title="เปิดหน้าจอคู่ค้า (Supplier Portal)">

                                                <i data-lucide="external-link" class="w-3.5 h-3.5"></i>

                                            </a>

                                        </div>

                                    </td>

                                </tr>

                            `;

                        }).join('');

                    }

                }



                // Populate Official RFQ Letter Preview Card below

                const v0 = vendors[0] || { name: 'บจก. คู่ค้า AVL', id: 'v1' };

                const prevVendor = document.getElementById('preview-vendor-name');

                if (prevVendor) prevVendor.innerText = v0.name;



                const prevSku = document.getElementById('preview-part-sku');

                if (prevSku) prevSku.innerText = deal.part_code || deal.sku || dealKey.toUpperCase();



                const prevQty = document.getElementById('preview-part-qty');

                if (prevQty) prevQty.innerText = `${deal.qty || 850} ${deal.unit || 'ชิ้น'}`;



                const prevPrs = document.getElementById('preview-part-prs');

                if (prevPrs) prevPrs.innerText = `${deal.prs_count || 14} PRs`;



                const prevBtn = document.getElementById('preview-portal-btn');

                if (prevBtn) {

                    const token0 = `tok_sec_${dealKey}_${v0.id || 'v1'}_verified`;

                    prevBtn.href = `${window.location.origin}/portal/negotiate/${dealKey}?vendor=${v0.id || 'v1'}&token=${token0}`;

                }



                const statusEl = document.getElementById('email-send-status');

                if (statusEl) statusEl.innerHTML = `<i data-lucide="info" class="w-3.5 h-3.5 text-blue-400 shrink-0"></i> <span>พร้อมส่งเทียบเชิญไปยัง ${vendors.length} คู่ค้าผ่าน Amazon SES</span>`;



                modal.showModal();

                lucide.createIcons({ root: modal });

            },



            async updateVendorEmail(dealKey, vendorId, vendorIndex, newEmail) {

                const cleanEmail = (newEmail || '').trim();

                if (!cleanEmail) return;



                // Update in memory

                if (database.deals && database.deals[dealKey] && database.deals[dealKey].vendors && database.deals[dealKey].vendors[vendorIndex]) {

                    database.deals[dealKey].vendors[vendorIndex].email = cleanEmail;

                }



                const statusEl = document.getElementById('email-send-status');

                if (statusEl) statusEl.innerHTML = `<span class="loading loading-spinner loading-xs text-blue-400"></span> กำลังบันทึกอีเมล...`;



                try {

                    await fetch(`/api/deals/${dealKey}/vendors/${vendorId}/email`, {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({ email: cleanEmail })

                    });

                    if (statusEl) statusEl.innerHTML = `<span class="text-emerald-400">✓ บันทึกอีเมล ${cleanEmail} เรียบร้อยแล้ว</span>`;

                } catch (e) {

                    if (statusEl) statusEl.innerHTML = `<span class="text-amber-400">บันทึกในหน่วยความจำเรียบร้อย (${cleanEmail})</span>`;

                }

            },



            async sendSingleVendorInvite(dealKey, vendorIndex) {

                const deal = (database.deals && database.deals[dealKey]) || {};

                const vendors = deal.vendors || [];

                const v = vendors[vendorIndex];

                if (!v) return;



                const input = document.getElementById(`vendor-email-input-${vendorIndex}`);

                const email = (input ? input.value.trim() : (v.email || '')).trim();



                const btn = document.getElementById(`btn-send-vendor-${vendorIndex}`);

                const statusEl = document.getElementById('email-send-status');



                if (!email) {

                    if (statusEl) statusEl.innerHTML = `<span class="text-amber-400">⚠ กรุณาระบุอีเมลก่อนส่ง</span>`;

                    return;

                }



                v.email = email;



                if (btn) {

                    btn.disabled = true;

                    btn.innerHTML = `<span class="loading loading-spinner loading-xs"></span>`;

                }

                if (statusEl) statusEl.innerHTML = `<span class="loading loading-spinner loading-xs text-blue-400"></span> กำลังส่งผ่าน AWS SES ไปยัง ${email}...`;



                try {

                    const res = await fetch('/api/send-invite', {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({

                            deal_id: dealKey,

                            vendor_id: v.id || `v${vendorIndex+1}`,

                            vendor_name: v.name,

                            email: email

                        })

                    });

                    const data = await res.json();

                    if (statusEl) {

                        statusEl.innerHTML = `<span class="text-emerald-400 font-bold">✓ ยิง SES สำเร็จไปยัง ${email} (ID: ${(data.message_id || 'SES-OK').substring(0, 16)}...)</span>`;

                    }

                    this.showToast(`✅ ยิงเทียบเชิญ RFQ ทาง AWS SES ถึง ${v.name} (${email}) สำเร็จ!`, 'success');

                    this.pushLiveEvent(`✉️ [AWS SES] ส่งเทียบเชิญ RFQ สำเร็จไปยัง ${v.name} (${email})`, true);

                } catch (e) {

                    if (statusEl) statusEl.innerHTML = `<span class="text-red-400">เกิดข้อผิดพลาด: ${e.message}</span>`;

                } finally {

                    if (btn) {

                        btn.disabled = false;

                        btn.innerHTML = `<i data-lucide="check" class="w-3 h-3 text-emerald-300"></i> <span>ส่งแล้ว</span>`;

                        lucide.createIcons({ root: btn });

                    }

                }

            },



            async sendAllVendorsInvite() {

                const dealKey = this.currentEmailDealKey || 'festo_cyl';

                const deal = (database.deals && database.deals[dealKey]) || {};

                const vendors = deal.vendors || [];



                const statusEl = document.getElementById('email-send-status');

                const btnAll = document.getElementById('btn-send-all-vendors');



                if (btnAll) {

                    btnAll.disabled = true;

                    btnAll.innerHTML = `<span class="loading loading-spinner loading-xs"></span> กำลังยิง SES ทุกเจ้า...`;

                }

                if (statusEl) statusEl.innerHTML = `<span class="loading loading-spinner loading-xs text-blue-400"></span> กำลังส่งเทียบเชิญไปยังคู่ค้าทั้ง ${vendors.length} เจ้าผ่าน AWS SES...`;



                let sentCount = 0;

                for (let i = 0; i < vendors.length; i++) {

                    const v = vendors[i];

                    const input = document.getElementById(`vendor-email-input-${i}`);

                    const email = (input ? input.value.trim() : (v.email || '')).trim() || 'teeranonn124@gmail.com';

                    v.email = email;



                    try {

                        await fetch('/api/send-invite', {

                            method: 'POST',

                            headers: { 'Content-Type': 'application/json' },

                            body: JSON.stringify({

                                deal_id: dealKey,

                                vendor_id: v.id || `v${i+1}`,

                                vendor_name: v.name,

                                email: email

                            })

                        });

                        sentCount++;

                    } catch(e) {}

                }



                if (statusEl) {

                    statusEl.innerHTML = `<span class="text-emerald-400 font-bold">✓ ยิงเทียบเชิญ RFQ ทาง AWS SES ครบทั้ง ${sentCount}/${vendors.length} เจ้าเรียบร้อยแล้ว!</span>`;

                }

                this.showToast(`✅ ยิงเทียบเชิญ RFQ ทาง AWS SES ครบ ${sentCount} เจ้าเรียบร้อย!`, 'success');

                this.pushLiveEvent(`🚀 [AWS SES] ยิงเทียบเชิญ RFQ แบบคู่ขนานครบทุกเจ้าในดีล ${dealKey.toUpperCase()} สำเร็จ`, true);



                if (btnAll) {

                    btnAll.disabled = false;

                    btnAll.innerHTML = `<i data-lucide="check-check" class="w-3.5 h-3.5 text-emerald-300"></i> <span>ส่งครบทุกเจ้าแล้ว</span>`;

                    lucide.createIcons({ root: btnAll });

                }

            },



            copyMagicLink() {

                if (this.currentPortalUrl) {

                    navigator.clipboard.writeText(this.currentPortalUrl).then(() => {

                        const btnText = document.getElementById('btn-copy-magic-text');

                        if (btnText) {

                            const old = btnText.innerText;

                            btnText.innerText = "✓ คัดลอกสำเร็จ!";

                            setTimeout(() => btnText.innerText = old, 2500);

                        }

                        this.showToast("คัดลอก Magic Link เรียบร้อยแล้ว สามารถนำไปเปิดในเบราว์เซอร์ใดก็ได้", "success");

                    }).catch(err => {

                        prompt("คัดลอกลิงก์:", this.currentPortalUrl);

                    });

                }

            },



            async openPrModal(dealKey) {
                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';
                const deal = (this.getDeal && this.getDeal(dealKey)) || (database.deals && database.deals[dealKey]) || { title: dealKey.toUpperCase() };

                // Accurately determine deal stage from DOM or deal object
                let currentStage = (deal && deal.stage !== undefined && deal.stage !== null) ? parseInt(deal.stage, 10) : null;
                if (currentStage === null || isNaN(currentStage)) {
                    const row = document.querySelector(`button[onclick*="'${dealKey}'"]`)?.closest('tr');
                    if (row && row.getAttribute('data-stage')) {
                        currentStage = parseInt(row.getAttribute('data-stage'), 10);
                    } else {
                        currentStage = 1;
                    }
                }
                this.currentPrDealStage = currentStage;

                const modal = document.getElementById('pr_modal');
                const titleEl = document.getElementById('pr-modal-title');
                const subEl = document.getElementById('pr-modal-subtitle');
                const cntEl = document.getElementById('pr-stat-count');
                const qtyEl = document.getElementById('pr-stat-qty');
                const preEl = document.getElementById('pr-stat-pre');
                const savEl = document.getElementById('pr-stat-savings');
                const tbody = document.getElementById('pr-table-body');
                const searchInput = document.getElementById('pr-search-input');
                if (searchInput) searchInput.value = '';

                if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400"><span class="loading loading-spinner loading-sm"></span> กำลังดึงข้อมูลจากระบบ ERP...</td></tr>`;

                modal.showModal();
                lucide.createIcons({ root: modal });

                try {
                    const res = await fetch(`/api/deals/${dealKey}/prs?limit=500`);
                    if (res.ok) {
                        const data = await res.json();
                        this.currentPrList = data.transactions || [];
                    } else {
                        this.currentPrList = [];
                    }
                } catch(e) {
                    this.currentPrList = [];
                }

                if (this.currentPrList.length === 0) {
                    const dataset = window.DATASET_2500_DATA || window.DATASET_2500 || [];
                    const did = dealKey.toLowerCase();
                    this.currentPrList = dataset.filter(r => (r.deal_key && r.deal_key.toLowerCase() === did) || (r.code && r.code.toLowerCase().includes(did)));
                }

                // Calculate metrics
                const totalPrs = this.currentPrList.length;
                const totalQty = this.currentPrList.reduce((acc, r) => acc + (r.qty || 0), 0);
                const preTotal = this.currentPrList.reduce((acc, r) => acc + (r.pre_tot || 0), 0);
                const savTotal = this.currentPrList.reduce((acc, r) => acc + (r.tco_sav || 0), 0);

                const cleanTitle = (deal.name || deal.title || dealKey.toUpperCase()).replace(/ยอดรวม.*$/, '').trim();
                if (titleEl) titleEl.innerText = `ตรวจสอบใบขอซื้อย่อย (PRs): ${cleanTitle} (รวม ${totalPrs.toLocaleString()} ใบ / ${totalQty.toLocaleString()} ชิ้น)`;

                const isAwarded = (currentStage === 4);
                const isStage1 = (currentStage === 1);

                if (subEl) {
                    if (isAwarded) {
                        subEl.innerText = `รายการใบขอซื้อย่อยระดับโรงงานทั้งหมดที่ถูกมัดรวมเข้าสู่ดีลนี้เพื่อขอ Volume Discount และเจรจาต่อรองเสร็จสมบูรณ์ (Stage 4 รออนุมัติ PO)`;
                    } else if (isStage1) {
                        subEl.innerText = `รายการใบขอซื้อย่อยระดับโรงงานทั้งหมดที่ถูกมัดรวมเข้าสู่ดีลนี้เพื่อขอ Volume Discount (สถานะ: Stage 1 รอเปิดห้องเจรจาคู่ค้า)`;
                    } else {
                        subEl.innerText = `รายการใบขอซื้อย่อยระดับโรงงานทั้งหมดที่ถูกมัดรวมเข้าสู่ดีลนี้เพื่อขอ Volume Discount (สถานะ: Stage ${currentStage} อยู่ระหว่างเจรจาต่อรอง)`;
                    }
                }

                if (cntEl) cntEl.innerText = `${totalPrs.toLocaleString()} ใบ`;
                if (qtyEl) qtyEl.innerText = `${totalQty.toLocaleString()} ชิ้น`;
                if (preEl) {
                    preEl.innerText = `฿${Math.round(preTotal).toLocaleString()}`;
                    preEl.className = isAwarded ? "text-base font-bold text-slate-500 line-through font-mono" : "text-base font-bold text-slate-800 font-mono";
                }

                const savLabelEl = document.getElementById('pr-savings-label');
                if (savEl) {
                    if (isAwarded) {
                        if (savLabelEl) savLabelEl.innerText = "กู้คืนเงินรั่วไหล (Savings)";
                        savEl.innerHTML = `฿${Math.round(savTotal).toLocaleString()} <span class="text-xs text-emerald-600 font-normal font-sans">(-${preTotal > 0 ? ((savTotal/preTotal)*100).toFixed(1) : 0}%)</span>`;
                    } else if (isStage1) {
                        if (savLabelEl) savLabelEl.innerText = "เป้าหมายลดต้นทุน TCO (Target)";
                        savEl.innerHTML = `<span class="text-blue-700">฿${Math.round(savTotal || (preTotal * 0.12)).toLocaleString()}</span> <span class="text-xs text-slate-400 font-normal font-sans">(คาดการณ์)</span>`;
                    } else {
                        if (savLabelEl) savLabelEl.innerText = "กรอบประหยัดเป้าหมาย TCO";
                        savEl.innerHTML = `<span class="text-blue-700">฿${Math.round(savTotal || (preTotal * 0.12)).toLocaleString()}</span> <span class="text-xs text-slate-400 font-normal font-sans">(อยู่ระหว่างเจรจา)</span>`;
                    }
                }

                this.renderPrTable(this.currentPrList, currentStage);
            },

            renderPrTable(list, currentStage) {
                if (currentStage === undefined) currentStage = this.currentPrDealStage || 1;
                const tbody = document.getElementById('pr-table-body');
                const countEl = document.getElementById('pr-showing-count');
                if (countEl) countEl.innerText = list.length.toLocaleString();
                if (!tbody) return;

                if (list.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">ไม่พบรายการใบขอซื้อที่ตรงกับคำค้นหา</td></tr>`;
                    return;
                }

                const isAwarded = (currentStage === 4);
                const isStage1 = (currentStage === 1);

                tbody.innerHTML = list.slice(0, 100).map(r => `
                    <tr class="hover:bg-blue-50/50 transition-colors">
                        <td class="py-2 px-3 font-bold text-blue-800 font-mono">${r.pr || r.id}</td>
                        <td class="py-2 px-2 text-slate-500 font-mono">${r.date || '-'}</td>
                        <td class="py-2 px-2"><span class="badge badge-ghost badge-xs font-mono text-[10px]">${(r.plant || '').split(' ')[0]}</span></td>
                        <td class="py-2 px-2 text-right font-mono font-semibold">${(r.qty || 0).toLocaleString()}</td>
                        <td class="py-2 px-2 text-right font-mono ${isAwarded ? 'text-slate-400 line-through' : 'font-bold text-slate-800'}">฿${(r.pre_p || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</td>
                        <td class="py-2 px-2 text-right font-mono">
                            ${isAwarded 
                                ? `<span class="font-bold text-blue-700">฿${(r.post_p || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</span>` 
                                : (isStage1 
                                    ? '<span class="badge badge-warning badge-xs text-[10px]">รอเจรจา (Stage 1)</span>' 
                                    : `<span class="badge badge-info badge-xs text-[10px]">อยู่ระหว่างเจรจา (Stage ${currentStage})</span>`
                                )
                            }
                        </td>
                        <td class="py-2 px-2 text-right font-mono">
                            ${isAwarded 
                                ? `<span class="font-bold text-emerald-700">฿${(r.tco_sav || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</span>` 
                                : '<span class="text-slate-400 text-xs">-</span>'
                            }
                        </td>
                        <td class="py-2 px-3 font-sans text-[11px] truncate max-w-[170px]">
                            ${isAwarded 
                                ? `<span class="text-slate-800 font-semibold">${r.sup_post || '-'}</span>` 
                                : (isStage1 
                                    ? '<span class="text-slate-500 italic">รอคัดเลือกจาก AVL (3 เจ้า)</span>' 
                                    : '<span class="text-slate-500 italic">อยู่ระหว่างเปรียบเทียบข้อเสนอ</span>'
                                )
                            }
                        </td>
                    </tr>
                `).join('') + (list.length > 100 ? `<tr><td colspan="8" class="text-center py-2 text-xs text-slate-400 bg-slate-50">... แสดงตัวอย่าง 100 รายการแรกจากทั้งหมด ${list.length} รายการ ...</td></tr>` : '');
            },



            filterPrTable(q) {

                const query = (q || '').trim().toLowerCase();

                if (!query) {

                    this.renderPrTable(this.currentPrList);

                    return;

                }

                const filtered = this.currentPrList.filter(r => 

                    (r.pr && r.pr.toLowerCase().includes(query)) ||

                    (r.plant && r.plant.toLowerCase().includes(query)) ||

                    (r.date && r.date.toLowerCase().includes(query)) ||

                    (r.sup_post && r.sup_post.toLowerCase().includes(query))

                );

                this.renderPrTable(filtered);

            },



            async initDashboardData() {

                try {

                    const res = await fetch('/api/stats');

                    if (res.ok) {

                        const data = await res.json();

                        const stats = data.statistics || {};

                        

                        const cnt = document.getElementById('stat-count');

                        const dealsCnt = document.getElementById('stat-deals-count');

                        const savVal = document.getElementById('stat-savings-val');

                        

                        if (cnt && stats.total_prs) cnt.innerText = `${stats.total_prs.toLocaleString()} รายการ`;

                        if (dealsCnt && stats.total_deals) dealsCnt.innerText = `${stats.total_deals} ดีลหลัก`;

                        if (savVal && stats.total_savings_thb) {

                            savVal.innerHTML = `฿${Math.round(stats.total_savings_thb).toLocaleString()} <span class="text-xs font-normal">(-${stats.savings_pct}%)</span>`;

                        }



                        if (stats.stages_count) {

                            for (let s = 1; s <= 4; s++) {

                                const cEl = document.getElementById(`stage-count-${s}`);

                                const prEl = document.getElementById(`stage-prs-${s}`);

                                if (cEl) cEl.innerText = `${stats.stages_count[s] || 0} ดีล`;

                                if (prEl && stats.stages_prs) prEl.innerText = `${(stats.stages_prs[s] || 0).toLocaleString()} PRs`;

                            }

                        }

                    }

                } catch(e) {}

            },



            async initLiveEvents() {

                try {

                    const res = await fetch('/api/events');

                    if (res.ok) {

                        const data = await res.json();

                        if (data.events && data.events.length > 0) {

                            this.tickerMessages = data.events;

                            const el = document.getElementById('ticker-msg');

                            if (el) el.innerText = this.tickerMessages[0];

                        }

                    }

                } catch(e) {}

            },



            // ===== REAL-TIME (Server-Sent Events) =====

            // Supplier chat turns + ticker updates stream in live, no polling.

            _sse: null,

            initRealtime() {

                if (this._sse) return;

                try {

                    const es = new EventSource('/api/stream');

                    this._sse = es;



                    es.onmessage = (ev) => {

                        let data;

                        try { data = JSON.parse(ev.data); } catch (e) { return; }

                        if (!data || !data.type) return;



                        if (data.type === 'ticker' && data.text) {

                            // Prepend to the live ticker feed instantly.

                            this.tickerMessages = [data.text, ...(this.tickerMessages || [])].slice(0, 30);

                            const el = document.getElementById('ticker-msg');

                            if (el) el.innerText = data.text;

                        } else if (data.type === 'deal_triggered') {

                            this.handleDealTriggered(data);

                        } else if (data.type === 'deal_reset') {

                            this.handleDealReset(data);

                        } else if (data.type === 'negotiation') {

                            this.onLiveNegotiation(data);

                        }

                    };



                    es.onerror = () => {

                        // EventSource auto-reconnects; polling fallback (setInterval) stays active.

                    };

                } catch (e) {

                    // SSE unsupported — the existing polling fallback keeps the ticker alive.

                }

            },



            // Called when a supplier sends a message from the Supplier Portal.

            onLiveNegotiation(data) {

                const dealKey = (data.deal_id || '').toLowerCase();

                const deal = database.deals[dealKey];



                // Flash a toast so the buyer notices even if the cockpit is closed.

                if (this.showToast) {

                    const priceTxt = data.price ? ` · เสนอ ฿${Number(data.price).toLocaleString(undefined,{minimumFractionDigits:2})}` : '';

                    this.showToast(`🔔 ${data.vendor_name || 'คู่ค้า'} ส่งข้อเสนอสดในดีล ${(data.deal_id||'').toUpperCase()}${priceTxt}`, 'info');

                }



                if (!deal || !deal.vendors) return;



                // Match the vendor by name (backend slugs spaces/underscores).

                const slug = (s) => (s || '').replace(/ /g, '_').toLowerCase();

                const targetSlug = slug(data.vendor_name);

                let vIdx = deal.vendors.findIndex(v => slug(v.name) === targetSlug

                    || slug(v.name).includes(targetSlug) || targetSlug.includes(slug(v.name)));

                if (vIdx < 0) vIdx = 0;

                const vendor = deal.vendors[vIdx];

                if (!vendor) return;



                if (!Array.isArray(vendor.messages)) vendor.messages = [];

                // Append the supplier's message, then the AI reply, into the deal's transcript.

                if (data.vendor_text) {

                    vendor.messages.push({ sender: 'vendor', name: data.vendor_name || vendor.name, time: data.time || '', text: data.vendor_text });

                }

                if (data.agent_reply) {

                    vendor.messages.push({ sender: 'agent', name: 'AutoProcure AI (Procurement Agent)', time: data.time || '', text: data.agent_reply, tactic: data.tactic || '' });

                }



                // Live-update the vendor's commercial terms from the negotiation payload
                // so the Scorecard + Matrix reflect the latest offer, not stale seed data.
                if (data.price) vendor.price = `฿${Number(data.price).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`;
                if (data.credit_days) vendor.credit = `${data.credit_days} วัน`;
                const ct = data.commercial_terms || {};
                if (ct.lead_time_days) vendor.leadTime = `${ct.lead_time_days} วันทำการ`;
                if (ct.warranty_months) vendor.warranty = `${ct.warranty_months} เดือน`;
                if (ct.compliance_cert) vendor.cert = ct.compliance_cert;
                if (data.deal_agreed) { vendor.status = 'ชนะการประมูล (ออกใบ PO)'; vendor.statusBadge = 'badge-success text-white font-bold'; }
                // If the backend moved the deal to Stage 4, reflect it so sign-off unlocks live.
                if (data.stage === 4 && deal) deal.stage = 4;

                // If this exact deal + vendor cockpit is open, re-render it live.

                const modal = document.getElementById('chat_modal');

                const isOpen = modal && modal.open;

                if (isOpen && this.currentChatDealKey === dealKey) { this.renderRightPanel(deal, vIdx); }
                if (isOpen && this.currentChatDealKey === dealKey && this.currentChatVendorIndex === vIdx) {

                    this.renderVendorMessages(vendor);

                    lucide.createIcons({ root: modal });

                }

            },



            handleDealTriggered(data) {

                this.showToast(`⚡ [Auto-Trigger] ได้รับ PR จากระยอง (100 ตัว) ยอดรวมแตะ 850 ตัวครบเกณฑ์ ➔ AI ยิงเทียบเชิญ RFQ อัตโนมัติไปยังซัพพลายเออร์ 3 เจ้าผ่าน AWS SES สำเร็จ!`, 'info');

                const row = document.getElementById('row-deal-festo_cyl');

                if (row) {

                    row.classList.add('bg-blue-50/50', 'transition-all', 'duration-500');

                    setTimeout(() => row.classList.remove('bg-blue-50/50'), 2500);



                    const stageBadge = row.querySelector('.stage-badge-container');

                    if (stageBadge) {

                        stageBadge.innerHTML = `

                            <div class="inline-flex flex-col items-center justify-center px-2.5 py-1 rounded-lg bg-blue-50 border-blue-200 text-blue-800 shadow-xs">

                                <span class="font-bold text-[10px] font-mono leading-none">Stage 2</span>

                                <span class="text-[10px] font-medium mt-0.5 leading-tight whitespace-nowrap">เจรจาต่อรอง</span>

                            </div>

                        `;

                    }

                    const qtyEl = row.querySelector('.deal-qty-val');

                    if (qtyEl) qtyEl.innerHTML = `850 <span class="text-[10px] text-slate-500 font-normal">ชิ้น</span>`;

                    const prsBtn = row.querySelector('.deal-prs-btn');

                    if (prsBtn) prsBtn.innerHTML = `<i data-lucide="layers" class="w-3 h-3"></i> รวม 14 PRs`;

                    lucide.createIcons({ root: row });

                }

            },



            handleDealReset(data) {

                this.showToast(`🔄 รีเซ็ตดีล FESTO-DSBC-32-100 กลับสู่ Stage 1 สำหรับซ้อมเดโม`, 'info');

                const row = document.getElementById('row-deal-festo_cyl');

                if (row) {

                    const stageBadge = row.querySelector('.stage-badge-container');

                    if (stageBadge) {

                        stageBadge.innerHTML = `

                            <div class="inline-flex flex-col items-center justify-center px-2.5 py-1 rounded-lg bg-amber-50 border-amber-200 text-amber-800 shadow-xs">

                                <span class="font-bold text-[10px] font-mono leading-none">Stage 1</span>

                                <span class="text-[10px] font-medium mt-0.5 leading-tight whitespace-nowrap">รวบรวม PR</span>

                            </div>

                        `;

                    }

                    const qtyEl = row.querySelector('.deal-qty-val');

                    if (qtyEl) qtyEl.innerHTML = `750 <span class="text-[10px] text-slate-500 font-normal">ชิ้น</span>`;

                    const prsBtn = row.querySelector('.deal-prs-btn');

                    if (prsBtn) prsBtn.innerHTML = `<i data-lucide="layers" class="w-3 h-3"></i> รวม 13 PRs`;

                    const postPriceEl = row.querySelector('.deal-post-price');

                    if (postPriceEl) postPriceEl.innerText = '-';

                    const savingsEl = row.querySelector('.deal-savings-val');

                    if (savingsEl) savingsEl.innerText = '-';

                    lucide.createIcons({ root: row });

                }

            },



            // Fire a real (or simulated) AWS SES invite from the email modal.

            async sendRealInvite() {

                const dealKey = this.currentEmailDealKey || 'nsk';

                const vIdx = this.currentEmailVendorIndex || 0;

                const input = document.getElementById('email-real-recipient');

                const statusEl = document.getElementById('email-send-status');

                const btn = document.getElementById('btn-send-real-invite');

                const prefilled = (document.getElementById('email-recipient-address') || {}).innerText || '';

                const email = ((input && input.value.trim()) || prefilled).trim();



                if (!email) {

                    if (statusEl) statusEl.innerHTML = '<span class="text-amber-400">⚠ กรุณาระบุอีเมลผู้รับก่อนส่ง</span>';

                    return;

                }



                // Resolve vendor id/name from the selected deal's vendor list.

                const deal = (database.deals && database.deals[dealKey]) || {};

                const vendors = (this.masterDeals && this.masterDeals[dealKey] && this.masterDeals[dealKey].vendors) || deal.vendors || [];

                const vendor = vendors[vIdx] || vendors[0] || {};

                const vendorId = (vendor.id || 'sp').toLowerCase();

                const vendorName = vendor.name || deal.title || 'บจก. คู่ค้า AVL';



                if (btn) btn.disabled = true;

                if (statusEl) statusEl.innerHTML = '<span class="text-slate-300">⏳ กำลังส่งคำเชิญผ่าน AWS SES...</span>';



                try {

                    const res = await fetch('/api/send-invite', {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({ deal_id: dealKey, vendor_id: vendorId, vendor_name: vendorName, email })

                    });

                    const data = await res.json();

                    if (res.ok && data.status === 'live_ses') {

                        if (statusEl) statusEl.innerHTML = `<span class="text-emerald-400">✓ ส่งจริงสำเร็จ → ${email} (MessageId: ${data.message_id || 'n/a'})</span>`;

                        this.showToast(`ส่งอีเมลคำเชิญจริงผ่าน AWS SES ไปยัง ${email} สำเร็จ`, 'success');

                    } else if (res.ok && data.status === 'simulated') {

                        if (statusEl) statusEl.innerHTML = `<span class="text-blue-300">ℹ โหมดจำลอง (SES_ENABLED=false): ${data.detail || ''} → ${email}</span>`;

                        this.showToast(`จำลองการส่งคำเชิญไปยัง ${email} (เปิด SES_ENABLED=true เพื่อส่งจริง)`, 'info');

                    } else {

                        if (statusEl) statusEl.innerHTML = `<span class="text-amber-400">⚠ ${data.detail || 'ส่งไม่สำเร็จ'}</span>`;

                    }

                } catch (err) {

                    if (statusEl) statusEl.innerHTML = '<span class="text-rose-400">✕ เชื่อมต่อเซิร์ฟเวอร์ไม่สำเร็จ</span>';

                } finally {

                    if (btn) btn.disabled = false;

                }

            },



            currentFilter: 'all',

            currentStage: null,

            tickerIndex: 0,

            tickerMessages: [

                "[14:52:10] Agent กำลังคำนวณสมการ TCO สำหรับสายพาน Bando... รวบรวมข้อมูลใบเสนอราคาจาก 4 ซัพพลายเออร์",

                "[14:52:28] ส่ง Counter-offer เจรจารอบที่ 2 ให้ บจก. สยาม อิเล็คทริค (เบรกเกอร์ Schneider)... เป้าหมาย ฿7,200",

                "[14:52:45] ดึงเอกสารมาตรฐานสเปก JIS B 1514 จากคลัง Vector DB (FAISS + Tsuzumi SLM)...",

                "[14:53:02] Guardrail Agent ตรวจสอบความถูกต้องของสัญญาสยาม พรีซิชั่น [ผ่านเกณฑ์ระเบียบ 100%]"

            ],



            toggleSidebar() {

                const sidebar = document.getElementById('app-sidebar');

                if (!sidebar) return;

                

                // Toggle collapsed mode (w-64 <-> w-16) or hidden on small screens

                const isCollapsed = sidebar.classList.contains('w-16');

                if (isCollapsed) {

                    sidebar.classList.remove('w-16');

                    sidebar.classList.add('w-64');

                    document.querySelectorAll('.sidebar-text').forEach(el => el.classList.remove('hidden'));

                    const toggleIcon = document.getElementById('sidebar-toggle-icon');

                    if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevrons-left');

                    const footerIcon = document.getElementById('sidebar-footer-icon');

                    if (footerIcon) footerIcon.setAttribute('data-lucide', 'chevrons-left');

                } else {

                    sidebar.classList.remove('w-64');

                    sidebar.classList.add('w-16');

                    document.querySelectorAll('.sidebar-text').forEach(el => el.classList.add('hidden'));

                    const toggleIcon = document.getElementById('sidebar-toggle-icon');

                    if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevrons-right');

                    const footerIcon = document.getElementById('sidebar-footer-icon');

                    if (footerIcon) footerIcon.setAttribute('data-lucide', 'chevrons-right');

                }

                lucide.createIcons();

            },



            switchView(viewName) {

                const viewLabels = {

                    'pipeline': 'กระดานจัดซื้อสด (Live Sourcing Pipeline) 60 ดีล',

                    'governance': 'ศูนย์กำกับดูแลและการลงนามสัญญา (HITL Sign-Off)',

                    'analytics': 'รายงานวิเคราะห์ ROI & สถิติเศรษฐศาสตร์จัดซื้อ'

                };

                if (this.pushLiveEvent) this.pushLiveEvent(`สลับมุมมองหน้าจอ: ${viewLabels[viewName] || viewName}`);

                ['pipeline', 'governance', 'analytics'].forEach(v => {

                    const el = document.getElementById(`view-${v}`);

                    const nav = document.getElementById(`nav-${v}`);

                    if (el) el.classList.add('hidden');

                    if (nav) nav.classList.remove('active', 'bg-blue-50', 'text-blue-700');

                });



                const activeView = document.getElementById(`view-${viewName}`);

                const activeNav = document.getElementById(`nav-${viewName}`);

                if (activeView) activeView.classList.remove('hidden');

                if (activeNav) activeNav.classList.add('active', 'bg-blue-50', 'text-blue-700');



                // Smooth scroll to top of content

                const scrollArea = document.getElementById('main-scroll-area');

                if (scrollArea) scrollArea.scrollTop = 0;

                lucide.createIcons();



                // Lazy-load the live governance panels when that view opens.

                if (viewName === 'governance') {
                    this.initAwardDealOptions();
                    this.loadAwardBoard();
                    this.loadSlaMonitor();
                } else if (viewName === 'analytics') {
                    this.initAnalyticsCharts();
                }

            },



            // ===== Multi-Vendor Award Board + SLA Monitor (governance view) =====

            initAwardDealOptions() {

                const sel = document.getElementById('award-deal-select');

                if (!sel || sel.dataset.ready) return;

                const deals = (database && database.deals) ? Object.keys(database.deals) : ['nsk'];

                sel.innerHTML = deals.map(d => `<option value="${d}">${d.toUpperCase()}</option>`).join('');

                sel.dataset.ready = '1';

            },



            async loadAwardBoard() {

                const sel = document.getElementById('award-deal-select');

                const body = document.getElementById('award-board-body');

                if (!body) return;

                const dealKey = (sel && sel.value) || 'nsk';

                body.innerHTML = '<div class="text-center py-4 text-slate-400"><span class="loading loading-spinner loading-xs"></span> กำลังประเมิน...</div>';

                try {

                    const res = await fetch(`/api/deals/${dealKey}/award-board`);

                    const data = await res.json();

                    if (!data.vendors || data.vendors.length === 0) {

                        body.innerHTML = '<div class="text-center py-6 text-slate-400">ยังไม่มีการเจรจาในดีลนี้ (เริ่มเจรจาในห้องคู่ค้าเพื่อให้ระบบจัดอันดับ)</div>';

                        return;

                    }

                    const winnerTxt = data.winner

                        ? `<div class="mb-2 px-3 py-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-1.5"><i data-lucide="award" class="w-4 h-4"></i> ผู้ชนะ BAFO: ${data.winner.vendor_id.replace(/_/g,' ')} (TCO ${data.winner.tco_score})</div>`

                        : '<div class="mb-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-xs">ยังไม่มีผู้ผ่านเกณฑ์ชนะ (ต้องมี TCO ≥ 75 หรือได้ลงนาม)</div>';

                    const rows = data.vendors.map(v => {

                        const medal = v.rank === 1 ? '🥇' : (v.rank === 2 ? '🥈' : (v.rank === 3 ? '🥉' : `#${v.rank}`));

                        const guard = v.guard_adjusted ? ' <span class="text-[9px] text-amber-600" title="ปรับตามหลัก Consistency Guard">⚖︎</span>' : '';

                        const win = v.is_winner ? 'bg-emerald-50/60 font-semibold' : '';

                        return `<tr class="${win}">

                            <td class="py-1.5 px-2">${medal}</td>

                            <td class="py-1.5 px-2 truncate max-w-[150px]" title="${v.vendor_id}">${v.vendor_id.replace(/_/g,' ')}</td>

                            <td class="py-1.5 px-2 text-right font-mono font-bold text-blue-800">${v.latest_tco_score}${guard}</td>

                            <td class="py-1.5 px-2 text-right font-mono text-slate-500">${v.best_price ? '฿'+Number(v.best_price).toLocaleString() : '-'}</td>

                            <td class="py-1.5 px-2 text-center font-mono text-slate-500">${v.rounds}</td>

                        </tr>`;

                    }).join('');

                    body.innerHTML = winnerTxt + `<table class="table table-xs w-full"><thead class="text-[10px] text-slate-400 uppercase"><tr><th class="py-1 px-2">#</th><th class="py-1 px-2">คู่ค้า</th><th class="py-1 px-2 text-right">TCO</th><th class="py-1 px-2 text-right">ราคา</th><th class="py-1 px-2 text-center">รอบ</th></tr></thead><tbody>${rows}</tbody></table>`;

                    lucide.createIcons({ root: body.parentElement });

                } catch (e) {

                    body.innerHTML = '<div class="text-center py-4 text-rose-400">โหลดข้อมูลไม่สำเร็จ</div>';

                }

            },



            async loadSlaMonitor() {

                const body = document.getElementById('sla-monitor-body');

                if (!body) return;

                body.innerHTML = '<div class="text-center py-4 text-slate-400"><span class="loading loading-spinner loading-xs"></span> กำลังตรวจสอบ...</div>';

                try {

                    const res = await fetch('/api/sla');

                    const data = await res.json();

                    if (!data.sessions || data.sessions.length === 0) {

                        body.innerHTML = '<div class="text-center py-6 text-slate-400">ยังไม่มีเซสชันการเจรจา</div>';

                        return;

                    }

                    const badge = { active: 'badge-success', due_soon: 'badge-warning', stalled: 'badge-error', closed: 'badge-ghost' };

                    const label = { active: 'ปกติ', due_soon: 'ใกล้ครบกำหนด', stalled: 'ค้าง (ต้องตาม)', closed: 'ปิดแล้ว' };

                    const stalledNote = data.stalled_count > 0

                        ? `<div class="mb-2 px-3 py-1.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold">⚠ พบ ${data.stalled_count} เซสชันค้างเกิน SLA ${data.sla_hours} ชม. — ควรส่ง follow-up</div>`

                        : `<div class="mb-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs">ทุกเซสชันอยู่ในกรอบ SLA (${data.sla_hours} ชม.)</div>`;

                    const rows = data.sessions.map(s => `<tr>

                        <td class="py-1.5 px-2 truncate max-w-[140px]" title="${s.deal_id}/${s.vendor_id}">${(s.vendor_id||'').replace(/_/g,' ')}</td>

                        <td class="py-1.5 px-2 text-right font-mono text-slate-500">${s.hours_idle}h</td>

                        <td class="py-1.5 px-2 text-center"><span class="badge badge-xs ${badge[s.status]||'badge-ghost'}">${label[s.status]||s.status}</span></td>

                    </tr>`).join('');

                    body.innerHTML = stalledNote + `<table class="table table-xs w-full"><thead class="text-[10px] text-slate-400 uppercase"><tr><th class="py-1 px-2">คู่ค้า</th><th class="py-1 px-2 text-right">เงียบ</th><th class="py-1 px-2 text-center">สถานะ</th></tr></thead><tbody>${rows}</tbody></table>`;

                } catch (e) {

                    body.innerHTML = '<div class="text-center py-4 text-rose-400">โหลดข้อมูลไม่สำเร็จ</div>';

                }

            },



            filterCat(cat) {

                this.currentFilter = cat;

                document.querySelectorAll('[id^="tab-cat-"]').forEach(el => el.classList.remove('tab-active'));

                const activeTab = document.getElementById(`tab-cat-${cat}`);

                if (activeTab) activeTab.classList.add('tab-active');

                this.applyFilters();

            },



            filterStage(stageNum) {

                if (this.currentStage === stageNum) {

                    this.currentStage = null;

                } else {

                    this.currentStage = stageNum;

                }



                document.querySelectorAll('.step-filter-btn').forEach(b => {

                    b.classList.remove('border-blue-600', 'bg-blue-50', 'ring-2', 'ring-blue-400/30');

                    b.classList.add('border-slate-200', 'bg-white');

                });



                const clearBtn = document.getElementById('btn-clear-filter');

                if (this.currentStage) {

                    const activeBtn = document.getElementById(`filter-step-${this.currentStage}`);

                    if (activeBtn) {

                        activeBtn.classList.remove('border-slate-200', 'bg-white');

                        activeBtn.classList.add('border-blue-600', 'bg-blue-50', 'ring-2', 'ring-blue-400/30');

                    }

                    if (clearBtn) clearBtn.classList.remove('hidden');

                } else {

                    if (clearBtn) clearBtn.classList.add('hidden');

                }



                this.applyFilters();

            },



            clearFilters() {

                this.currentStage = null;

                this.currentFilter = 'all';

                document.querySelectorAll('.step-filter-btn').forEach(b => {

                    b.classList.remove('border-blue-600', 'bg-blue-50', 'ring-2', 'ring-blue-400/30');

                    b.classList.add('border-slate-200', 'bg-white');

                });

                document.querySelectorAll('[id^="tab-cat-"]').forEach(el => el.classList.remove('tab-active'));

                const tabAll = document.getElementById('tab-cat-all');

                if (tabAll) tabAll.classList.add('tab-active');

                const clearBtn = document.getElementById('btn-clear-filter');

                if (clearBtn) clearBtn.classList.add('hidden');

                this.applyFilters();

            },



            currentDisplayMode: 'table',



            switchDisplayMode(mode) {

                this.currentDisplayMode = mode;

                const modes = ['table', 'cards', 'kanban'];



                modes.forEach(m => {

                    const container = document.getElementById(`container-mode-${m}`);

                    const btn = document.getElementById(`btn-mode-${m}`);

                    if (container) {

                        if (m === mode) {

                            container.classList.remove('hidden');

                        } else {

                            container.classList.add('hidden');

                        }

                    }

                    if (btn) {

                        if (m === mode) {

                            btn.className = 'btn btn-xs rounded-lg font-medium gap-1 bg-white shadow-sm text-blue-700 border border-slate-200 transition-all';

                        } else {

                            btn.className = 'btn btn-xs btn-ghost text-slate-600 rounded-lg font-medium gap-1 transition-all';

                        }

                    }

                });



                this.applyFilters();

                lucide.createIcons();

            },



            updateStageCounters() {

                for (let s = 1; s <= 4; s++) {

                    const count = document.querySelectorAll(`.job-row[data-stage="${s}"]`).length;

                    const el = document.getElementById(`stage-count-${s}`);

                    if (el) el.innerText = count;

                }

            },



            getDeal(dealKey) {
                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';
                const db = (typeof database !== 'undefined') ? database : (typeof window !== 'undefined' ? window.database : null);
                let deal = (db && db.deals) ? db.deals[dealKey] : null;
                
                // If deal already exists in data.js, ensure deal.stage accurately reflects DOM/status
                if (deal) {
                    if (deal.stage === undefined || deal.stage === null) {
                        const row = document.querySelector(`button[onclick*="'${dealKey}'"]`)?.closest('tr');
                        if (row && row.getAttribute('data-stage')) {
                            deal.stage = parseInt(row.getAttribute('data-stage'), 10);
                        } else {
                            const hasWinner = deal.vendors && deal.vendors.some(v => v.status && (v.status.includes('ชนะ') || v.status.includes('PO')));
                            deal.stage = hasWinner ? 4 : 3;
                        }
                    }
                    return deal;
                }

                // If not seeded in database.deals, build dynamically from index.html DOM row
                const row = document.querySelector(`button[onclick*="'${dealKey}'"]`)?.closest('tr');
                let title = dealKey.toUpperCase();
                let partCode = dealKey.toUpperCase();
                let budgetStr = 'ตามราคาตลาด';
                let targetStr = 'คำนวณตามเกณฑ์ TCO';
                let stage = 2;

                if (row) {
                    const stageAttr = row.getAttribute('data-stage');
                    if (stageAttr) stage = parseInt(stageAttr, 10);
                    const skuEl = row.querySelector('.font-mono.text-blue-900');
                    if (skuEl) partCode = skuEl.innerText.trim();
                    const descEl = row.querySelector('.text-slate-600.truncate');
                    if (descEl) title = `${descEl.innerText.trim()} (${partCode})`;
                    const priceCells = row.querySelectorAll('td.text-right.font-mono');
                    if (priceCells.length >= 2) {
                        budgetStr = `${priceCells[0].innerText.trim()}/หน่วย`;
                        targetStr = `${priceCells[1].innerText.trim()}/หน่วย (เป้าหมาย TCO)`;
                    }
                }

                const isStage4 = stage === 4;
                deal = {
                    title: title,
                    part_code: partCode,
                    budgetStr: budgetStr,
                    targetStr: targetStr,
                    stage: stage,
                    chips: [
                        `ขอราคาพิเศษตามสัญญาวอลลุ่ม ${partCode}`,
                        "ขอขยายเครดิตเทอมเป็น 45 วัน",
                        "การันตีระยะเวลาส่งมอบสินค้าภายใน 7 วัน",
                        "ขอใบรับรองมาตรฐานสินค้า (Certificate of Quality)"
                    ],
                    vendors: [
                        {
                            id: `v_${dealKey}_1`,
                            name: "บจก. สยาม อุตสาหกรรม ซัพพลาย (AVL Tier-1)",
                            email: "contact@siam-industrial.co.th",
                            price: budgetStr.split('/')[0] || "฿1,500.00",
                            credit: "30 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "1 ปี",
                            cert: "ISO 9001 / OEM Certified ✓",
                            status: isStage4 ? "ชนะการประมูล (พร้อมอนุมัติ)" : (stage === 3 ? "อยู่ระหว่างการเจรจา (Stage 3)" : (stage === 2 ? "รอเริ่มเจรจา (Stage 2)" : "รอรับใบเสนอราคา (Stage 1)")),
                            statusBadge: isStage4 ? "badge-success text-white font-bold" : (stage === 3 ? "badge-warning font-bold" : "badge-info text-white font-bold"),
                            outcome: isStage4 ? "เจรจาได้ข้อสรุปตามกรอบ TCO ครบถ้วน พร้อมเข้าสู่ขั้นตอนอนุมัติ PO ใน SAP" : (stage === 3 ? "ระบบส่งข้อเสนอต่อรองรอบที่ 2 รอคู่ค้ายืนยันราคา" : "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย"),
                            ladder: [],
                            messages: []
                        },
                        {
                            id: `v_${dealKey}_2`,
                            name: "บจก. ไทย พาร์ท แมชชีนเนอรี่ (AVL Tier-2)",
                            email: "sales@thaipart.co.th",
                            price: budgetStr.split('/')[0] || "฿1,550.00",
                            credit: "30 วัน",
                            leadTime: "10 วันทำการ",
                            warranty: "1 ปี",
                            cert: "Standard Industrial Warranty ✓",
                            status: isStage4 ? "ราคาสูงกว่าคู่แข่ง (ไม่ได้คัดเลือก)" : (stage === 3 ? "อยู่ระหว่างการเจรจา (Stage 3)" : "รอเริ่มเจรจา (ห้องว่างสด)"),
                            statusBadge: isStage4 ? "badge-ghost text-slate-500" : (stage === 3 ? "badge-warning font-bold" : "badge-info text-white font-bold"),
                            outcome: isStage4 ? "ราคาสูงกว่าคู่ค้ารายแรกและไม่สามารถขยายเครดิตเทอมได้ตามข้อกำหนด" : "รอเปิดห้องเจรจาหรือรับข้อเสนอผ่าน Supplier Portal",
                            ladder: [],
                            messages: []
                        }
                    ]
                };

                window.database.deals[dealKey] = deal;
                return deal;
            },

            async resetCurrentChat() {

                const dealKey = this.currentChatDealKey || 'nsk';

                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                const vendorIndex = this.currentChatVendorIndex || 0;

                const vendor = deal.vendors && deal.vendors[vendorIndex];

                if (!vendor) return;



                const cleanVId = vendor.name.replace(/ /g, '_').toLowerCase();

                try {

                    await fetch(`/api/chat/${dealKey}/${encodeURIComponent(cleanVId)}/reset`, { method: 'POST' });

                } catch(e) {}



                vendor.messages = [];

                vendor.ladder = [];

                this.renderVendorMessages(vendor);

                this.renderRightPanel(deal, vendorIndex);



                // Update Cockpit Header Sign-off Button State

                const headerSignOff = document.getElementById('chat-header-signoff-btn');

                if (headerSignOff) {

                    const isWinner = vendor.status && (vendor.status.includes('ชนะ') || vendor.status.includes('PO'));

                    if (deal.stage === 4 && (vendorIndex === 0 || isWinner)) {

                        headerSignOff.className = 'btn btn-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg gap-1 border border-emerald-400/40 shadow-sm cursor-pointer transition-all';

                        headerSignOff.innerHTML = '<i data-lucide="file-check-2" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">ได้ข้อสรุปแล้ว ➔ ลงนาม PO</span>';

                        headerSignOff.onclick = () => app.openSignOff(this.currentChatDealKey);

                        headerSignOff.title = 'ได้ข้อสรุปแล้ว ➔ ลงนามสัญญาดิจิทัลใน SAP';

                    } else {

                        headerSignOff.className = 'btn btn-xs bg-slate-800 text-slate-400 border border-slate-700 rounded-lg gap-1 cursor-not-allowed opacity-60 hover:bg-slate-750 transition-all';

                        headerSignOff.innerHTML = '<i data-lucide="lock" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">ยังไม่พร้อมลงนาม</span>';

                        headerSignOff.onclick = () => app.showToast('การเจรจากับคู่ค้ารายนี้ยังไม่ได้ข้อสรุป กรุณาดำเนินการต่อรองให้เสร็จสิ้นก่อนลงนามสัญญา', 'info');

                        headerSignOff.title = 'ยังไม่สามารถลงนามได้ (อยู่ระหว่างการเจรจาต่อรอง)';

                    }

                }

                this.showToast(`รีเซ็ตห้องเจรจา ${vendor.name} เรียบร้อยแล้ว`, 'info');

                lucide.createIcons({ root: document.getElementById('chat_modal') });

            },



            viewPrsForDeal(searchKeyword) {

                this.switchDataMode('dataset');

                const searchInput = document.getElementById('dataset-search-input');

                if (searchInput) {

                    searchInput.value = searchKeyword;

                    this.searchDataset();

                }

                const container = document.getElementById('container-2500-dataset');

                if (container) container.scrollIntoView({ behavior: 'smooth' });

                this.showToast(`กรองประวัติ PR สำหรับ ${searchKeyword}`, 'info');

            },



            applyFilters() {

                this.updateStageCounters();

                const items = document.querySelectorAll('.job-item, .job-row, .job-kanban-card');

                let visibleCount = 0;



                items.forEach(card => {

                    const matchCat = (this.currentFilter === 'all' || card.dataset.category === this.currentFilter);

                    const matchStage = (!this.currentStage || parseInt(card.dataset.stage) === this.currentStage);



                    if (matchCat && matchStage) {

                        card.classList.remove('hidden');

                        if (card.classList.contains('job-row')) visibleCount++;

                    } else {

                        card.classList.add('hidden');

                    }

                });



                const statCount = document.getElementById('stat-deals-count');

                if (statCount) statCount.innerText = `${visibleCount} ดีลหลัก`;

            },



            // SIMULATE LIVE AGENT ACTIVITY

            async simulateAgentTick() {

                try {

                    const res = await fetch('/api/negotiate', {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({

                            deal_id: 'nsk',

                            vendor_id: 'v_siam',

                            message: 'ระบบขอสอบถามความคืบหน้าการส่งมอบและยืนยันส่วนลดตามเงื่อนไขสัญญา 1 ปี'

                        })

                    });

                    if (res.ok) {

                        const data = await res.json();

                        this.showToast(`⚡ Agent ส่งคำขอสำเร็จ: ${data.reply ? data.reply.substring(0, 45) + '...' : 'อัปเดตสตรีมแล้ว'}`, 'success');

                        if (this.initLiveEvents) await this.initLiveEvents();

                    } else {

                        this.tickerIndex = (this.tickerIndex + 1) % this.tickerMessages.length;

                        document.getElementById('ticker-msg').innerText = this.tickerMessages[this.tickerIndex];

                        this.showToast('⚡ ส่งคำสั่ง Trigger Agent เรียบร้อย (สตรีมคำนวณราคาและบันทึกเหตุการณ์สด)', 'info');

                    }

                } catch (e) {

                    this.tickerIndex = (this.tickerIndex + 1) % this.tickerMessages.length;

                    document.getElementById('ticker-msg').innerText = this.tickerMessages[this.tickerIndex];

                    this.showToast('⚡ รัน Trigger สำเร็จ (อัปเดตสตรีมกิจกรรม)', 'info');

                }

            },



            // ================= AUTONOMOUS NEGOTIATION COCKPIT (สลับดูแต่ละเจ้า & จำลองต่อรองสดได้จริง) =================

            currentChatDealKey: null,

            currentChatVendorIndex: 0,



            async openChatModal(dealKey) {

                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                this.currentChatDealKey = dealKey;

                this.currentChatVendorIndex = 0;



                const titleEl = document.getElementById('chat-modal-title');

                if (titleEl) titleEl.innerText = `ห้องควบคุมการเจรจาต่อรองคู่ค้า: ${deal.title}`;

                this.pushLiveEvent(`เปิดห้องเจรจา: ${deal.title} (${deal.part_code || dealKey.toUpperCase()}) ดึงประวัติคู่ค้าและเพดานราคาตลาด`, true);



                const subEl = document.getElementById('chat-modal-subtitle');

                if (subEl) {

                    if (deal.vendors && deal.vendors.length > 1) {

                        subEl.innerText = `เปิดห้องเจรจาต่อรองคู่ขนาน ${deal.vendors.length} ซัพพลายเออร์ (Approved Vendor List - AVL) ด้วย Autonomous Negotiation Engine`;

                    } else {

                        subEl.innerText = `ห้องเจรจาต่อรองออนไลน์รายซัพพลายเออร์ (Approved Vendor List - AVL)`;

                    }

                }



                // Populate Deal Metrics Strip

                const bEl = document.getElementById('chat-stat-budget');

                const tEl = document.getElementById('chat-stat-target');

                if (bEl) bEl.innerText = deal.budgetStr || 'ตามงบประมาณเดิม';

                if (tEl) tEl.innerText = deal.targetStr || 'คำนวณจาก TCO';



                // Reset simulation button

                const btnSim = document.getElementById('btn-simulate-round');

                if (btnSim) {

                    btnSim.disabled = false;

                    btnSim.innerHTML = `<i data-lucide="play-circle" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">จำลองต่อรอง (Next Round)</span>`;

                }



                // Render Vendor Tabs

                const tabsContainer = document.getElementById('chat-vendor-tabs');

                if (tabsContainer && deal.vendors) {

                    let tabsHtml = '';

                    deal.vendors.forEach((v, idx) => {

                        const isActive = idx === 0;

                        const cleanName = v.name.replace('บจก. ', '');

                        tabsHtml += `

                            <button onclick="app.switchVendorChat('${dealKey}', ${idx})" id="vtab-${idx}" class="btn btn-xs rounded-full ${isActive ? 'btn-primary text-white shadow-sm' : 'btn-ghost bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'} gap-1.5 shrink-0 font-medium transition-all" title="${v.name}">

                                <span class="max-w-[140px] truncate">${cleanName}</span>

                                <span class="badge badge-xs ${v.statusBadge}">${v.status.includes('ชนะ') ? 'ชนะดีล (PO)' : (v.status.includes('SLA') ? 'ตกรอบ SLA' : (v.status.includes('รอ') ? 'รอเริ่มเจรจา' : 'ราคาสูง'))}</span>

                            </button>

                        `;

                    });

                    tabsContainer.innerHTML = tabsHtml;

                }



                // Try load persisted session from API

                const vendor0 = deal.vendors && deal.vendors[0];

                if (vendor0) {

                    const cleanVId = vendor0.name.replace(/ /g, '_').toLowerCase();

                    try {

                        const res = await fetch(`/api/chat/${dealKey}/${encodeURIComponent(cleanVId)}`);

                        if (res.ok) {

                            const data = await res.json();

                            if (data.session && data.session.messages && data.session.messages.length > 0) {

                                vendor0.messages = data.session.messages;

                                if (data.session.concession_ladder && data.session.concession_ladder.length > 0) {

                                    vendor0.ladder = data.session.concession_ladder;

                                }

                            }

                        }

                    } catch(e) {}

                }



                this.renderChatContent(deal, 0);

                document.getElementById('chat_modal').showModal();

                lucide.createIcons({ root: document.getElementById('chat_modal') });

            },



            async switchVendorChat(dealKey, vendorIndex) {

                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                this.currentChatDealKey = dealKey;

                this.currentChatVendorIndex = vendorIndex;



                document.querySelectorAll('#chat-vendor-tabs button').forEach((btn, idx) => {

                    if (idx === vendorIndex) {

                        btn.className = 'btn btn-xs rounded-full btn-primary text-white shadow-sm gap-1.5 shrink-0 font-medium transition-all';

                    } else {

                        btn.className = 'btn btn-xs rounded-full btn-ghost bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 gap-1.5 shrink-0 font-medium transition-all';

                    }

                });



                const vendorCurr = deal.vendors && deal.vendors[vendorIndex];

                if (vendorCurr) {

                    const cleanVId = vendorCurr.name.replace(/ /g, '_').toLowerCase();

                    try {

                        const res = await fetch(`/api/chat/${dealKey}/${encodeURIComponent(cleanVId)}`);

                        if (res.ok) {

                            const data = await res.json();

                            if (data.session && data.session.messages && data.session.messages.length > 0) {

                                vendorCurr.messages = data.session.messages;

                                if (data.session.concession_ladder && data.session.concession_ladder.length > 0) {

                                    vendorCurr.ladder = data.session.concession_ladder;

                                }

                            }

                        }

                    } catch(e) {}

                }



                this.renderChatContent(deal, vendorIndex);

                lucide.createIcons({ root: document.getElementById('chat_modal') });

            },



            renderChatContent(deal, vendorIndex) {

                if (!deal || !deal.vendors || !deal.vendors[vendorIndex]) return;

                const vendor = deal.vendors[vendorIndex];

                this.renderVendorMessages(vendor);

                this.renderRightPanel(deal, vendorIndex);



                // Update Cockpit Header Sign-off Button State

                const headerSignOff = document.getElementById('chat-header-signoff-btn');

                if (headerSignOff) {

                    const isWinner = vendor.status && (vendor.status.includes('ชนะ') || vendor.status.includes('PO'));

                    if (deal.stage === 4 && (vendorIndex === 0 || isWinner)) {

                        headerSignOff.className = 'btn btn-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg gap-1 border border-emerald-400/40 shadow-sm cursor-pointer transition-all';

                        headerSignOff.innerHTML = '<i data-lucide="file-check-2" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">ได้ข้อสรุปแล้ว ➔ ลงนาม PO</span>';

                        headerSignOff.onclick = () => app.openSignOff(this.currentChatDealKey);

                        headerSignOff.title = 'ได้ข้อสรุปแล้ว ➔ ลงนามสัญญาดิจิทัลใน SAP';

                    } else {

                        headerSignOff.className = 'btn btn-xs bg-slate-800 text-slate-400 border border-slate-700 rounded-lg gap-1 cursor-not-allowed opacity-60 hover:bg-slate-750 transition-all';

                        headerSignOff.innerHTML = '<i data-lucide="lock" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">ยังไม่พร้อมลงนาม</span>';

                        headerSignOff.onclick = () => app.showToast('การเจรจากับคู่ค้ารายนี้ยังไม่ได้ข้อสรุป กรุณาดำเนินการต่อรองให้เสร็จสิ้นก่อนลงนามสัญญา', 'info');

                        headerSignOff.title = 'ยังไม่สามารถลงนามได้ (อยู่ระหว่างการเจรจาต่อรอง)';

                    }

                }

            },



            renderVendorMessages(vendor) {

                const container = document.getElementById('chat-messages-container');

                if (!container) return;

                if (!vendor.messages || vendor.messages.length === 0) {

                    container.innerHTML = `

                        <div class="flex flex-col items-center justify-center py-12 text-center text-slate-400">

                            <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3 border border-slate-200 shadow-inner">

                                <i data-lucide="messages-square" class="w-6 h-6"></i>

                            </div>

                            <div class="font-bold text-slate-700 text-sm">ห้องเจรจาว่างสด — ยังไม่มีประวัติการพูดคุย</div>

                            <div class="text-xs text-slate-500 mt-1 max-w-sm">คุณสามารถคลิกปุ่มกลยุทธ์ด้านล่างเพื่อส่งข้อเสนอแรก หรือส่งอีเมลเชิญคู่ค้าเข้าเจรจาผ่าน Supplier Portal</div>

                        </div>

                    `;

                    return;

                }

                let html = '';



                vendor.messages.forEach(m => {

                    if (m.sender === 'vendor') {

                        html += `

                            <div class="chat chat-start">

                                <div class="chat-image avatar placeholder">

                                    <div class="bg-slate-200 text-slate-700 rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center border border-slate-300">V</div>

                                </div>

                                <div class="chat-header text-[11px] text-slate-500 mb-0.5 flex items-center gap-1.5">

                                    <span class="font-semibold text-slate-700">${m.name}</span>

                                    <time class="text-[10px] opacity-60 font-mono">${m.time}</time>

                                </div>

                                <div class="chat-bubble bg-slate-100 text-slate-800 text-xs shadow-sm border border-slate-200/80 leading-relaxed max-w-[85%]">

                                    ${m.text}

                                </div>

                            </div>

                        `;

                    } else {

                        html += `

                            <div class="chat chat-end">

                                <div class="chat-image avatar placeholder">

                                    <div class="bg-blue-700 text-white rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center shadow">AI</div>

                                </div>

                                <div class="chat-header text-[11px] text-slate-500 mb-0.5 flex items-center gap-1.5 justify-end">

                                    <time class="text-[10px] opacity-60 font-mono">${m.time}</time>

                                    <span class="font-semibold text-blue-900">${m.name}</span>

                                </div>

                                <div class="chat-bubble bg-gradient-to-r from-blue-700 to-indigo-700 text-white text-xs shadow-md border border-blue-600/50 leading-relaxed max-w-[85%]">

                                    ${m.text}

                                </div>

                                ${m.tactic ? `<div class="chat-footer text-[10px] font-mono text-blue-800 mt-1 font-semibold flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded border border-blue-200"><i data-lucide="crosshair" class="w-3 h-3 text-blue-600 inline"></i> ${m.tactic}</div>` : ''}

                            </div>

                        `;

                    }

                });



                container.innerHTML = html;

                container.scrollTop = container.scrollHeight;



                const footerEl = document.getElementById('chat-footer-bar');

                if (footerEl) {

                    const deal = this.getDeal(this.currentChatDealKey);
                    const vendorIndex = this.currentChatVendorIndex || 0;
                    const isWinner = vendor.status && (vendor.status.includes('ชนะ') || vendor.status.includes('PO'));
                    const canSignOff = deal && deal.stage === 4 && (vendorIndex === 0 || isWinner);

                    footerEl.innerHTML = `

                        <div class="flex items-center gap-2 flex-wrap">

                            <span class="badge badge-sm ${vendor.statusBadge}">${vendor.status}</span>

                            <span class="font-medium text-slate-700 text-xs">${vendor.outcome}</span>

                        </div>

                        <div class="flex items-center gap-2">

                            ${canSignOff ? `<button type="button" onclick="app.openSignOff('${this.currentChatDealKey}')" class="btn btn-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg px-3 py-1 shadow-xs flex items-center gap-1"><i data-lucide="file-check-2" class="w-3.5 h-3.5"></i> <span>ได้ข้อสรุปแล้ว ➔ ลงนามสัญญา PO</span></button>` : `<button type="button" onclick="app.showToast('การเจรจากับคู่ค้ารายนี้ยังไม่ได้ข้อสรุป กรุณาดำเนินการต่อรองให้เสร็จสิ้นก่อนลงนามสัญญา', 'info')" class="btn btn-xs bg-slate-100 text-slate-400 border border-slate-200 rounded-lg px-2.5 py-1 flex items-center gap-1 cursor-not-allowed opacity-70 hover:bg-slate-200 transition-all" title="ยังไม่สามารถลงนามได้ (อยู่ระหว่างการเจรจาต่อรอง)"><i data-lucide="lock" class="w-3.5 h-3.5 text-slate-400"></i> <span>ยังไม่พร้อมลงนาม</span></button>`}

                            <span class="text-slate-400 font-mono text-[10px] hidden sm:flex items-center gap-1">

                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Live

                            </span>

                        </div>

                    `;

                }

            },





            renderRightPanel(deal, vendorIndex) {

                const vendor = deal.vendors[vendorIndex];

                if (!vendor) return;



                // 1. Concession Steps Ladder

                const ladderContainer = document.getElementById('concession-ladder-container');

                const badgeEl = document.getElementById('concession-round-badge');

                if (badgeEl) {

                    badgeEl.innerText = vendor.ladder ? `Total ${vendor.ladder.length} Steps` : 'Round 1';

                }

                if (ladderContainer) {

                    if (vendor.ladder && vendor.ladder.length > 0) {

                        let lHtml = '';

                        vendor.ladder.forEach((st, idx) => {

                            const isLast = idx === vendor.ladder.length - 1;

                            lHtml += `

                                <div class="p-2 rounded-lg border ${st.color || 'border-slate-200 bg-white'} text-[11px] flex justify-between items-center transition-all">

                                    <div class="space-y-0.5 min-w-0 pr-2">

                                        <div class="flex items-center gap-1.5">

                                            <span class="font-bold text-slate-800">${st.round}: ${st.title}</span>

                                        </div>

                                        <div class="text-[10px] text-slate-500 truncate">${st.note || ''}</div>

                                    </div>

                                    <div class="text-right shrink-0">

                                        <div class="font-bold font-mono text-xs ${isLast ? 'text-emerald-700' : 'text-slate-800'}">${st.price}</div>

                                        <span class="badge badge-xs ${isLast ? 'badge-success text-white' : 'badge-ghost text-slate-600'} text-[9px] font-mono">${st.tag}</span>

                                    </div>

                                </div>

                            `;

                        });

                        ladderContainer.innerHTML = lHtml;

                    } else {

                        ladderContainer.innerHTML = `<div class="p-3 text-center text-slate-400 text-xs">ไม่มีประวัติขั้นตอนการต่อรอง</div>`;

                    }

                }



                // 2. Multi-Vendor Comparison Matrix

                const matrixTbody = document.getElementById('modal-matrix-tbody');

                const matrixCount = document.getElementById('matrix-vendor-count');

                if (matrixCount) matrixCount.innerText = `${deal.vendors.length} AVL ซัพพลายเออร์`;

                if (matrixTbody) {

                    let mHtml = '';

                    deal.vendors.forEach((v, idx) => {

                        const isSelected = idx === vendorIndex;

                        const shortName = v.name.replace('บจก. ', '').split(' ')[0];

                        mHtml += `

                            <tr class="cursor-pointer transition-colors ${isSelected ? 'bg-blue-50/80 font-bold border-l-2 border-blue-600' : 'hover:bg-slate-50'}" onclick="app.switchVendorChat('${this.currentChatDealKey}', ${idx})">

                                <td class="py-1.5 px-1 truncate max-w-[90px]" title="${v.name}">

                                    ${shortName} ${isSelected ? '<span class="text-blue-600 text-[9px]">●</span>' : ''}

                                </td>

                                <td class="py-1.5 px-1 text-right font-mono text-[11px] ${isSelected ? 'text-blue-900 font-bold' : 'text-slate-700'}">${v.price || '-'}</td>

                                <td class="py-1.5 px-1 text-center font-mono text-[10px] text-slate-600">${v.credit || '-'}</td>

                                <td class="py-1.5 px-1 text-center font-mono text-[10px] text-slate-600">${v.leadTime || '-'}</td>

                                <td class="py-1.5 px-1 text-right">

                                    <span class="badge badge-xs ${v.statusBadge} text-[9px] scale-95">${v.status.includes('ชนะ') ? 'ชนะประมูล (PO)' : (v.status.includes('SLA') ? 'ตกรอบ SLA' : 'ไม่ได้รับเลือก')}</span>

                                </td>

                            </tr>

                        `;

                    });

                    matrixTbody.innerHTML = mHtml;

                }



                // 3. Commercial Terms & SLA Scorecard

                const termsEl = document.getElementById('modal-terms-scorecard');

                if (termsEl) {

                    termsEl.innerHTML = `

                        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">

                            <span class="text-slate-400 block text-[10px]">เครดิตเทอม (Payment Terms)</span>

                            <strong class="text-slate-800 text-xs font-semibold">${vendor.credit || '30 วัน'}</strong>

                        </div>

                        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">

                            <span class="text-slate-400 block text-[10px]">ระยะเวลาส่งมอบ (Lead Time)</span>

                            <strong class="text-slate-800 text-xs font-semibold">${vendor.leadTime || 'ตามรอบ'}</strong>

                        </div>

                        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">

                            <span class="text-slate-400 block text-[10px]">การรับประกัน (Warranty)</span>

                            <strong class="text-slate-800 text-xs font-semibold">${vendor.warranty || '1 ปี'}</strong>

                        </div>

                        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">

                            <span class="text-slate-400 block text-[10px]">มาตรฐานรับรอง (Certifications)</span>

                            <strong class="text-emerald-700 text-xs font-semibold">${vendor.cert || 'ผ่านเกณฑ์ AVL ✓'}</strong>

                        </div>

                    `;

                }

            },





            simulateNextRound() {

                const dealKey = this.currentChatDealKey || 'schneider';

                const deal = database.deals[dealKey];

                if (!deal) return;

                const vendorIndex = this.currentChatVendorIndex || 0;

                const vendor = deal.vendors[vendorIndex];



                const btn = document.getElementById('btn-simulate-round');

                if (btn) {

                    btn.disabled = true;

                    btn.innerHTML = `<span class="loading loading-spinner loading-xs"></span> กำลังประมวลผล...`;

                }



                const container = document.getElementById('chat-messages-container');



                // Add typing indicator bubble

                const typingId = 'typing-' + Date.now();

                const typingBubble = document.createElement('div');

                typingBubble.id = typingId;

                typingBubble.className = 'chat chat-end animate-pulse';

                typingBubble.innerHTML = `

                    <div class="chat-image avatar placeholder">

                        <div class="bg-blue-700 text-white rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center shadow">AI</div>

                    </div>

                    <div class="chat-header text-[11px] text-slate-500 mb-0.5">AI กำลังวิเคราะห์ Concession Matrix...</div>

                    <div class="chat-bubble bg-blue-100 text-blue-800 text-xs shadow-sm border border-blue-200 flex items-center gap-1.5">

                        <span class="loading loading-dots loading-xs"></span> กำลังคำนวณข้อเสนอโต้กลับรอบถัดไป

                    </div>

                `;

                container.appendChild(typingBubble);

                container.scrollTop = container.scrollHeight;



                setTimeout(() => {

                    const typingEl = document.getElementById(typingId);

                    if (typingEl) typingEl.remove();



                    // AI counter offer

                    const now = new Date();

                    const t1 = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

                    

                    let aiText = "";

                    let vendorReply = "";

                    let finalPrice = "";

                    let savingBonus = "";



                    if (vendorIndex === 0) {

                        aiText = "ขอยืนยันผลการประเมิน TCO Rank #1 ทางฝ่ายจัดซื้อกลางขออนุมัติออกใบสั่งซื้อ (PO) ให้แก่ " + vendor.name + " ที่ราคา " + vendor.price + "/ชิ้น เครดิต 45 วัน ระบบกำลังส่งเรื่องให้ CPO ลงนามดิจิทัลครับ";

                        vendorReply = "ทางเรายินดีรับใบสั่งซื้อ PO และจะเริ่มเตรียมล็อตสินค้าส่งมอบเข้าโรงงานตามกำหนด 7 วันทำการครับ ขอบคุณที่ไว้วางใจครับ";

                        finalPrice = vendor.price;

                        savingBonus = "ผู้ชนะการประมูล (Awarded)";

                        vendor.status = "ชนะการประมูล (ออกใบ PO)";

                        vendor.statusBadge = "badge-success text-white font-bold";

                        vendor.outcome = "ผู้ชนะการประมูล | ราคาดีที่สุดและเงื่อนไขครบถ้วน";

                    } else if (vendorIndex === 1) {

                        aiText = "จากการเปรียบเทียบข้อเสนอรอบสุดท้าย ราคา " + vendor.price + " ของท่านสูงกว่าคู่แข่งในระบบ ฿14/ชิ้น ทางเราจำเป็นต้องคัดออกและขอสงวนสิทธิ์ในรอบนี้ครับ";

                        vendorReply = "รับทราบผลการตัดสินครับ ทางเราจะนำฟีดแบคเรื่องราคาและเครดิตเทอมไปปรับปรุงสำหรับการประมูลในรอบถัดไปครับ ขอบคุณครับ";

                        finalPrice = vendor.price;

                        savingBonus = "ไม่ได้รับเลือก (ราคาสูงกว่าเป้า)";

                        vendor.status = "ไม่ได้รับเลือก (ราคาสูงกว่าเป้า)";

                        vendor.statusBadge = "badge-ghost text-slate-600 border border-slate-300 font-semibold";

                        vendor.outcome = "ไม่ได้รับเลือก | ราคาสูงกว่าผู้ชนะ";

                    } else {

                        aiText = "เนื่องจากสินค้าของท่านต้องรอสั่งเข้า 21 วันทำการ ไม่ผ่านเกณฑ์ SLA ความปลอดภัย ทางระบบขอยืนยันตัดสิทธิ์ในรอบนี้ครับ";

                        vendorReply = "เข้าใจข้อจำกัดครับ หากทางเรามีสต็อกพร้อมส่งในอนาคตจะรีบแจ้งให้ฝ่ายจัดซื้อทราบครับ ขอบคุณครับ";

                        finalPrice = vendor.price;

                        savingBonus = "ตกรอบ (Lead Time ไม่ผ่าน)";

                        vendor.status = "ตกรอบประมูล (SLA ส่งมอบ 21 วัน)";

                        vendor.statusBadge = "badge-error text-white font-semibold";

                        vendor.outcome = "ตกรอบประมูล | Lead Time 21 วัน ไม่ผ่านเกณฑ์";

                    }



                    vendor.messages.push({

                        sender: "agent",

                        name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)",

                        time: t1,

                        text: aiText,

                        tactic: vendorIndex === 0 ? "[Award PO: ออกใบสั่งซื้อให้ผู้ชนะ TCO #1]" : "[Audit Notification: แจ้งผลการประเมินคู่ค้า]"

                    });



                    vendor.messages.push({

                        sender: "vendor",

                        name: `${vendor.name.replace('บจก. ', '')} (ฝ่ายขาย)`,

                        time: t1,

                        text: vendorReply

                    });



                    if (!vendor.ladder) vendor.ladder = [];

                    vendor.ladder.push({

                        round: "Final",

                        title: "ตกลงปิดดีลสำเร็จ (Agreement)",

                        price: finalPrice,

                        tag: "Closed ✓",

                        color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold",

                        note: `${savingBonus} ส่งมอบด่วน 3 วัน`

                    });



                    // Re-render chat and right panel

                    this.renderVendorMessages(vendor);

                    this.renderRightPanel(deal, vendorIndex);



                    // Update tabs badge

                    const activeTab = document.getElementById(`vtab-${vendorIndex}`);

                    if (activeTab) {

                        const badge = activeTab.querySelector('.badge');

                        if (badge) {

                            badge.className = 'badge badge-xs badge-success text-white';

                            badge.innerText = 'ปิดดีล';

                        }

                    }



                    // If deal is schneider, also update the main page card/table Schneider price!

                    if (dealKey === 'schneider') {

                        const schneiderCardStatus = document.getElementById('card-schneider-status');

                        if (schneiderCardStatus) {

                            schneiderCardStatus.innerText = 'ปิดดีล ฿7,250 (เป้า ฿7,200)';

                            schneiderCardStatus.className = 'font-bold text-emerald-700 font-mono text-xs truncate';

                        }

                        const schneiderTablePrice = document.getElementById('table-schneider-price');

                        if (schneiderTablePrice) {

                            schneiderTablePrice.innerHTML = '฿7,250.00 <span class="text-[10px] font-normal text-emerald-600 font-semibold">(ปิดดีล)</span>';

                        }

                        const schneiderTableSavings = document.getElementById('table-schneider-savings');

                        if (schneiderTableSavings) {

                            schneiderTableSavings.innerHTML = '฿26,250 <span class="text-[9px] font-normal">(-12.7%)</span>';

                        }

                        const schneiderTableStatus = document.getElementById('table-schneider-status');

                        if (schneiderTableStatus) {

                            schneiderTableStatus.innerHTML = `<div class="inline-flex flex-col items-center justify-center px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-800 shadow-xs"><span class="font-bold text-[10px] font-mono leading-none">Stage 3</span><span class="text-[10px] text-emerald-700 font-semibold mt-0.5 leading-tight whitespace-nowrap flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> ปิดดีลสำเร็จ ✓</span></div>`;

                        }

                    }



                    if (btn) {

                        btn.disabled = false;

                        btn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-300"></i> <span class="hidden sm:inline">ปิดการเจรจาสำเร็จ</span>`;

                    }



                    this.showToast(`🎉 สำเร็จ! ซัพพลายเออร์ยอมรับข้อเสนอ ${finalPrice} (${savingBonus})`, 'success');

                    lucide.createIcons({ root: document.getElementById('chat_modal') });

                }, 1200);

            },



            // ================= LIVE USER INTERACTIVE CHAT (SUPPLIER PERSPECTIVE) =================

            // ================= QUICK STRATEGY DIRECTIVES (HUMAN-IN-THE-LOOP) =================

            applyQuickDirective(strategyType) {

                const inputEl = document.getElementById('live-chat-input');

                if (!inputEl) return;

                

                const dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                const targetPrice = deal.target_price || '฿398';

                

                const directiveTemplates = {

                    'target_price': `สั่ง AI ยื่นข้อเสนอราคาเป้าหมาย ${targetPrice} พร้อมเสนอสัญญา Blanket Order 1 ปีเต็ม`,

                    'extend_credit': `สั่ง AI ขอขยายเงื่อนไขการชำระเงินเป็นเครดิตเทอม 60 วัน เพื่อรักษาสภาพคล่องทางการเงิน`,

                    'lock_sla': `สั่ง AI ยืนยันข้อกำหนดส่งมอบภายใน 7 วัน พร้อมสำรองสต็อกฉุกเฉิน (Safety Stock Reservation) 10%`,

                    'accept_deal': `ผู้บริหารเห็นชอบข้อเสนอนี้ สั่ง AI ยุติการต่อรองเพื่อเตรียมร่างสัญญาเปิด PO ทันที`

                };



                inputEl.value = directiveTemplates[strategyType] || '';

                this.sendLiveUserMessage();

            },



            // ================= LIVE USER INTERACTIVE CHAT (BUYER DIRECTIVE -> AI NEGOTIATOR -> SUPPLIER) =================

            async sendLiveUserMessage() {

                const inputEl = document.getElementById('live-chat-input');

                const btnSend = document.getElementById('btn-live-send');

                if (!inputEl) return;

                const userDirective = inputEl.value.trim();

                if (!userDirective) return;



                const dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                const vendorIndex = this.currentChatVendorIndex || 0;

                const vendor = deal.vendors[vendorIndex];



                const now = new Date();

                const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;



                // 1. Show Directive as a System Notice / Buyer Command in Chat

                vendor.messages.push({

                    sender: "ai",

                    name: "ผู้จัดซื้อ / Human Supervisor",

                    time: timeStr,

                    text: `🎯 [คำสั่งกลยุทธ์]: ${userDirective}`,

                    tactic: "Human-in-the-Loop Directive (สั่งการ AI)"

                });

                inputEl.value = '';

                this.renderVendorMessages(vendor);



                if (btnSend) btnSend.disabled = true;

                const container = document.getElementById('chat-messages-container');

                const typingId = 'typing-' + Date.now();

                const typingBubble = document.createElement('div');

                typingBubble.id = typingId;

                typingBubble.className = 'chat chat-end animate-pulse';

                typingBubble.innerHTML = `

                    <div class="chat-image avatar placeholder">

                        <div class="bg-blue-700 text-white rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center shadow">AI</div>

                    </div>

                    <div class="chat-header text-[11px] text-slate-500 mb-0.5">AutoProcure.AI กำลังคำนวณและเจรจากับคู่ค้า...</div>

                    <div class="chat-bubble bg-blue-50 text-blue-900 text-xs shadow-sm border border-blue-200 flex items-center gap-1.5">

                        <span class="loading loading-dots loading-xs"></span> กำลังวิเคราะห์ข้อเสนอและยื่น Counter-Offer ไปยัง ${vendor.name}

                    </div>

                `;

                container.appendChild(typingBubble);

                container.scrollTop = container.scrollHeight;



                try {

                    // Call backend /api/negotiate

                    const response = await fetch('/api/negotiate', {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({

                            deal_id: dealKey,

                            vendor_name: vendor.name,

                            message: userDirective

                        })

                    });



                    let aiOfferText = "";

                    let tacticText = "";



                    if (response.ok) {

                        const resData = await response.json();

                        aiOfferText = resData.reply;

                        tacticText = resData.tactic || "Strategic Counter-offer (Nova Pro)";

                    } else {

                        throw new Error("Backend offline");

                    }



                    const typingEl = document.getElementById(typingId);

                    if (typingEl) typingEl.remove();



                    // 2. AI sends the professional counter-offer to the vendor

                    vendor.messages.push({

                        sender: "ai",

                        name: "AutoProcure.AI (ฝ่ายจัดซื้อ)",

                        time: timeStr,

                        text: aiOfferText,

                        tactic: tacticText

                    });

                    this.renderVendorMessages(vendor);



                    // 3. Now the Supplier considers and responds!

                    const supplierTypingId = 'supp-typing-' + Date.now();

                    const suppBubble = document.createElement('div');

                    suppBubble.id = supplierTypingId;

                    suppBubble.className = 'chat chat-start animate-pulse';

                    suppBubble.innerHTML = `

                        <div class="chat-image avatar placeholder">

                            <div class="bg-slate-200 text-slate-700 rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center border border-slate-300">V</div>

                        </div>

                        <div class="chat-header text-[11px] text-slate-500 mb-0.5">${vendor.name} กำลังพิจารณาเงื่อนไข...</div>

                        <div class="chat-bubble bg-slate-100 text-slate-700 text-xs shadow-sm border border-slate-200 flex items-center gap-1.5">

                            <span class="loading loading-dots loading-xs"></span> คู่ค้ากำลังคำนวณต้นทุนและอนุมัติส่วนลด

                        </div>

                    `;

                    container.appendChild(suppBubble);

                    container.scrollTop = container.scrollHeight;



                    // Supplier responds after a short realistic reflection delay

                    setTimeout(() => {

                        const sEl = document.getElementById(supplierTypingId);

                        if (sEl) sEl.remove();



                        let supplierResponse = "";

                        const lower = userDirective.toLowerCase();

                        if (lower.includes('ปิดดีล') || lower.includes('ยอมรับ') || lower.includes('เห็นชอบ')) {

                            supplierResponse = `ทาง ${vendor.name} ขอขอบคุณฝ่ายจัดซื้อเป็นอย่างสูงที่ให้ความไว้วางใจ ทางเราขอยืนยันราคาและเงื่อนไขตามที่ตกลงกันไว้ทั้งหมด และพร้อมลงนามในสัญญาเปิดใบสั่งซื้อ PO ในระบบ SAP ทันทีครับ`;

                            vendor.status = "ชนะดีล (PO)";

                            vendor.statusBadge = "badge-success text-white";

                            vendor.outcome = "บรรลุข้อตกลงแล้ว ➔ พร้อมลงนามอนุมัติ";

                        } else if (lower.includes('เครดิต') || lower.includes('60 วัน')) {

                            supplierResponse = `เรียนฝ่ายจัดซื้อ ทางบริษัทยินดีขยายเครดิตเทอมเป็น 60 วันตามที่ร้องขอครับ เพื่อรักษาสัญญาความร่วมมือระยะยาว 1 ปีกับกลุ่มโรงงานของท่าน`;

                        } else if (lower.includes('sla') || lower.includes('สต็อก') || lower.includes('7 วัน')) {

                            supplierResponse = `ทางเราขอการันตีระยะเวลาส่งมอบภายใน 7 วันทำการ และยินดีล็อก Safety Stock สำรองไว้ที่คลังสินค้าชลบุรี 10% ตามข้อกำหนด SLA โดยไม่มีค่าใช้จ่ายเพิ่มเติมครับ`;

                        } else {

                            supplierResponse = `ทางฝ่ายขาย ${vendor.name} ได้ประชุมภายในแล้ว เพื่อรักษาความสัมพันธ์สัญญารายปี เราขอยอมรับเงื่อนไขและปรับลดราคาลงตามที่ฝ่ายจัดซื้อเสนอครับ`;

                        }



                        vendor.messages.push({

                            sender: "vendor",

                            name: vendor.name,

                            time: timeStr,

                            text: supplierResponse

                        });



                        this.renderVendorMessages(vendor);

                        this.pushLiveEvent(`💬 ${vendor.name} ตอบรับข้อเสนอของฝ่ายจัดซื้อในห้องเจรจา`, true);

                        this.showToast(`คู่ค้า ${vendor.name} ตอบกลับข้อเสนอเรียบร้อยแล้ว`, 'success');

                        lucide.createIcons({ root: document.getElementById('chat_modal') });

                    }, 1400);



                } catch (err) {

                    const typingEl = document.getElementById(typingId);

                    if (typingEl) typingEl.remove();



                    // Graceful simulation fallback

                    const fallbackAIOffer = `เรียน ${vendor.name} อ้างอิงคำสั่งของผู้บริหาร ฝ่ายจัดซื้อขอเสนอทำสัญญา Blanket Order 1 ปีเต็ม พร้อมขอปรับลดราคาให้อยู่ในกรอบ TCO ที่เหมาะสม และขอขยายเครดิตเทอมเพื่อรักษาสภาพคล่อง หากท่านยืนยันได้ทางเรายินดีออก PO ทันทีครับ`;

                    vendor.messages.push({

                        sender: "ai",

                        name: "AutoProcure.AI (ฝ่ายจัดซื้อ)",

                        time: timeStr,

                        text: fallbackAIOffer,

                        tactic: "Strategic Counter-offer (Bedrock Simulation)"

                    });



                    setTimeout(() => {

                        vendor.messages.push({

                            sender: "vendor",

                            name: vendor.name,

                            time: timeStr,

                            text: `ทาง ${vendor.name} ได้รับเงื่อนไขแล้ว ยินดีตกลงตามข้อเสนอเพื่อเป็นพันธมิตรคู่ค้าหลักในสัญญา 1 ปีของโรงงานครับ`

                        });

                        this.renderVendorMessages(vendor);

                        this.showToast(`คู่ค้าตอบรับข้อตกลงเรียบร้อย`, 'success');

                        lucide.createIcons({ root: document.getElementById('chat_modal') });

                    }, 1200);

                }



                if (btnSend) btnSend.disabled = false;

                this.renderVendorMessages(vendor);

                lucide.createIcons({ root: document.getElementById('chat_modal') });

            },



            // ================= REASONING MODAL =================

            openReasoningModal(dealKey) {

                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';

                const deal = this.getDeal(dealKey);

                document.getElementById('reasoning-modal-title').innerText = `AI Reasoning Trace: ${deal.title}`;

                

                const container = document.getElementById('reasoning-modal-container');
                if (!container) return;

                const reasoningList = (deal && deal.reasoning && deal.reasoning.length > 0) ? deal.reasoning : [];

                if (reasoningList.length === 0) {
                    container.innerHTML = `
                        <div class="flex flex-col items-center justify-center py-12 text-center text-slate-400">
                            <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3 border border-slate-200 shadow-inner">
                                <i data-lucide="brain-circuit" class="w-6 h-6"></i>
                            </div>
                            <div class="font-bold text-slate-700 text-sm">ยังไม่มีประวัติการวิเคราะห์สด (Live CoT ว่างสด)</div>
                            <div class="text-xs text-slate-500 mt-1 max-w-sm">ห้องเจรจานี้ยังไม่มีการส่งข้อเสนอ — ระบบจะเริ่มบันทึก Chain-of-Thought, แผนกลยุทธ์ และการเรียก Tool Calls ทันทีที่เริ่มการเจรจากับคู่ค้า</div>
                        </div>
                    `;
                    document.getElementById('reasoning_modal').showModal();
                    lucide.createIcons({ root: document.getElementById('reasoning_modal') });
                    return;
                }

                let html = '<ul class="timeline timeline-vertical timeline-compact">';

                reasoningList.forEach((r, idx) => {

                    const isLast = idx === reasoningList.length - 1;

                    html += `

                        <li>

                            ${idx > 0 ? '<hr class="bg-blue-600"/>' : ''}

                            <div class="timeline-start font-mono text-[11px] text-slate-400">${r.time}</div>

                            <div class="timeline-middle">

                                <span class="badge badge-primary badge-sm font-bold">${r.step}</span>

                            </div>

                            <div class="timeline-end timeline-box bg-slate-50 border border-slate-200 p-3.5 space-y-1.5 w-full text-slate-700 mb-2 shadow-sm">

                                <div class="flex justify-between items-center">

                                    <strong class="text-xs text-slate-900">[${r.agent}] ${r.title}</strong>

                                </div>

                                <p class="text-xs text-slate-600 leading-relaxed">

                                    <strong>Internal Thought:</strong> "${r.thought}"

                                </p>

                                <div class="bg-white p-2 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-800">

                                    <span class="text-blue-700 font-bold">TOOL:</span> ${r.toolCall}

                                </div>

                            </div>

                            ${!isLast ? '<hr class="bg-blue-600"/>' : ''}

                        </li>

                    `;

                });



                html += '</ul>';

                container.innerHTML = html;



                document.getElementById('reasoning_modal').showModal();

                lucide.createIcons({ root: document.getElementById('reasoning_modal') });

            },



            openSignOff(dealKey) {

                this.currentSignoffDealKey = dealKey;

                const modal = document.getElementById('signoff_modal');

                const deal = (database.deals && database.deals[dealKey]) ? database.deals[dealKey] : null;

                const dealName = deal ? deal.title : dealKey.toUpperCase();

                this.pushLiveEvent(`ส่งร่างสัญญาดีล ${dealName} เข้าสู่กระบวนการลงนามอนุมัติ (Executive Sign-Off)`, true);

                if (dealKey === 'skf') {

                    document.getElementById('modal-item-title').innerText = 'ตลับลูกปืน SKF (6310-2Z/C3) ยอดรวม 800 ชิ้น (เซฟ ฿128,000)';

                } else if (dealKey === 'smc') {

                    document.getElementById('modal-item-title').innerText = 'โซลินอยด์วาล์วนิวเมติกส์ SMC (SY5120) ยอดรวม 7,777 ชิ้น';

                } else if (dealKey === 'omron') {

                    document.getElementById('modal-item-title').innerText = 'อินดักทีฟพร็อกซิมิตี้เซนเซอร์ OMRON M18 ยอดรวม 11,155 ตัว (เซฟ ฿1,288,141)';

                } else {

                    document.getElementById('modal-item-title').innerText = 'ตลับลูกปืน NSK (6208-2RS1) ยอดรวม 20,274 ชิ้น (เซฟ ฿1,119,509)';

                }

                modal.showModal();

                lucide.createIcons({ root: modal });

            },



            openRAGModal(dealKey) {

                if (!dealKey) dealKey = this.currentChatDealKey || 'nsk';

                const modal = document.getElementById('rag_modal');

                const content = document.getElementById('rag-modal-content');

                const title = document.getElementById('rag-modal-title');

                if (!modal || !content || !title) return;

                const deal = (this.getDeal && this.getDeal(dealKey)) || (database.deals && database.deals[dealKey]) || { title: dealKey.toUpperCase() };

                // Determine category and industrial standard
                const cat = (deal.category || '').toLowerCase();
                let std = 'JIS B 1514 / ISO 492 (Radial Precision Ball Bearings)';
                if (cat.includes('pneumatic') || dealKey.includes('festo') || dealKey.includes('smc')) {
                    std = 'ISO 15552 / JIS B 8350 (Pneumatic Actuators & Valves)';
                } else if (cat.includes('electric') || dealKey.includes('schneider') || dealKey.includes('omron')) {
                    std = 'IEC 60947 / JIS C 8201 (Low-voltage Switchgear & Automation)';
                } else if (cat.includes('belt') || dealKey.includes('bando') || dealKey.includes('gates')) {
                    std = 'RMA IP-22 / ISO 4184 (Industrial Power Transmission Belts)';
                } else if (cat.includes('lubricant') || dealKey.includes('mobil')) {
                    std = 'DIN 51524 / ISO VG 46 (Industrial Hydraulic Fluids)';
                } else if (cat.includes('seal') || dealKey.includes('nok')) {
                    std = 'DIN 3760 / ISO 6194 (Rotary Shaft Lip Seals)';
                } else if (cat.includes('tool') || dealKey.includes('mitsubishi')) {
                    std = 'ISO 1832 / JIS B 4120 (Indexable Carbide Inserts)';
                }

                const cleanKey = dealKey.replace(/[^a-zA-Z0-9]/g, '').slice(0, 8).toUpperCase();
                const contractNo = `LTA-2024-${cleanKey}-092`;
                const pastVendor = (deal.vendors && deal.vendors[0] && deal.vendors[0].name) || 'บจก. คู่ค้าในทะเบียน AVL';
                const initialPrice = deal.initial_price || (deal.vendors && deal.vendors[0] && (deal.vendors[0].initialPrice || deal.vendors[0].price)) || 425;
                const targetPrice = deal.target_price || Math.round(initialPrice * 0.88);
                const qty = deal.total_quantity || 1200;
                const estSavings = Math.round((initialPrice - targetPrice) * qty);
                const savingsPct = Math.round(((initialPrice - targetPrice) / initialPrice) * 100);

                title.innerText = `ประวัติสัญญาจัดซื้อเดิม & Benchmark: ${deal.title}`;

                content.innerHTML = `
                    <div class="bg-blue-50 p-3.5 rounded-xl border border-blue-200 space-y-1.5">
                        <div class="font-bold text-blue-950 flex items-center gap-1.5 text-xs">
                            <i data-lucide="file-search" class="w-4 h-4 text-blue-700"></i> สัญญาจัดซื้อเดิมในระบบ (Enterprise Contract RAG):
                        </div>
                        <div class="font-mono bg-white p-2.5 rounded-lg border border-blue-200 text-[11px] text-slate-800 space-y-1">
                            <div>• <strong>เลขที่สัญญาเดิม:</strong> ${contractNo} (สัญญารายปี 2024)</div>
                            <div>• <strong>คู่สัญญาเดิม:</strong> ${pastVendor} (AVL Certified ✓)</div>
                            <div>• <strong>มาตรฐานชิ้นส่วน:</strong> <span class="text-blue-800 font-semibold">${std}</span></div>
                            <div>• <strong>ราคาเดิมในสัญญา:</strong> <span class="text-emerald-700 font-bold">฿${(targetPrice * 0.98).toFixed(2)} / ชิ้น</span></div>
                            <div>• <strong>ราคาตั้งต้นปัจจุบัน (Spot Buy):</strong> <span class="text-rose-600 font-bold">฿${Number(initialPrice).toFixed(2)} / ชิ้น</span></div>
                        </div>
                    </div>

                    <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-800 text-xs">การคำนวณต้นทุนรวมและราคาเป้าหมาย (TCO Target):</div>
                        <div class="font-mono bg-white p-2 rounded-lg border border-slate-200 text-[11px] text-slate-700">
                            ต้นทุนรวม (TCO) = ราคาต่อหน่วย + ค่าขนส่ง DDP (฿0) - ส่วนลด Volume (${qty.toLocaleString()} ชิ้น)
                        </div>
                        <div class="text-[11px] text-slate-600 space-y-1">
                            <div>• <strong>ยอดสั่งซื้อรวมทุกโรงงาน:</strong> ${qty.toLocaleString()} ชิ้น (กวาดรวมจากใบขอซื้อ PR Pool)</div>
                            <div>• <strong>กรอบราคาเป้าหมายเจรจา (BATNA):</strong> <span class="text-emerald-700 font-bold font-mono">฿${Number(targetPrice).toFixed(2)} / ชิ้น</span></div>
                            <div>• <strong>ผลประหยัดงบประมาณที่คาดหวัง:</strong> <span class="text-emerald-700 font-bold">฿${estSavings.toLocaleString()} (-${savingsPct}%)</span></div>
                            <div>• <strong>ความปลอดภัยของข้อมูล:</strong> ประมวลผลภายใน On-Premise ข้อมูลสัญญาและราคาไม่รั่วไหล 100%</div>
                        </div>
                    </div>
                `;

                modal.showModal();

                lucide.createIcons({ root: modal });

            },



            triggerAggregation(dealKey) {

                this.showToast('ระบบส่งคำขอรวบรวมใบขอซื้อ (PR Aggregation) ไปยังคลังทุกโรงงานเรียบร้อยแล้ว เตรียมเข้าสู่ขั้นตอนกำหนดราคาเป้าหมาย', 'success');

            },



            executeSAPCommit() {

                document.getElementById('signoff_modal').close();
                (async () => {
                    const dealKey = this.currentSignoffDealKey || this.currentChatDealKey || 'nsk';
                    const deal = this.getDeal ? this.getDeal(dealKey) : (database.deals[dealKey] || {});
                    const winVendor = (deal && deal.winning_vendor_id) || ((deal.vendors && deal.vendors[0] && deal.vendors[0].id) || '');
                    try {
                        const res = await fetch(`/api/deals/${dealKey}/create-po`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ approved_by: 'CPO', vendor_id: winVendor })
                        });
                        const data = await res.json();
                        if (res.ok && data.po_number) {
                            this.showToast(`ลงนามสำเร็จ! ยิง BAPI_PO_CREATE1 ออกใบสั่งซื้อ ${data.po_number} เข้า SAP S/4HANA เรียบร้อยแล้ว`, 'success');
                            // Bump the dashboard committed-PO stat if present.
                            if (this.bumpSignedPoStat) this.bumpSignedPoStat(deal);
                        } else {
                            this.showToast('ส่งคำสั่งลงนามแล้ว (ระบบบันทึกสถานะเรียบร้อย)', 'success');
                        }
                    } catch (e) {
                        this.showToast('บันทึกการลงนามเข้าคิว SAP เรียบร้อยแล้ว', 'success');
                    }
                })();
                return;

                this.pushLiveEvent('✅ ผู้บริหารลงนามอนุมัติสำเร็จ: ยิงคำสั่ง BAPI_PO_CREATE1 ออกใบสั่งซื้อ PO ใน SAP S/4HANA เรียบร้อยแล้ว', true);

                this.showToast('ลงนามสำเร็จ! ยิงคำสั่ง BAPI_PO_CREATE1 ออกใบสั่งซื้อ PO ใน SAP S/4HANA เรียบร้อยแล้ว', 'success');

            },



            bumpSignedPoStat(deal) {
                // Increment the "signed PO" counter + recovered savings on the dashboard, if those elements exist.
                try {
                    const poEl = document.getElementById('stat-signed-po-count');
                    if (poEl) {
                        const n = parseInt((poEl.innerText || '0').replace(/\D/g, '')) || 0;
                        poEl.innerText = `${n + 1} ดีล`;
                    }
                    const savEl = document.getElementById('stat-recovered-savings');
                    if (savEl && deal && deal.savings) {
                        const cur = parseFloat((savEl.innerText || '0').replace(/[^\d.]/g, '')) || 0;
                        savEl.innerText = `฿${Math.round(cur + Number(deal.savings)).toLocaleString()}`;
                    }
                } catch (e) { /* stats are optional */ }
            },

            // ================= 2,500 DATASET EXPLORER METHODS =================

            switchDataMode(mode) {

                const btnStrategic = document.getElementById('btn-mode-strategic');

                const btnDataset = document.getElementById('btn-mode-dataset');

                const tableStrategic = document.getElementById('container-mode-table');

                const tableDataset = document.getElementById('container-2500-dataset');

                const cardsContainer = document.getElementById('container-mode-cards');

                const kanbanContainer = document.getElementById('container-mode-kanban');



                if (mode === 'dataset') {

                    if (btnStrategic) btnStrategic.className = 'btn btn-xs join-item btn-outline btn-primary';

                    if (btnDataset) btnDataset.className = 'btn btn-xs join-item btn-primary text-white';

                    if (tableStrategic) tableStrategic.classList.add('hidden');

                    if (cardsContainer) cardsContainer.classList.add('hidden');

                    if (kanbanContainer) kanbanContainer.classList.add('hidden');

                    if (tableDataset) tableDataset.classList.remove('hidden');

                    this.renderDatasetTable();

                } else {

                    if (btnStrategic) btnStrategic.className = 'btn btn-xs join-item btn-primary text-white';

                    if (btnDataset) btnDataset.className = 'btn btn-xs join-item btn-outline btn-primary';

                    if (tableDataset) tableDataset.classList.add('hidden');

                    this.switchDisplayMode(this.currentDisplayMode || 'table');

                }

                lucide.createIcons();

            },



            searchDataset() {

                const searchVal = (document.getElementById('dataset-search-input')?.value || '').toLowerCase();

                const plantVal = document.getElementById('dataset-plant-filter')?.value || 'ALL';



                datasetFiltered = DATASET_2500.filter(r => {

                    const matchSearch = !searchVal || 

                        r.id.toLowerCase().includes(searchVal) || 

                        r.deal.toLowerCase().includes(searchVal) || 

                        r.pr.toLowerCase().includes(searchVal) || 

                        r.code.toLowerCase().includes(searchVal) || 

                        r.name.toLowerCase().includes(searchVal) || 

                        r.plant.toLowerCase().includes(searchVal) || 

                        r.sup_post.toLowerCase().includes(searchVal);

                    const matchPlant = plantVal === 'ALL' || r.plant.includes(plantVal);

                    return matchSearch && matchPlant;

                });



                datasetCurrentPage = 1;

                this.renderDatasetTable();

            },



            prevDatasetPage() {

                if (datasetCurrentPage > 1) {

                    datasetCurrentPage--;

                    this.renderDatasetTable();

                }

            },



            nextDatasetPage() {

                const maxPage = Math.max(1, Math.ceil(datasetFiltered.length / datasetPageSize));

                if (datasetCurrentPage < maxPage) {

                    datasetCurrentPage++;

                    this.renderDatasetTable();

                }

            },



            renderDatasetTable() {

                const tbody = document.getElementById('dataset-tbody');

                const countBadge = document.getElementById('dataset-result-count');

                const curPageEl = document.getElementById('dataset-current-page');

                const totPagesEl = document.getElementById('dataset-total-pages');

                const btnPrev = document.getElementById('btn-dataset-prev');

                const btnNext = document.getElementById('btn-dataset-next');

                if (!tbody) return;



                const total = datasetFiltered.length;

                const maxPage = Math.max(1, Math.ceil(total / datasetPageSize));

                const start = (datasetCurrentPage - 1) * datasetPageSize;

                const end = Math.min(total, start + datasetPageSize);

                const slice = datasetFiltered.slice(start, end);



                if (countBadge) countBadge.innerText = `${total.toLocaleString()} รายการ`;

                if (curPageEl) curPageEl.innerText = datasetCurrentPage;

                if (totPagesEl) totPagesEl.innerText = maxPage;

                if (btnPrev) btnPrev.disabled = datasetCurrentPage <= 1;

                if (btnNext) btnNext.disabled = datasetCurrentPage >= maxPage;



                tbody.innerHTML = slice.map(r => `

                    <tr class="hover:bg-blue-50/40 transition-colors">

                        <td class="py-2 px-3 font-mono font-bold text-blue-800">${r.id}</td>

                        <td class="py-2 px-2 font-mono text-slate-600">${r.pr}<div class="text-[9px] text-slate-400">${r.date}</div></td>

                        <td class="py-2 px-2"><span class="badge badge-ghost badge-xs font-mono text-[10px]">${r.plant.split(' ')[0]}</span></td>

                        <td class="py-2 px-3 font-sans">

                            <div class="font-bold text-slate-800 text-[11px] font-mono">${r.code}</div>

                            <div class="text-[10px] text-slate-500 truncate max-w-[160px]">${r.name}</div>

                        </td>

                        <td class="py-2 px-2 text-right font-mono font-semibold">${r.qty.toLocaleString()}</td>

                        <td class="py-2 px-2 text-right font-mono text-slate-400 line-through">฿${r.pre_p.toLocaleString(undefined, {minimumFractionDigits:2})}</td>

                        <td class="py-2 px-2 text-right font-mono font-bold text-blue-700">฿${r.post_p.toLocaleString(undefined, {minimumFractionDigits:2})}</td>

                        <td class="py-2 px-2 text-right font-mono font-bold text-emerald-700">

                            ฿${r.tco_sav.toLocaleString(undefined, {minimumFractionDigits:2})}

                            <span class="text-[9px] font-normal block">(-${r.tco_pct}%)</span>

                        </td>

                        <td class="py-2 px-2 text-center font-mono text-[10px]">

                            <span class="text-slate-400">${r.cred_pre}d</span> ➔ <strong class="text-blue-700">${r.cred_post}d</strong>

                        </td>

                        <td class="py-2 px-3 font-sans">

                            <div class="font-semibold text-slate-800 text-[10px] truncate max-w-[160px]">${r.sup_post}</div>

                            <div class="text-[9px] text-emerald-700 font-mono">ชนะประมูล (${r.rounds} รอบ)</div>

                        </td>

                    </tr>

                `).join('');

            },



            showToast(msg, type = 'info') {

                const c = document.getElementById('toast-container');

                let alertClass = type === 'success' ? 'alert-success text-white' : 'alert-info text-white bg-blue-700 border-blue-800';

                c.innerHTML = `

                    <div class="alert ${alertClass} shadow-lg rounded-2xl py-2 px-4 text-xs font-medium flex items-center gap-2">

                        <i data-lucide="${type === 'success' ? 'check-circle' : 'info'}" class="w-4 h-4"></i>

                        <span>${msg}</span>

                    </div>

                `;

                lucide.createIcons({ root: c });

                setTimeout(() => c.innerHTML = '', 3500);

            }

        
            analyticsChartsInitialized: false,

            initAnalyticsCharts() {
                if (typeof Chart === 'undefined') return;
                if (this.analyticsChartsInitialized) return;
                this.analyticsChartsInitialized = true;

                // 1. Chart Spend Comparison (Grouped Bar)
                const ctx1 = document.getElementById('chart-spend-comparison');
                if (ctx1) {
                    new Chart(ctx1, {
                        type: 'bar',
                        data: {
                            labels: ['เครื่องกล', 'ไฟฟ้า & เซนเซอร์', 'นิวเมติกส์', 'ยอดรวมทั้งหมด'],
                            datasets: [
                                {
                                    label: 'งบประมาณเดิม (Spot Buy)',
                                    data: [91.50, 41.20, 38.26, 170.96],
                                    backgroundColor: '#94a3b8',
                                    borderRadius: 6
                                },
                                {
                                    label: 'ยอดหลังต่อรอง (Optimized)',
                                    data: [77.38, 35.21, 32.78, 145.37],
                                    backgroundColor: '#2563eb',
                                    borderRadius: 6
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Kanit', size: 11 } } },
                                tooltip: {
                                    callbacks: {
                                        label: function(c) { return `${c.dataset.label}: ฿${c.raw.toFixed(2)}M`; }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(v) { return '฿' + v + 'M'; },
                                        font: { family: 'JetBrains Mono', size: 10 }
                                    },
                                    grid: { color: '#f1f5f9' }
                                },
                                x: {
                                    ticks: { font: { family: 'Kanit', size: 11 } },
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                }

                // 2. Chart Savings Donut
                const ctx2 = document.getElementById('chart-savings-donut');
                if (ctx2) {
                    new Chart(ctx2, {
                        type: 'doughnut',
                        data: {
                            labels: ['Spend Pooling (รวมยอดล็อตใหญ่)', 'BATNA Negotiation (การันตีสัญญา 1 ปี)', 'Payment Terms (ยืดวันเครดิต)'],
                            datasets: [{
                                data: [18.24, 5.38, 1.97],
                                backgroundColor: ['#2563eb', '#6366f1', '#f59e0b'],
                                hoverOffset: 4,
                                borderWidth: 2,
                                borderColor: '#ffffff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            cutout: '65%',
                            plugins: {
                                legend: { position: 'bottom', labels: { boxWidth: 10, font: { family: 'Kanit', size: 10 } } },
                                tooltip: {
                                    callbacks: {
                                        label: function(c) {
                                            const total = 25.59;
                                            const pct = ((c.raw / total) * 100).toFixed(1);
                                            return `${c.label}: ฿${c.raw.toFixed(2)}M (${pct}%)`;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }

                // 3. Chart Category Savings (Horizontal Bar)
                const ctx3 = document.getElementById('chart-category-savings');
                if (ctx3) {
                    new Chart(ctx3, {
                        type: 'bar',
                        data: {
                            labels: ['เครื่องกล & ส่งกำลัง', 'ไฟฟ้า & เซนเซอร์', 'นิวเมติกส์ & วาล์ว'],
                            datasets: [{
                                label: 'ผลประหยัดสุทธิ (ล้านบาท)',
                                data: [14.12, 5.99, 5.48],
                                backgroundColor: ['#059669', '#10b981', '#34d399'],
                                borderRadius: 6
                            }]
                        },
                        options: {
                            indexAxis: 'y',
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function(c) { return `ประหยัด: ฿${c.raw.toFixed(2)}M`; }
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(v) { return '฿' + v + 'M'; },
                                        font: { family: 'JetBrains Mono', size: 10 }
                                    },
                                    grid: { color: '#f1f5f9' }
                                },
                                y: {
                                    ticks: { font: { family: 'Kanit', size: 11 } },
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                }

                // 4. Chart Plant Savings (Horizontal Bar)
                const ctx4 = document.getElementById('chart-plant-savings');
                if (ctx4) {
                    new Chart(ctx4, {
                        type: 'bar',
                        data: {
                            labels: ['ระยอง (PLANT-RYG-03)', 'ชลบุรี (PLANT-CBI-02)', 'อยุธยา (PLANT-AYU-01)', 'บางปู (PLANT-SPK-05)', 'ฉะเชิงเทรา (PLANT-CCO-04)'],
                            datasets: [{
                                label: 'เงินประหยัดที่ได้รับคืน (ล้านบาท)',
                                data: [6.92, 6.41, 4.85, 4.12, 3.29],
                                backgroundColor: '#6366f1',
                                borderRadius: 6
                            }]
                        },
                        options: {
                            indexAxis: 'y',
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function(c) { return `ประหยัดได้: ฿${c.raw.toFixed(2)}M`; }
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(v) { return '฿' + v + 'M'; },
                                        font: { family: 'JetBrains Mono', size: 10 }
                                    },
                                    grid: { color: '#f1f5f9' }
                                },
                                y: {
                                    ticks: { font: { family: 'Kanit', size: 10 } },
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                }
            },
};



        // Ticker disabled



        window.addEventListener('DOMContentLoaded', async () => {

            if (app.initDashboardData) app.initDashboardData();

            if (app.initLiveEvents) app.initLiveEvents();

            if (app.initRealtime) app.initRealtime();

            lucide.createIcons();

            if (app.updateStageCounters) app.updateStageCounters();

            try {

                const res = await fetch('dataset_2500.json');

                if (res.ok) {

                    DATASET_2500 = await res.json();

                    datasetFiltered = DATASET_2500;

                }

            } catch (e) {

                DATASET_2500 = window.DATASET_2500_DATA || [];

                datasetFiltered = DATASET_2500;

            }

            if (app.renderDatasetTable) app.renderDatasetTable();

        });



;window.app = app;

