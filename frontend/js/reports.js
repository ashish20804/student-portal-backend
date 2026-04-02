let trendChart, distChart;
let currentReportData = [];
let currentReportType = '';

const STATUS_OPTIONS = {
    'placement': [
        { value: 'all',      label: 'All Students' },
        { value: 'placed',   label: 'Only Placed' },
        { value: 'unplaced', label: 'Only Unplaced' }
    ],
    'higher-studies': [
        { value: 'all',               label: 'All Students' },
        { value: 'higher_studies',    label: 'Going for Higher Studies' },
        { value: 'no_higher_studies', label: 'Not Going for Higher Studies' }
    ],
    'activity': [
        { value: 'all', label: 'All Students' }
    ]
};

// All possible columns per report type
const COLUMNS = {
    'placement': [
        { key: 'roll_no',  label: 'Roll Number' },
        { key: 'name',     label: 'Student Name' },
        { key: 'dept',     label: 'Department' },
        { key: 'company',  label: 'Company' },
        { key: 'package',  label: 'Package' },
        { key: 'year',     label: 'Year' }
    ],
    'higher-studies': [
        { key: 'roll_no',    label: 'Roll Number' },
        { key: 'name',       label: 'Student Name' },
        { key: 'dept',       label: 'Department' },
        { key: 'university', label: 'University' },
        { key: 'course',     label: 'Course' },
        { key: 'year',       label: 'Year' }
    ],
    'activity': [
        { key: 'roll_no',       label: 'Roll Number' },
        { key: 'name',          label: 'Student Name' },
        { key: 'dept',          label: 'Department' },
        { key: 'activity_name', label: 'Activity Name' },
        { key: 'category',      label: 'Category' },
        { key: 'achievement',   label: 'Achievement' }
    ]
};

function getSelectedColumns() {
    return COLUMNS[currentReportType || 'placement'].filter(col => {
        const cb = document.getElementById(`col_${col.key}`);
        return cb ? cb.checked : true;
    });
}

function renderColumnSelector(type) {
    const cols = COLUMNS[type] || [];
    document.getElementById('columnSelector').innerHTML = cols.map(col => `
        <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" id="col_${col.key}" value="${col.key}"
                   checked onchange="rerenderTable()">
            <label class="form-check-label small" for="col_${col.key}">${col.label}</label>
        </div>
    `).join('');
}

function rerenderTable() {
    if (currentReportData.length > 0) renderTable(currentReportType, currentReportData);
}

