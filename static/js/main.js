// ── Resume Mode Toggle ───────────────────────────
let resumeMode = 'file'; // 'file' | 'text'
let currentAnalysisId = null; // Stores DB ID for tailoring

function toggleResumeMode() {
    resumeMode = resumeMode === 'file' ? 'text' : 'file';
    const btn = document.getElementById('switchModeBtn');
    const file = document.getElementById('panelFile');
    const text = document.getElementById('panelText');
    if (resumeMode === 'text') {
        file.style.display = 'none';
        text.style.display = 'block';
        btn.textContent = 'Switch to PDF Mode';
    } else {
        file.style.display = 'block';
        text.style.display = 'none';
        btn.textContent = 'Switch to Text Mode';
    }
}

// ── Drag and Drop ─────────────────────────────────
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('resumeFileInput');
const fileNameDisplay = document.getElementById('fileName');

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) {
        fileNameDisplay.textContent = '✓ ' + fileInput.files[0].name;
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.pdf')) {
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        fileNameDisplay.textContent = '✓ ' + file.name;
    } else {
        alert('Please drop a valid .pdf file.');
    }
});

// New Analysis button resets the form
document.getElementById('newAnalysisBtn').addEventListener('click', () => {
    document.getElementById('targetRoleText').value = '';
    document.getElementById('jobDesc').value = '';
    document.getElementById('resumeInput').value = '';
    fileNameDisplay.textContent = '';
    fileInput.value = '';
    document.getElementById('resultsBody').style.display = 'none';
    document.getElementById('resultsPlaceholder').style.display = 'flex';
    document.getElementById('resultsId').textContent = '— AWAITING INPUT // IDLE';
    document.getElementById('btnTailor').style.display = 'none';
    document.getElementById('tailorSection').style.display = 'none';
    currentAnalysisId = null;
    resetScore();
});

// ── Score Ring Animation ─────────────────────────
function setScore(score) {
    const arc = document.getElementById('scoreArc');
    const num = document.getElementById('scoreNumber');
    const verdict = document.getElementById('verdictText');
    const conf = document.getElementById('verdictConf');
    const circumference = 326.73;

    let color, verdictLabel;
    if (score >= 75) {
        color = 'var(--green)';
        verdictLabel = 'High Intent Match';
    } else if (score >= 50) {
        color = 'var(--amber)';
        verdictLabel = 'Moderate Intent Match';
    } else {
        color = 'var(--red)';
        verdictLabel = 'Low Intent Match';
    }

    arc.style.stroke = color;
    arc.style.strokeDashoffset = circumference - (circumference * score / 100);
    num.textContent = score + '%';
    num.style.color = color;
    verdict.textContent = verdictLabel;
    verdict.style.color = color;
    conf.textContent = `CONFIDENCE INTERVAL: ${Math.min(score + 9, 99).toFixed(1)}%`;
}

function resetScore() {
    const arc = document.getElementById('scoreArc');
    arc.style.strokeDashoffset = '326.73';
    document.getElementById('scoreNumber').textContent = '--';
    document.getElementById('scoreNumber').style.color = '';
    document.getElementById('verdictText').textContent = '—';
    document.getElementById('verdictText').style.color = 'var(--text-muted)';
    document.getElementById('verdictConf').textContent = 'CONFIDENCE INTERVAL: —';
}

// ── Insight icon helpers ─────────────────────────
const insightConfig = [
    { type: 'blue',   icon: iconInfo,    prefix: 'Core Strength:' },
    { type: 'amber',  icon: iconWarning, prefix: 'Interview Probe:' },
    { type: 'green',  icon: iconTrend,   prefix: 'Growth Potential:' },
    { type: 'purple', icon: iconCheck,   prefix: 'Strategic Recommendation:' },
];

function iconInfo() {
    return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
}
function iconWarning() {
    return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
}
function iconTrend() {
    return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`;
}
function iconCheck() {
    return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`;
}

