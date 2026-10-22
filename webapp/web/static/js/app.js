// AUTO-EXTRACTED from index.html by Phase-F refactor. Do not add server-rendered values here.
        const app = {
            currentPrList: [],

                        async openEmailModal(dealKey, vendorIndex = 0) {
                if (!dealKey) dealKey = 'nsk';
                this.currentEmailDealKey = dealKey;
                this.currentEmailVendorIndex = vendorIndex;
                const modal = document.getElementById('email_sim_modal');
                if (!modal) return;

                let deal = null;
                if (this.masterDeals && this.masterDeals[dealKey]) {
                    deal = this.masterDeals[dealKey];
                } else {
                    try {
                        const res = await fetch('/api/deals');
                        if (res.ok) {
                            const data = await res.json();
                            this.masterDeals = data.deals || {};
                            deal = this.masterDeals[dealKey];
                        }
                    } catch(e) {}
                }

                if (!deal) {
                    deal = (database.deals && database.deals[dealKey]) ? {
                        sku: dealKey.toUpperCase(),
                        name: database.deals[dealKey].title,
                        qty: 18755,
                        prs_count: 166,
                        supplier: (database.deals[dealKey].vendors && database.deals[dealKey].vendors[0]) ? database.deals[dealKey].vendors[0].name : "บจก. คู่ค้า AVL",
                        post_price: 398,
                        vendors: database.deals[dealKey].vendors
                    } : {
                        sku: dealKey.toUpperCase(),
                        name: `อะไหล่มาตรฐานอุตสาหกรรม ${dealKey.toUpperCase()}`,
                        qty: 5000,
                        prs_count: 50,
                        supplier: "บจก. คู่ค้าที่ได้รับเชิญ",
                        post_price: 500
                    };
                }

                // Identify target vendor
                let vendorsList = (database.deals && database.deals[dealKey] && database.deals[dealKey].vendors) || deal.vendors || [];
                if (vendorsList.length === 0) {
                    vendorsList = [{
                        id: "v1",
                        name: deal.supplier || "บจก. คู่ค้า AVL",
                        price: `฿${deal.post_price || 398}`,
                        credit: "45 วัน",
                        status: "ชนะการประมูล (ออกใบ PO)"
                    }];
                }

                const selectedVendor = vendorsList[vendorIndex] || vendorsList[0];
                const vendorSlug = (selectedVendor.id || 'v1').toLowerCase();
                const token = `tok_sec_${dealKey}_${vendorSlug}_verified`;
                const portalUrl = `${window.location.origin}/portal/negotiate/${dealKey}?vendor=${vendorSlug}&token=${token}`;

                // Populate vendor switcher pills
                const pillsContainer = document.getElementById('email-vendor-pills');
                if (pillsContainer) {
                    pillsContainer.innerHTML = vendorsList.map((v, idx) => {
                        const isAct = idx === vendorIndex;
                        const isWin = v.status && (v.status.includes('ชนะ') || v.status.includes('PO'));
                        const badgeClass = isAct 
                            ? 'bg-blue-600 text-white font-bold border-blue-500' 
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border-slate-700';
                        const labelWin = isWin ? ' [Rank #1 ผู้ชนะ]' : ' [Rank #2 คู่แข่ง]';
                        return `<button type="button" onclick="app.openEmailModal('${dealKey}', ${idx})" class="px-2 py-0.5 rounded-md text-[10px] font-mono border transition-all ${badgeClass}">${v.name.split(' ')[1] || v.name}${labelWin}</button>`;
                    }).join('');
                }

                const vendorClean = selectedVendor.name.replace(/\(V-.*?\)/, '').trim();
                const vendorEmail = `sales-director@${vendorSlug}-supplier.co.th`;

                const elRecipient = document.getElementById('email-recipient-address');
                if (elRecipient) elRecipient.innerText = vendorEmail;

                const elCompany = document.getElementById('email-vendor-company');
                if (elCompany) elCompany.innerText = selectedVendor.name;

                const elSubject = document.getElementById('email-subject-line');
                if (elSubject) elSubject.innerText = `[RFQ-2026-MRO] คำเชิญเข้าร่วมเจรจาข้อตกลงจัดซื้อระยะยาว (LTA) ประจำปี 2026: ${deal.sku || dealKey.toUpperCase()} - บมจ. เอ็นทีที เดต้า อินดัสเทรียล`;

                const elBodyVendor = document.getElementById('email-body-vendor-name');
                if (elBodyVendor) elBodyVendor.innerText = selectedVendor.name;

                const elBodySku = document.getElementById('email-body-sku');
                if (elBodySku) elBodySku.innerText = deal.sku || dealKey.toUpperCase();

                const elBodyQty = document.getElementById('email-body-qty');
                if (elBodyQty) elBodyQty.innerText = `${(deal.qty || 1000).toLocaleString()} ${deal.unit || 'ชิ้น'}`;

                const elBodyPrs = document.getElementById('email-body-prs');
                if (elBodyPrs) elBodyPrs.innerText = `${deal.prs_count || 50} PRs (5 โรงงาน)`;

                const elRfqRef = document.getElementById('email-rfq-ref');
                if (elRfqRef) elRfqRef.innerText = `RFQ-2026-MRO-${(deal.sku || dealKey).toUpperCase().replace(/[^A-Z0-9]/g, '-')}`;

                const elMsgId = document.getElementById('email-ses-message-id');
                const elSesUuid = document.getElementById('email-ses-uuid');
                const randId = `0100018f-${dealKey.toLowerCase()}-${vendorSlug}-${Math.floor(Math.random()*8999+1000)}`;
                if (elMsgId) elMsgId.innerText = randId;
                if (elSesUuid) elSesUuid.innerText = randId;

                const elPortalBtn = document.getElementById('email-portal-link-btn');
                if (elPortalBtn) elPortalBtn.href = `/portal/negotiate/${dealKey}?vendor=${vendorSlug}&token=${token}`;

                const elBottomBtn = document.getElementById('email-portal-bottom-btn');
                if (elBottomBtn) elBottomBtn.href = `/portal/negotiate/${dealKey}?vendor=${vendorSlug}&token=${token}`;

                const elDisplayUrl = document.getElementById('email-display-token-url');
                if (elDisplayUrl) elDisplayUrl.innerText = portalUrl;

                this.currentPortalUrl = portalUrl;

                modal.showModal();
                lucide.createIcons({ root: modal });
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
                const deal = (database.deals && database.deals[dealKey]) || { title: dealKey.toUpperCase() };
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
                if (subEl) subEl.innerText = `รายการใบขอซื้อย่อยระดับโรงงานทั้งหมดที่ถูกมัดรวมเข้าสู่ดีลนี้เพื่อขอ Volume Discount และเจรจาต่อรอง`;

                if (cntEl) cntEl.innerText = `${totalPrs.toLocaleString()} ใบ`;
                if (qtyEl) qtyEl.innerText = `${totalQty.toLocaleString()} ชิ้น`;
                if (preEl) preEl.innerText = `฿${Math.round(preTotal).toLocaleString()}`;
                if (savEl) savEl.innerText = `฿${Math.round(savTotal).toLocaleString()}`;

                this.renderPrTable(this.currentPrList);
            },

            renderPrTable(list) {
                const tbody = document.getElementById('pr-table-body');
                const countEl = document.getElementById('pr-showing-count');
                if (countEl) countEl.innerText = list.length.toLocaleString();
                if (!tbody) return;

                if (list.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">ไม่พบรายการใบขอซื้อที่ตรงกับคำค้นหา</td></tr>`;
                    return;
                }

                tbody.innerHTML = list.slice(0, 100).map(r => `
                    <tr class="hover:bg-blue-50/50 transition-colors">
                        <td class="py-2 px-3 font-bold text-blue-800 font-mono">${r.pr || r.id}</td>
                        <td class="py-2 px-2 text-slate-500 font-mono">${r.date || '-'}</td>
                        <td class="py-2 px-2"><span class="badge badge-ghost badge-xs font-mono text-[10px]">${(r.plant || '').split(' ')[0]}</span></td>
                        <td class="py-2 px-2 text-right font-mono font-semibold">${(r.qty || 0).toLocaleString()}</td>
                        <td class="py-2 px-2 text-right font-mono text-slate-400 line-through">฿${(r.pre_p || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</td>
                        <td class="py-2 px-2 text-right font-mono font-bold text-blue-700">฿${(r.post_p || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</td>
                        <td class="py-2 px-2 text-right font-mono font-bold text-emerald-700">฿${(r.tco_sav || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</td>
                        <td class="py-2 px-3 font-sans text-[11px] text-slate-700 truncate max-w-[150px]">${r.sup_post || '-'}</td>
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

                // If this exact deal + vendor cockpit is open, re-render it live.
                const modal = document.getElementById('chat_modal');
                const isOpen = modal && modal.open;
                if (isOpen && this.currentChatDealKey === dealKey && this.currentChatVendorIndex === vIdx) {
                    this.renderVendorMessages(vendor);
                    lucide.createIcons({ root: modal });
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
                if (sidebar) sidebar.classList.toggle('hidden');
            },

            switchView(viewName) {
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

            async resetCurrentChat() {
                const dealKey = this.currentChatDealKey || 'nsk';
                const deal = database.deals[dealKey] || database.deals.nsk;
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

                const statCount = document.getElementById('stat-count');
                if (statCount) statCount.innerText = `${visibleCount} รายการ`;
            },

            // SIMULATE LIVE AGENT ACTIVITY
            simulateAgentTick() {
                this.tickerIndex = (this.tickerIndex + 1) % this.tickerMessages.length;
                document.getElementById('ticker-msg').innerText = this.tickerMessages[this.tickerIndex];
                this.showToast('จำลอง: Agent ส่งข้อความต่อรองเข้าสู่ห้องเจรจา (WebSocket Stream อัปเดต)', 'info');
            },

            // ================= AUTONOMOUS NEGOTIATION COCKPIT (สลับดูแต่ละเจ้า & จำลองต่อรองสดได้จริง) =================
            currentChatDealKey: null,
            currentChatVendorIndex: 0,

            async openChatModal(dealKey) {
                const deal = database.deals[dealKey] || database.deals.nsk;
                this.currentChatDealKey = dealKey;
                this.currentChatVendorIndex = 0;

                const titleEl = document.getElementById('chat-modal-title');
                if (titleEl) titleEl.innerText = `ห้องควบคุมการเจรจาต่อรองคู่ค้า: ${deal.title}`;

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
                                <span class="badge badge-xs ${v.statusBadge}">${v.status.includes('ชนะ') ? 'ชนะดีล (PO)' : (v.status.includes('SLA') ? 'ตกรอบ SLA' : 'ราคาสูง')}</span>
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
                const deal = database.deals[dealKey] || database.deals.nsk;
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
                    const isWinner = vendor.status && (vendor.status.includes('ชนะ') || vendor.status.includes('PO'));
                    footerEl.innerHTML = `
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="badge badge-sm ${vendor.statusBadge}">${vendor.status}</span>
                            <span class="font-medium text-slate-700 text-xs">${vendor.outcome}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            ${isWinner ? `<button type="button" onclick="app.openSignOff('${this.currentChatDealKey}')" class="btn btn-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg px-3 py-1 shadow-xs flex items-center gap-1"><i data-lucide="file-check-2" class="w-3.5 h-3.5"></i> <span>ได้ข้อสรุปแล้ว ➔ ลงนามสัญญา PO</span></button>` : `<button type="button" onclick="app.showToast('การเจรจากับคู่ค้ารายนี้ยังไม่ได้ข้อสรุป กรุณาดำเนินการต่อรองให้เสร็จสิ้นก่อนลงนามสัญญา', 'info')" class="btn btn-xs bg-slate-100 text-slate-400 border border-slate-200 rounded-lg px-2.5 py-1 flex items-center gap-1 cursor-not-allowed opacity-70 hover:bg-slate-200 transition-all" title="ยังไม่สามารถลงนามได้ (อยู่ระหว่างการเจรจาต่อรอง)"><i data-lucide="lock" class="w-3.5 h-3.5 text-slate-400"></i> <span>ยังไม่พร้อมลงนาม</span></button>`}
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
            async sendLiveUserMessage() {
                const inputEl = document.getElementById('live-chat-input');
                const btnSend = document.getElementById('btn-live-send');
                if (!inputEl) return;
                const text = inputEl.value.trim();
                if (!text) return;

                const dealKey = this.currentChatDealKey || 'nsk';
                const deal = database.deals[dealKey] || database.deals.nsk;
                const vendorIndex = this.currentChatVendorIndex || 0;
                const vendor = deal.vendors[vendorIndex];

                const now = new Date();
                const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

                // 1. Append User (Supplier) Message
                vendor.messages.push({
                    sender: "vendor",
                    name: `${vendor.name.replace('บจก. ', '')} (พิมพ์สด)`,
                    time: timeStr,
                    text: text
                });
                inputEl.value = '';
                this.renderVendorMessages(vendor);

                // Disable button and show typing state
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
                    <div class="chat-header text-[11px] text-slate-500 mb-0.5">AutoProcure.AI กำลังประมวลผลกลยุทธ์...</div>
                    <div class="chat-bubble bg-blue-100 text-blue-800 text-xs shadow-sm border border-blue-200 flex items-center gap-1.5">
                        <span class="loading loading-dots loading-xs"></span> กำลังวิเคราะห์ข้อเสนอและคำนวณ TCO
                    </div>
                `;
                container.appendChild(typingBubble);
                container.scrollTop = container.scrollHeight;

                try {
                    // Try to call Flask Backend /api/negotiate
                    const response = await fetch('/api/negotiate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            deal_key: dealKey,
                            vendor_name: vendor.name,
                            history: vendor.messages.slice(-6),
                            message: text
                        })
                    });

                    let aiReplyText = "";
                    let tacticText = "";

                    if (response.ok) {
                        const resData = await response.json();
                        aiReplyText = resData.reply;
                        tacticText = resData.tactic || `[${resData.source || 'AI Agent'}]`;
                        if (resData.ladder && resData.ladder.length > 0) {
                            vendor.ladder = resData.ladder;
                        }
                        this.showToast(`AI Agent ตอบกลับสำเร็จ (${tacticText})`, 'success');
                    } else {
                        throw new Error("Backend offline");
                    }

                    const typingEl = document.getElementById(typingId);
                    if (typingEl) typingEl.remove();

                    vendor.messages.push({
                        sender: "agent",
                        name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)",
                        time: timeStr,
                        text: aiReplyText,
                        tactic: tacticText
                    });

                } catch (err) {
                    // Fallback to intelligent local procurement logic if opened directly as file://
                    const typingEl = document.getElementById(typingId);
                    if (typingEl) typingEl.remove();

                    let fallbackReply = "";
                    const lowerText = text.toLowerCase();
                    if (lowerText.includes('ลด') || lowerText.includes('บาท') || lowerText.includes('ราคา') || lowerText.includes('%')) {
                        fallbackReply = `ขอบคุณสำหรับข้อเสนอราคาครับ จากการวิเคราะห์ TCO ของกลุ่มโรงงานเรา หากทาง ${vendor.name} สามารถปรับราคาลงมาใกล้เคียงราคาเป้าหมาย ทางเราพร้อมพิจารณาทำสัญญา Blanket Order 1 ปีเต็ม พร้อมขยายเครดิตเทอมเป็น 45 วันครับ [Volume Consolidation & Credit Extension]`;
                    } else if (lowerText.includes('เครดิต') || lowerText.includes('วัน') || lowerText.includes('จ่าย')) {
                        fallbackReply = `เรื่องเครดิตเทอม ทางเราขอยืนยันที่ 45-60 วัน เพื่อรักษาสภาพคล่องทางการเงิน หากท่านรองรับได้ ทางเราจะจัดสรรคำสั่งซื้อล็อตใหญ่ของทั้ง 5 โรงงานให้เป็นลำดับแรกครับ [Working Capital Optimization]`;
                    } else {
                        fallbackReply = `รับทราบข้อเสนอครับ ทางระบบ AutoProcure.AI ได้บันทึกเงื่อนไขเข้าสู่ระบบประเมินคู่ค้า (AVL) เรียบร้อยแล้ว หากท่านมีเงื่อนไขเรื่องการรับประกัน 18 เดือนหรือบริการจัดส่งฟรี DDP ทางเรายินดีนำมาพิจารณาเป็นคะแนนพิเศษครับ [Multi-variable Evaluation]`;
                    }

                    vendor.messages.push({
                        sender: "agent",
                        name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)",
                        time: timeStr,
                        text: fallbackReply,
                        tactic: "[Autonomous Negotiation Engine]"
                    });
                }

                if (btnSend) btnSend.disabled = false;
                this.renderVendorMessages(vendor);
                lucide.createIcons({ root: document.getElementById('chat_modal') });
            },

            // ================= REASONING MODAL =================
            openReasoningModal(dealKey) {
                const deal = database.deals[dealKey] || database.deals.nsk;
                document.getElementById('reasoning-modal-title').innerText = `AI Reasoning Trace: ${deal.title}`;
                
                const container = document.getElementById('reasoning-modal-container');
                let html = '<ul class="timeline timeline-vertical timeline-compact">';

                deal.reasoning.forEach((r, idx) => {
                    const isLast = idx === deal.reasoning.length - 1;
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
                const modal = document.getElementById('signoff_modal');
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

            openRAGModal(dealKey = 'mitsubishi') {
                const modal = document.getElementById('rag_modal');
                const content = document.getElementById('rag-modal-content');
                const title = document.getElementById('rag-modal-title');
                
                if (dealKey === 'mitsubishi') {
                    title.innerText = 'ประวัติสัญญาจัดซื้อเดิม: เม็ดมีดกลึง Mitsubishi';
                    content.innerHTML = `
                        <div class="bg-blue-50 p-3.5 rounded-xl border border-blue-200 space-y-1.5">
                            <div class="font-bold text-blue-950 flex items-center gap-1.5 text-xs">
                                <i data-lucide="file-search" class="w-4 h-4 text-blue-700"></i> สัญญาจัดซื้อเดิมในระบบ (ฐานข้อมูลสัญญาองค์กร):
                            </div>
                            <div class="font-mono bg-white p-2.5 rounded-lg border border-blue-200 text-[11px] text-slate-800 space-y-1">
                                <div>• <strong>เลขที่สัญญาเดิม:</strong> LTA-2024-MITS-092 (สัญญารายปี 2024)</div>
                                <div>• <strong>คู่สัญญาเดิม:</strong> บจก. เคียวเซร่า & มิตซูบิชิ ทูลส์ (AVL Verified)</div>
                                <div>• <strong>ราคาเดิมในสัญญา:</strong> <span class="text-emerald-700 font-bold">฿168.00 / ชิ้น</span> (สั่ง 300 ชิ้น)</div>
                                <div>• <strong>ราคาตั้งต้นปัจจุบัน:</strong> <span class="text-rose-600 font-bold">฿195.00 / ชิ้น</span> (Spot Buy หน้าร้าน)</div>
                            </div>
                        </div>

                        <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
                            <div class="font-bold text-slate-800 text-xs">การคำนวณต้นทุนรวมและราคาเป้าหมาย (TCO Target):</div>
                            <div class="font-mono bg-white p-2 rounded-lg border border-slate-200 text-[11px] text-slate-700">
                                ต้นทุนรวม (TCO) = ราคาต่อหน่วย + ค่าขนส่ง (฿0 ส่งฟรีถึง Tool Crib) - ส่วนลด Volume
                            </div>
                            <div class="text-[11px] text-slate-600 space-y-1">
                                <div>• <strong>ยอดสั่งซื้อรวม:</strong> 500 ชิ้น (กวาดรวมจากตู้เบิก Smart Tool Crib ทุกไลน์)</div>
                                <div>• <strong>กรอบราคาเป้าหมายเจรจา:</strong> <span class="text-emerald-700 font-bold font-mono">฿170.00 / ชิ้น</span></div>
                                <div>• <strong>ผลประหยัดงบประมาณ:</strong> <span class="text-emerald-700 font-bold">฿12,500 (-12.8%)</span> เทียบกับราคา Spot Buy</div>
                                <div>• <strong>ความปลอดภัยของข้อมูล:</strong> ประมวลผลภายในระบบ On-Premise ข้อมูลสัญญาและราคาไม่รั่วไหล 100%</div>
                            </div>
                        </div>
                    `;
                } else {
                    title.innerText = 'ข้อมูลสเปกและราคาอ้างอิง: อะไหล่ MRO';
                    content.innerHTML = `
                        <div class="bg-blue-50 p-3 rounded-xl border border-blue-200 space-y-1 text-xs">
                            <div class="font-bold text-blue-900 flex items-center gap-1.5">
                                <i data-lucide="file-search" class="w-3.5 h-3.5 text-blue-700"></i> สเปกและราคาอ้างอิงเดิม:
                            </div>
                            <div class="font-mono bg-white p-2 rounded border border-blue-200 text-[11px] text-slate-700 space-y-0.5">
                                <div>• <strong>มาตรฐานชิ้นส่วน:</strong> JIS B 1514 / ISO 492 (Radial Bearings)</div>
                                <div>• <strong>ราคาเพดานในอดีต:</strong> ฿450.00 / ชิ้น</div>
                                <div>• <strong>ราคาเป้าหมายเจรจาใหม่:</strong> ฿395.00 - ฿398.00 / ชิ้น</div>
                            </div>
                        </div>
                    `;
                }
                modal.showModal();
                lucide.createIcons({ root: modal });
            },

            triggerAggregation(dealKey) {
                this.showToast('ระบบส่งคำขอรวบรวมใบขอซื้อ (PR Aggregation) ไปยังคลังทุกโรงงานเรียบร้อยแล้ว เตรียมเข้าสู่ขั้นตอนกำหนดราคาเป้าหมาย', 'success');
            },

            executeSAPCommit() {
                document.getElementById('signoff_modal').close();
                this.showToast('ลงนามสำเร็จ! ยิงคำสั่ง BAPI_PO_CREATE1 ออกใบสั่งซื้อ PO ใน SAP S/4HANA เรียบร้อยแล้ว', 'success');
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
        };

        // AUTO ROTATE LIVE TICKER EVERY 6 SECONDS TO FEEL ALIVE
        setInterval(async () => {
            if (app.tickerIndex % 5 === 0 && app.initLiveEvents) {
                await app.initLiveEvents();
            }
            if (app.tickerMessages && app.tickerMessages.length > 0) {
                app.tickerIndex = (app.tickerIndex + 1) % app.tickerMessages.length;
                const el = document.getElementById('ticker-msg');
                if (el) el.innerText = app.tickerMessages[app.tickerIndex];
            }
        }, 4000);

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