function updateReportUI() {
    const type = document.getElementById('reportType').value;
    currentReportType = type;

    const titleMap = {
        'placement':      'Placement Report',
        'higher-studies': 'Higher Studies Report',
        'activity':       'Activity Report'
    };
    document.getElementById('reportTitle').innerText = titleMap[type] || 'System Report';

    const statusSelect = document.getElementById('statusFilter');
    const opts = STATUS_OPTIONS[type] || STATUS_OPTIONS['placement'];
    statusSelect.innerHTML = opts.map(o => `<option value="${o.value}">${o.label}</option>`).join('');

    const monthGroup = document.getElementById('monthRangeGroup');
    if (monthGroup) monthGroup.style.display = (type === 'activity') ? 'none' : '';

    renderColumnSelector(type);

    const now = new Date();
    document.getElementById('pdfGeneratedDate').innerText =
        now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

window.onload = function () {
    populateMonthYearDropdowns();
    updateReportUI();
};

function populateMonthYearDropdowns() {
    const months = [
        { v: '',   l: 'Month' },
        { v: '01', l: 'Jan' }, { v: '02', l: 'Feb' }, { v: '03', l: 'Mar' },
        { v: '04', l: 'Apr' }, { v: '05', l: 'May' }, { v: '06', l: 'Jun' },
        { v: '07', l: 'Jul' }, { v: '08', l: 'Aug' }, { v: '09', l: 'Sep' },
        { v: '10', l: 'Oct' }, { v: '11', l: 'Nov' }, { v: '12', l: 'Dec' }
    ];
    const currentYear = new Date().getFullYear();
    const years = [{ v: '', l: 'Year' }];
    for (let y = 2020; y <= currentYear + 1; y++) years.push({ v: String(y), l: String(y) });

    const monthOpts = months.map(m => `<option value="${m.v}">${m.l}</option>`).join('');
    const yearOpts  = years.map(y  => `<option value="${y.v}">${y.l}</option>`).join('');

    ['monthFromMonth', 'monthToMonth'].forEach(id => {
        document.getElementById(id).innerHTML = monthOpts;
    });
    ['monthFromYear', 'monthToYear'].forEach(id => {
        document.getElementById(id).innerHTML = yearOpts;
    });
}

async function fetchReportData() {
    const type      = document.getElementById('reportType').value;
    const rollFrom  = document.getElementById('rollFrom').value.trim();
    const rollTo    = document.getElementById('rollTo').value.trim();
    const monthFrom = (() => {
        const m = document.getElementById('monthFromMonth').value;
        const y = document.getElementById('monthFromYear').value;
        return (m && y) ? `${y}-${m}` : '';
    })();
    const monthTo = (() => {
        const m = document.getElementById('monthToMonth').value;
        const y = document.getElementById('monthToYear').value;
        return (m && y) ? `${y}-${m}` : '';
    })();
    const status = document.getElementById('statusFilter').value;
    const btn    = document.getElementById('generateBtn');
    const token  = localStorage.getItem('access_token');

    const params = new URLSearchParams();
    if (rollFrom)               params.set('roll_from',  rollFrom);
    if (rollTo)                 params.set('roll_to',    rollTo);
    if (monthFrom)              params.set('month_from', monthFrom);
    if (monthTo)                params.set('month_to',   monthTo);
    if (status && status !== 'all') params.set('status', status);

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i>';

    try {
        const statsEndpoint = type === 'placement'      ? 'placement-stats' :
                              type === 'higher-studies' ? 'higher-studies-stats' : 'activity-stats';

        const [listRes, trendRes, statsRes] = await Promise.all([
            fetch(`http://127.0.0.1:5000/admin/reports/${type}?${params.toString()}`,
                { method: 'GET', credentials: 'include', headers }),
            fetch(`http://127.0.0.1:5000/admin/reports/${type}/year-wise`,
                { method: 'GET', credentials: 'include', headers }),
            fetch(`http://127.0.0.1:5000/admin/reports/${statsEndpoint}`,
                { method: 'GET', credentials: 'include', headers })
        ]);

        if ([listRes, trendRes, statsRes].some(r => r.status === 401)) {
            alert('Session expired. Please login again.');
            window.location.href = 'login.html';
            return;
        }

        const listData  = await listRes.json();
        const trendData = await trendRes.json();
        const statsData = await statsRes.json();

        currentReportType = type;
        currentReportData = listData;

        renderTable(type, listData);
        renderCharts(type, trendData, statsData);

    } catch (err) {
        console.error('Report Error:', err);
        alert('Error loading report: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-search"></i>';
    }
}

function renderTable(type, list) {
    const head = document.getElementById('tableHead');
    const body = document.getElementById('reportTableBody');
    const selectedCols = getSelectedColumns();

    head.innerHTML = selectedCols.map(col => `<th>${col.label}</th>`).join('');

    if (!list || list.length === 0) {
        body.innerHTML = `<tr><td colspan="${selectedCols.length}" class="text-center text-muted p-4">No records found for this selection.</td></tr>`;
        return;
    }

    body.innerHTML = list.map(item => {
        const cells = selectedCols.map(col => {
            let val = item[col.key] ?? '-';
            if (col.key === 'package' && val !== '-') val = val + ' LPA';
            if (col.key === 'dept')    return `<td><span class="badge bg-light text-dark border">${val}</span></td>`;
            if (col.key === 'company') return `<td><span class="text-primary fw-bold">${val}</span></td>`;
            if (col.key === 'achievement') return `<td><span class="text-success">${val}</span></td>`;
            return `<td>${val}</td>`;
        }).join('');
        return `<tr>${cells}</tr>`;
    }).join('');
}

function renderCharts(type, trendData, statsData) {
    if (trendChart) trendChart.destroy();
    if (distChart)  distChart.destroy();

    const ctx1 = document.getElementById('trendChart').getContext('2d');
    const ctx2 = document.getElementById('distChart').getContext('2d');

    trendChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: trendData.labels && trendData.labels.length ? trendData.labels : ['No Data'],
            datasets: [{
                label: 'Total Count',
                data: trendData.counts && trendData.counts.length ? trendData.counts : [0],
                backgroundColor: '#2f80ed',
                borderRadius: 5
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: type === 'activity' ? 'Category-wise Distribution' : 'Year-wise Distribution'
                }
            },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });

    const hasDistData = statsData.distLabels && statsData.distLabels.length;
    distChart = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: hasDistData ? statsData.distLabels : ['No Data'],
            datasets: [{
                data: hasDistData ? statsData.distData : [1],
                backgroundColor: ['#9b51e0','#2f80ed','#dc3545','#ffc107','#27ae60','#e74c3c','#3498db']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.3,
            layout: { padding: 15 },
            plugins: {
                legend: { position: 'bottom', labels: { padding: 8, boxWidth: 12, font: { size: 10 } } },
                title: {
                    display: true,
                    text: 'Department-wise Distribution',
                    padding: { top: 5, bottom: 8 },
                    font: { size: 13 }
                }
            }
        }
    });
}