// ── Build Skill Tags ─────────────────────────────
function buildTags(container, skills, cssClass) {
    container.innerHTML = '';
    if (!skills || skills.length === 0) {
        container.innerHTML = `<span style="font-size:11px;color:var(--text-muted);font-family:'Roboto Mono',monospace;">None identified</span>`;
        return;
    }
    skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = `tag ${cssClass}`;
        tag.textContent = skill;
        container.appendChild(tag);
    });
}

// ── Analyze Button ────────────────────────────────
document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const jobDesc = document.getElementById('jobDesc').value.trim();
    const targetRole = document.getElementById('targetRoleText').value.trim();

    const btn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');
    const loader = document.getElementById('loader');

    if (!jobDesc) { alert('Please enter a job description.'); return; }
    if (resumeMode === 'text' && !document.getElementById('resumeInput').value.trim()) {
        alert('Please paste your resume text.'); return;
    }
    if (resumeMode === 'file' && !fileInput.files[0]) {
        alert('Please upload a PDF resume.'); return;
    }

    // Loading state
    btn.disabled = true;
    btnText.textContent = 'Analyzing...';
    btnIcon.style.display = 'none';
    loader.style.display = 'inline-block';
    document.getElementById('resultsBody').style.display = 'none';
    document.getElementById('resultsPlaceholder').style.display = 'flex';
    document.getElementById('resultsPlaceholder').innerHTML = `
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.2;animation:spin 1.5s linear infinite;"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <span>Extracting signal... please wait</span>`;
    document.getElementById('resultsId').textContent = 'ID: HS-' + Date.now() + ' // PARSING';
    document.getElementById('btnTailor').style.display = 'none';
    document.getElementById('tailorSection').style.display = 'none';

    try {
        let response;
        if (resumeMode === 'file') {
            const formData = new FormData();
            formData.append('job_desc', jobDesc);
            formData.append('resume_file', fileInput.files[0]);
            formData.append('target_role', targetRole);
            response = await fetch('/analyze', { method: 'POST', body: formData });
        } else {
            const resume = document.getElementById('resumeInput').value.trim();
            response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume, job_desc: jobDesc, target_role: targetRole })
            });
        }

        const data = await response.json();

        if (data.error) {
            document.getElementById('resultsPlaceholder').innerHTML = `
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <span style="color:var(--red);">Error: ${data.error}</span>`;
            document.getElementById('resultsId').textContent = '— ERROR // PARSE_FAILED';
            return;
        }

        // ── Hydrate dashboard ──
        const score = data.score || 0;
        if (data.analysis_id) {
            currentAnalysisId = data.analysis_id;
            document.getElementById('btnTailor').style.display = 'flex';
        }
        
        const analysisId = 'HS-' + new Date().getFullYear() + '-X' + Math.floor(Math.random()*900+100);
        document.getElementById('resultsId').textContent = `ID: ${analysisId} // PARSING_COMPLETE`;

        document.getElementById('resultsPlaceholder').style.display = 'none';
        document.getElementById('resultsBody').style.display = 'flex';

        // Score ring
        setScore(score);

        // Skill count
        const totalSkills = (data.present_skills?.length || 0) + (data.missing_skills?.length || 0);
        document.getElementById('skillCount').textContent = totalSkills + ' nodes parsed';

        // Matched = present skills, Gaps = missing, Partial = suggestions skills if any
        buildTags(document.getElementById('matchedSkillsTags'), data.present_skills, 'matched');
        buildTags(document.getElementById('gapSkillsTags'), data.missing_skills, 'gap');
        // For partial, we'll try to split missing at midpoint if there are many
        const partial = (data.missing_skills || []).slice(0, Math.min(2, Math.floor((data.missing_skills||[]).length/2)));
        buildTags(document.getElementById('partialSkillsTags'), partial.length ? partial : null, 'partial');

        // ATS Checks
        const atsSection = document.getElementById('atsSection');
        const atsDiv = document.getElementById('atsChecks');
        atsDiv.innerHTML = '';
        if (data.ats_issues && data.ats_issues.length > 0) {
            atsSection.style.display = 'block';
            data.ats_issues.forEach(issue => {
                const row = document.createElement('div');
                row.className = 'ats-row';
                const iconHtml = issue.passed
                    ? `<svg class="ats-icon-pass" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`
                    : `<svg class="ats-icon-fail" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
                row.innerHTML = `${iconHtml}<span><strong>${issue.name}:</strong> <span style="color:var(--text-muted)">${issue.message}</span></span>`;
                atsDiv.appendChild(row);
            });
        } else {
            atsSection.style.display = 'none';
        }

        // Insight Cards
        const insightsGrid = document.getElementById('insightsGrid');
        insightsGrid.innerHTML = '';
        const allInsights = [...(data.strengths || []), ...(data.suggestions || [])];
        const colors = ['blue','amber','green','purple'];
        const icons  = [iconInfo, iconWarning, iconTrend, iconCheck];
        const prefixes = ['Core Strength:', 'Interview Probe:', 'Growth Potential:', 'Strategic Recommendation:'];

        allInsights.slice(0, 4).forEach((text, i) => {
            const card = document.createElement('div');
            card.className = `insight-card ${colors[i % colors.length]}`;
            card.innerHTML = `
                <div class="insight-card-header">
                    <div class="insight-icon">${icons[i % icons.length]()}</div>
                    <div class="insight-card-title">${prefixes[i % prefixes.length]}</div>
                </div>
                <div class="insight-card-body">${text}</div>`;
            insightsGrid.appendChild(card);
        });

        if (allInsights.length === 0) {
            insightsGrid.innerHTML = `<span style="color:var(--text-muted);font-size:12px;font-family:'Roboto Mono',monospace;">No insights returned.</span>`;
        }

    } catch (err) {
        document.getElementById('resultsPlaceholder').innerHTML =
            `<span style="color:var(--red);">Network Error: ${err.message}</span>`;
        document.getElementById('resultsId').textContent = '— NETWORK_ERROR // FAILED';
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Analyze Candidate';
        btnIcon.style.display = '';
        loader.style.display = 'none';
    }
});

// ── Auto-Tailor ────────────────────────────────
document.getElementById('btnTailor').addEventListener('click', async () => {
    if (!currentAnalysisId) return;
    const tailorBtn = document.getElementById('btnTailor');
    const tailorSection = document.getElementById('tailorSection');
    const consText = document.getElementById('conservativeText');
    const aggText = document.getElementById('aggressiveText');

    tailorBtn.disabled = true;
    tailorBtn.innerHTML = '<div class="loader" style="width:12px;height:12px;border-width:2px;display:inline-block;border-color:var(--purple);border-bottom-color:transparent;margin-right:6px;"></div> Tailoring...';
    tailorSection.style.display = 'block';
    
    setTimeout(() => tailorSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);

    consText.innerHTML = '<span style="color:var(--text-muted);"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity:0.5;animation:spin 1s linear infinite;"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg> Generating conservative version...</span>';
    aggText.innerHTML = '<span style="color:var(--text-muted);"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity:0.5;animation:spin 1s linear infinite;"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg> Generating aggressive version...</span>';

    try {
        const response = await fetch('/api/tailor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ analysis_id: currentAnalysisId })
        });

        // Always parse JSON — even on 401/404/500 our API returns JSON
        let options;
        try {
            options = await response.json();
        } catch (_) {
            throw new Error(`Server returned status ${response.status}. Is the server running?`);
        }

        if (!response.ok || options.error) {
            const msg = options.error || `Server error (${response.status})`;
            consText.innerHTML = `<span style="color:var(--red);">${msg}</span>`;
            aggText.innerHTML = `<span style="color:var(--red);">${msg}</span>`;
        } else {
            consText.textContent = options.conservative;
            aggText.textContent = options.aggressive;
        }
    } catch (e) {
        consText.innerHTML = `<span style="color:var(--red);">${e.message}</span>`;
        aggText.innerHTML = `<span style="color:var(--red);">${e.message}</span>`;
    } finally {
        tailorBtn.disabled = false;
        tailorBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Auto-Tailor`;
    }
});

function copyTailored(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector(`button[onclick="copyTailored('${elementId}')"]`);
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.style.color = 'var(--purple)';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.color = '';
        }, 2000);
    });
}
