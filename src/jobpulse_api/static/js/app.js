// ===== JobPulse UI (hardened) =====
let currentPage = 1;
const jobsPerPage = 20;
let allJobs = [];
let filteredJobs = [];
const $ = (id) => document.getElementById(id);
const searchInput = $('searchInput');
const searchBtn = $('searchBtn');
const companyFilter = $('companyFilter');
const locationFilter = $('locationFilter');
const resetBtn = $('resetBtn');
const jobsContainer = $('jobsContainer');
const totalJobsEl = $('totalJobs');
const totalCompaniesEl = $('totalCompanies');
const paginationEl = $('pagination');
// Error banner
function showError(msg) {
  jobsContainer.innerHTML = `
    <div class="no-results">
      <h3>⚠️ שגיאה בטעינת נתונים</h3>
      <p style="direction:ltr;text-align:left">${msg}</p>
    </div>
  `;
  console.error("[UI]", msg);
}
function getApiBase() {
  // same-origin
  return `${location.origin}`;
}
async function apiGet(path) {
  const url = `${getApiBase()}${path}`;
  const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' }});
  if (!res.ok) {
    const text = await res.text().catch(()=>'');
    throw new Error(`HTTP ${res.status} on ${path} — ${text.slice(0,500)}`);
  }
  // try parse json
  return await res.json();
}
async function init() {
  try {
    // fetch large page (server patched to le=10000)
    const data = await apiGet('/jobs/?limit=10000');
    if (!Array.isArray(data)) throw new Error("Response is not an array");
    allJobs = data.filter(j => j && j.title && j.company); // minimal sanity
    filteredJobs = [...allJobs];
    updateStats();
    populateFilters();
    renderJobs();
  } catch (err) {
    showError(String(err));
  } finally {
    setupEventListeners();
  }
}
function updateStats() {
  try {
    totalJobsEl.textContent = filteredJobs.length.toLocaleString('he-IL');
    const companies = new Set(filteredJobs.map(j => j.company).filter(Boolean));
    totalCompaniesEl.textContent = companies.size.toLocaleString('he-IL');
  } catch (e) {
    showError("updateStats failed: " + e);
  }
}
function populateFilters() {
  try {
    const companies = [...new Set(allJobs.map(j => j.company).filter(Boolean))].sort();
    const locations = [...new Set(allJobs.map(j => j.location).filter(Boolean))].sort();
    companyFilter.innerHTML = '<option value="">כל החברות</option>' +
      companies.map(c => `<option value="${c}">${c}</option>`).join('');
    locationFilter.innerHTML = '<option value="">כל המיקומים</option>' +
      locations.map(l => `<option value="${l}">${l}</option>`).join('');
  } catch (e) {
    showError("populateFilters failed: " + e);
  }
}
function filterJobs() {
  try {
    const searchTerm = (searchInput.value || '').toLowerCase();
    const company = companyFilter.value || '';
    const location = locationFilter.value || '';
    filteredJobs = allJobs.filter(job => {
      const t = (job.title || '').toLowerCase();
      const c = (job.company || '').toLowerCase();
      const l = (job.location || '').toLowerCase();
      const matchSearch = !searchTerm || t.includes(searchTerm) || c.includes(searchTerm) || l.includes(searchTerm);
      const matchCompany = !company || job.company === company;
      const matchLocation = !location || job.location === location;
      return matchSearch && matchCompany && matchLocation;
    });
    currentPage = 1;
    updateStats();
    renderJobs();
  } catch (e) {
    showError("filterJobs failed: " + e);
  }
}
function renderJobs() {
  try {
    if (!filteredJobs.length) {
      jobsContainer.innerHTML = `
        <div class="no-results">
          <h3>😔 לא נמצאו משרות</h3>
          <p>נסה לשנות את פרמטרי החיפוש</p>
        </div>`;
      paginationEl.innerHTML = '';
      return;
    }
    const startIdx = (currentPage - 1) * jobsPerPage;
    const endIdx = startIdx + jobsPerPage;
    const pageJobs = filteredJobs.slice(startIdx, endIdx);
    jobsContainer.innerHTML = pageJobs.map(job => {
      const url = job.url || '#';
      const safeTitle = job.title ?? '(ללא כותרת)';
      const safeCompany = job.company ?? '';
      const safeLoc = job.location ?? '';
      const safeSource = job.source ?? '';
      return `
        <div class="job-card" ${url !== '#' ? `onclick="window.open('${url}','_blank')"` : ''}>
          <div class="job-header">
            <div>
              <h2 class="job-title">${safeTitle}</h2>
              <div class="job-company">${safeCompany}</div>
            </div>
          </div>
          <div class="job-meta">
            ${safeLoc ? `<div class="job-meta-item">📍 ${safeLoc}</div>` : ''}
            ${safeSource ? `<div class="job-meta-item">🔗 ${safeSource}</div>` : ''}
          </div>
          ${url !== '#' ? `<a href="${url}" target="_blank" class="job-link" onclick="event.stopPropagation()">צפה במשרה ←</a>` : ''}
        </div>`;
    }).join('');
    renderPagination();
  } catch (e) {
    showError("renderJobs failed: " + e);
  }
}
function renderPagination() {
  try {
    const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);
    if (totalPages <= 1) { paginationEl.innerHTML = ''; return; }
    let html = `
      <button class="page-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>← הקודם</button>
    `;
    const maxButtons = 5;
    const start = 1;
    const end = Math.min(totalPages, maxButtons);
    for (let i = start; i <= end; i++) {
      html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }
    if (totalPages > maxButtons) {
      html += `<span style="color: white; padding: 0 10px;">...</span>`;
      html += `<button class="page-btn" onclick="changePage(${totalPages})">${totalPages}</button>`;
    }
    html += `<button class="page-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>הבא →</button>`;
    paginationEl.innerHTML = html;
  } catch (e) {
    showError("renderPagination failed: " + e);
  }
}
window.changePage = function(page) {
  const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  renderJobs();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function resetFilters() {
  searchInput.value = '';
  companyFilter.value = '';
  locationFilter.value = '';
  filterJobs();
}
function setupEventListeners() {
  searchBtn?.addEventListener('click', filterJobs);
  searchInput?.addEventListener('keyup', (e) => { if (e.key === 'Enter') filterJobs(); });
  companyFilter?.addEventListener('change', filterJobs);
  locationFilter?.addEventListener('change', filterJobs);
  resetBtn?.addEventListener('click', resetFilters);
}
document.addEventListener('DOMContentLoaded', init);