// --- Excel Export ---
function exportToExcel() {
    if (!currentReportData.length) {
        alert('Generate a report first before exporting.');
        return;
    }

    const selectedCols = getSelectedColumns();
    const sheetData = [
        selectedCols.map(c => c.label),  // header row
        ...currentReportData.map(item =>
            selectedCols.map(col => {
                let val = item[col.key] ?? '-';
                if (col.key === 'package' && val !== '-') val = val + ' LPA';
                return val;
            })
        )
    ];

    const ws = XLSX.utils.aoa_to_sheet(sheetData);

    // Auto column widths
    ws['!cols'] = selectedCols.map((col, i) => {
        const maxLen = Math.max(
            col.label.length,
            ...currentReportData.map(item => String(item[col.key] ?? '').length)
        );
        return { wch: Math.min(maxLen + 4, 40) };
    });

    // Style header row bold (basic)
    selectedCols.forEach((_, i) => {
        const cellRef = XLSX.utils.encode_cell({ r: 0, c: i });
        if (ws[cellRef]) ws[cellRef].s = { font: { bold: true } };
    });

    const wb = XLSX.utils.book_new();
    const titleMap = {
        'placement':      'Placement',
        'higher-studies': 'Higher_Studies',
        'activity':       'Activities'
    };
    XLSX.utils.book_append_sheet(wb, ws, titleMap[currentReportType] || 'Report');

    const filename = `${titleMap[currentReportType] || 'Report'}_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, filename);
}

// --- PDF Export ---
async function exportToPDF() {
    const element = document.getElementById('reportContent');
    const pdfBtn  = document.getElementById('pdfBtn');
    const original = pdfBtn.innerHTML;

    pdfBtn.disabled = true;
    pdfBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';

    try {
        await new Promise(resolve => setTimeout(resolve, 500));
        await html2pdf().set({
            margin: 10,
            filename: `Student_Portal_Report_${new Date().toISOString().split('T')[0]}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: {
                scale: 2, useCORS: true, backgroundColor: '#ffffff',
                scrollY: 0, scrollX: 0,
                windowHeight: element.scrollHeight,
                onclone: (doc) => {
                    const el = doc.getElementById('reportContent');
                    if (el) { el.style.width = '100%'; el.style.display = 'block'; }
                }
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        }).from(element).save();
    } catch (err) {
        alert('Error generating PDF: ' + err.message);
    } finally {
        pdfBtn.disabled = false;
        pdfBtn.innerHTML = original;
    }
}
