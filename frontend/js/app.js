/**
 * Recruitment Management System (RMS) - Frontend Application
 */

const API_BASE = window.location.port === "3000" && window.location.pathname.startsWith("/api")
  ? "/api/v1"
  : "http://localhost:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  checkApiHealth();
  loadDashboardData();
  loadRequisitions();
  loadApplications();
  loadInterviews();
  loadFeedback();
  loadOffers();
  loadExceptions();
  initModals();
});

// ----------------------------------------------------
// Tab Switching
// ----------------------------------------------------
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const target = document.getElementById(tab.dataset.tab);
      if (target) target.classList.add("active");
    });
  });
}

// ----------------------------------------------------
// Health Check
// ----------------------------------------------------
async function checkApiHealth() {
  try {
    const res = await fetch("http://localhost:8000/health/database");
    const indicator = document.getElementById("api-status");
    const text = document.getElementById("api-status-text");
    if (res.ok) {
      indicator.className = "status-indicator status-online";
      text.textContent = "Backend & DB Connected";
    } else {
      indicator.className = "status-indicator";
      indicator.style.background = "#fee2e2";
      indicator.style.color = "#991b1b";
      text.textContent = "DB Disconnected";
    }
  } catch (err) {
    const text = document.getElementById("api-status-text");
    text.textContent = "Backend Offline";
  }
}

// ----------------------------------------------------
// Dashboard & Analytics
// ----------------------------------------------------
async function loadDashboardData() {
  try {
    const [kpiRes, funnelRes, deptRes] = await Promise.all([
      fetch(`${API_BASE}/analytics/kpis`),
      fetch(`${API_BASE}/analytics/funnel`),
      fetch(`${API_BASE}/analytics/departments`)
    ]);

    if (kpiRes.ok) {
      const kpis = await kpiRes.json();
      document.getElementById("kpi-reqs").textContent = kpis.total_requisitions;
      document.getElementById("kpi-reqs-sub").textContent = `${kpis.open_requisitions} Open Roles (${kpis.closed_requisitions} Closed)`;
      document.getElementById("kpi-apps").textContent = kpis.total_applications.toLocaleString();
      document.getElementById("kpi-ints").textContent = kpis.total_interviews.toLocaleString();
      document.getElementById("kpi-offers").textContent = `${kpis.offer_acceptance_rate_percent}%`;
      document.getElementById("kpi-offers-sub").textContent = `Avg Time-to-Hire: ${kpis.avg_time_to_hire_days} days`;
    }

    if (funnelRes.ok) {
      const funnel = await funnelRes.json();
      const container = document.getElementById("funnel-container");
      container.innerHTML = "";

      funnel.funnel.forEach(item => {
        const row = document.createElement("div");
        row.className = "funnel-row";
        row.innerHTML = `
          <div class="funnel-label">${item.stage}</div>
          <div class="funnel-bar-track">
            <div class="funnel-bar-fill" style="width: ${Math.max(item.conversion_rate_percent, 2)}%;"></div>
          </div>
          <div class="funnel-meta">${item.count.toLocaleString()} (${item.conversion_rate_percent}%)</div>
        `;
        container.appendChild(row);
      });
    }

    if (deptRes.ok) {
      const depts = await deptRes.json();
      const tbody = document.getElementById("dept-table-body");
      tbody.innerHTML = "";

      depts.forEach(d => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${d.department_name}</strong></td>
          <td>${d.total_requisitions}</td>
          <td><span class="badge badge-open">${d.open_requisitions} Open</span></td>
          <td>${d.total_applications}</td>
          <td>${d.total_offers}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

// ----------------------------------------------------
// Requisitions
// ----------------------------------------------------
async function loadRequisitions() {
  try {
    const res = await fetch(`${API_BASE}/requisitions/?limit=100`);
    if (!res.ok) return;
    const reqs = await res.json();
    const tbody = document.getElementById("requisitions-table-body");
    tbody.innerHTML = "";

    reqs.forEach(r => {
      const tr = document.createElement("tr");
      const badgeClass = r.status === "OPEN" ? "badge-open" : r.status === "CLOSED" ? "badge-closed" : "badge-draft";
      tr.innerHTML = `
        <td><code>${r.job_code}</code></td>
        <td><strong>${r.job_title}</strong></td>
        <td>Dept #${r.department_id}</td>
        <td>${r.openings}</td>
        <td>₹${(r.min_salary / 100000).toFixed(1)}L - ₹${(r.max_salary / 100000).toFixed(1)}L</td>
        <td>${r.experience_required} yrs</td>
        <td><span class="badge ${badgeClass}">${r.status}</span></td>
        <td>${new Date(r.created_at).toLocaleDateString()}</td>
        <td>
          ${r.status === "OPEN" ? `<button class="btn btn-secondary btn-sm" onclick="closeRequisition(${r.requisition_id})">Close</button>` : "-"}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading requisitions:", err);
  }
}

window.closeRequisition = async function(reqId) {
  if (!confirm(`Are you sure you want to close requisition #${reqId}?`)) return;
  try {
    const res = await fetch(`${API_BASE}/requisitions/${reqId}/close`, { method: "POST" });
    if (res.ok) {
      alert("Requisition closed successfully.");
      loadRequisitions();
      loadDashboardData();
    } else {
      const err = await res.json();
      alert(`Error closing requisition: ${err.detail || "Failed"}`);
    }
  } catch (e) {
    alert("Request failed.");
  }
};

// ----------------------------------------------------
// Applications
// ----------------------------------------------------
async function loadApplications() {
  const statusFilter = document.getElementById("filter-app-status").value;
  let url = `${API_BASE}/applications/?limit=50`;
  if (statusFilter) url += `&status=${statusFilter}`;

  try {
    const res = await fetch(url);
    if (!res.ok) return;
    const apps = await res.json();
    const tbody = document.getElementById("applications-table-body");
    tbody.innerHTML = "";

    apps.forEach(a => {
      const tr = document.createElement("tr");
      const badgeClass = `badge-${a.status.toLowerCase()}`;
      tr.innerHTML = `
        <td><code>${a.application_code}</code></td>
        <td>Candidate #${a.candidate_id}</td>
        <td>Req #${a.requisition_id}</td>
        <td>${new Date(a.applied_at).toLocaleDateString()}</td>
        <td><strong>${a.screening_score !== null ? a.screening_score + " / 100" : "Pending"}</strong></td>
        <td><span class="badge ${badgeClass}">${a.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="quickScreen(${a.application_id})">Score</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading applications:", err);
  }
}

document.getElementById("filter-app-status").addEventListener("change", loadApplications);

window.quickScreen = function(appId) {
  document.querySelector('.tab-btn[data-tab="tab-screening"]').click();
  document.getElementById("screen-app-id").value = appId;
  document.getElementById("btn-run-screen").click();
};

// ----------------------------------------------------
// Screening Engine
// ----------------------------------------------------
document.getElementById("btn-run-screen").addEventListener("click", async () => {
  const appId = document.getElementById("screen-app-id").value;
  if (!appId) {
    alert("Please enter an Application ID");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/screening/evaluate/${appId}`, { method: "POST" });
    if (!res.ok) {
      const err = await res.json();
      alert(`Screening evaluation error: ${err.detail || "Failed"}`);
      return;
    }

    const data = await res.json();
    const box = document.getElementById("screening-result-box");
    box.style.display = "block";

    const alertBox = document.getElementById("screening-summary-alert");
    alertBox.className = data.is_qualified ? "alert alert-success" : "alert alert-danger";
    alertBox.innerHTML = `
      <strong>Screening Result:</strong> Application #${data.application_id} scored 
      <strong>${data.total_score} / 100</strong>. 
      Recommended Stage: <span class="badge ${data.is_qualified ? 'badge-shortlisted' : 'badge-rejected'}">${data.recommended_stage}</span> 
      (${data.is_qualified ? 'Qualified for interview rounds' : 'Disqualified under minimum policy threshold'}).
    `;

    const tbody = document.getElementById("screening-breakdown-body");
    tbody.innerHTML = "";

    data.rule_breakdown.forEach(rb => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${rb.criteria_name}</strong></td>
        <td>${rb.weight}%</td>
        <td>${rb.raw_score} / 100</td>
        <td>+${rb.weighted_score} pts</td>
        <td><span class="badge ${rb.passed ? 'badge-open' : 'badge-rejected'}">${rb.passed ? 'PASS' : 'FAIL'}</span></td>
        <td><small>${rb.comments}</small></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    alert("Evaluation failed to connect to API.");
  }
});

// ----------------------------------------------------
// Interviews
// ----------------------------------------------------
async function loadInterviews() {
  try {
    const res = await fetch(`${API_BASE}/interviews/?limit=50`);
    if (!res.ok) return;
    const intvs = await res.json();
    const tbody = document.getElementById("interviews-table-body");
    tbody.innerHTML = "";

    intvs.forEach(i => {
      const tr = document.createElement("tr");
      const panelNames = i.assignments.map(a => a.interviewer_name || `IVR #${a.interviewer_id}`).join(", ") || "No panel assigned";
      tr.innerHTML = `
        <td><code>${i.interview_code}</code></td>
        <td>App #${i.application_id}</td>
        <td><strong>${i.round_name}</strong></td>
        <td><small>${new Date(i.scheduled_start).toLocaleString()} - ${new Date(i.scheduled_end).toLocaleTimeString()}</small></td>
        <td><span class="badge badge-interview">${i.status}</span></td>
        <td>${panelNames}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="promptAssignPanel(${i.interview_id})">+ Panel</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading interviews:", err);
  }
}

window.promptAssignPanel = async function(intvId) {
  const ivrId = prompt(`Enter Interviewer ID to assign to Interview #${intvId}:\n(Schedule conflict checking is enforced automatically)`);
  if (!ivrId) return;

  try {
    const res = await fetch(`${API_BASE}/interviews/${intvId}/assign`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interviewer_id: parseInt(ivrId) })
    });

    if (res.ok) {
      alert("Panel member assigned successfully.");
      loadInterviews();
    } else {
      const err = await res.json();
      alert(`Cannot assign interviewer:\n${err.detail}`);
    }
  } catch (e) {
    alert("Assignment request failed.");
  }
};

// ----------------------------------------------------
// Feedback
// ----------------------------------------------------
async function loadFeedback() {
  try {
    const res = await fetch(`${API_BASE}/feedback/?limit=50`);
    if (!res.ok) return;
    const fbs = await res.json();
    const tbody = document.getElementById("feedback-table-body");
    tbody.innerHTML = "";

    fbs.forEach(fb => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${fb.feedback_code}</code></td>
        <td>Int #${fb.interview_id}</td>
        <td>Ivr #${fb.interviewer_id}</td>
        <td>${fb.technical_score} / 10</td>
        <td>${fb.problem_solving_score} / 10</td>
        <td>${fb.communication_score} / 10</td>
        <td><strong>${fb.overall_score}</strong></td>
        <td><span class="badge ${fb.recommendation.includes('HIRE') ? 'badge-offer' : 'badge-rejected'}">${fb.recommendation}</span></td>
        <td>${new Date(fb.submitted_at).toLocaleDateString()}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading feedback:", err);
  }
}

// ----------------------------------------------------
// Offers
// ----------------------------------------------------
async function loadOffers() {
  try {
    const res = await fetch(`${API_BASE}/offers/?limit=50`);
    if (!res.ok) return;
    const offers = await res.json();
    const tbody = document.getElementById("offers-table-body");
    tbody.innerHTML = "";

    offers.forEach(o => {
      const tr = document.createElement("tr");
      const badgeClass = o.status === "APPROVED" ? "badge-open" : o.status === "ACCEPTED" ? "badge-offer" : o.status === "PENDING_APPROVAL" ? "badge-screening" : "badge-rejected";
      const approvalCount = o.approvals ? o.approvals.length : 0;

      tr.innerHTML = `
        <td><code>${o.offer_code}</code></td>
        <td>App #${o.application_id}</td>
        <td><strong>₹${(o.offered_salary).toLocaleString()}</strong></td>
        <td>${o.joining_date ? new Date(o.joining_date).toLocaleDateString() : "-"}</td>
        <td><span class="badge ${badgeClass}">${o.status}</span></td>
        <td>${approvalCount} decision event(s)</td>
        <td>
          ${o.status === "PENDING_APPROVAL" ? `
            <button class="btn btn-success btn-sm" onclick="approveOffer(${o.offer_id})">Approve</button>
            <button class="btn btn-danger btn-sm" onclick="rejectOffer(${o.offer_id})">Reject</button>
          ` : "-"}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading offers:", err);
  }
}

window.approveOffer = async function(offerId) {
  try {
    const res = await fetch(`${API_BASE}/offers/${offerId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision: "APPROVED", approver_id: 1, comments: "Approved via Web UI Console" })
    });
    if (res.ok) {
      alert("Offer approved and candidate advanced to OFFER stage.");
      loadOffers();
      loadDashboardData();
    } else {
      const err = await res.json();
      alert(`Approval error: ${err.detail}`);
    }
  } catch (e) {
    alert("Approval request failed.");
  }
};

window.rejectOffer = async function(offerId) {
  try {
    const res = await fetch(`${API_BASE}/offers/${offerId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision: "REJECTED", approver_id: 1, comments: "Rejected via Web UI Console" })
    });
    if (res.ok) {
      alert("Offer rejected.");
      loadOffers();
    }
  } catch (e) {
    alert("Rejection request failed.");
  }
};

// ----------------------------------------------------
// Exceptions & Audit
// ----------------------------------------------------
async function loadExceptions() {
  try {
    const res = await fetch(`${API_BASE}/exceptions/detect`);
    if (!res.ok) return;
    const report = await res.json();

    const summaryAlert = document.getElementById("audit-summary-alert");
    summaryAlert.innerHTML = `
      <strong>Automated Audit Complete:</strong> Detected <strong>${report.total_anomalies_detected}</strong> policy exception event(s) across the database.
      Reconciled against <strong>${report.ground_truth_matches}</strong> known ground-truth edge case categories.
    `;

    const list = document.getElementById("anomalies-list");
    list.innerHTML = "";

    report.anomalies.slice(0, 30).forEach(an => {
      const div = document.createElement("div");
      div.className = "anomaly-card";
      div.innerHTML = `
        <div class="anomaly-head">
          <div class="anomaly-title"><span class="badge badge-rejected">${an.scenario_id}</span> ${an.scenario_name}</div>
          <span class="badge ${an.severity === 'CRITICAL' ? 'badge-rejected' : 'badge-screening'}">${an.severity}</span>
        </div>
        <div class="anomaly-desc">${an.description}</div>
        <div style="margin-top: 0.4rem; font-size: 0.75rem; color: var(--text-muted);">
          Entity: <code>${an.entity_type} (${an.entity_id})</code>
        </div>
      `;
      list.appendChild(div);
    });
  } catch (err) {
    console.error("Error loading exceptions:", err);
  }
}

document.getElementById("btn-rescan-exceptions").addEventListener("click", loadExceptions);

// ----------------------------------------------------
// Modals
// ----------------------------------------------------
function initModals() {
  const reqModal = document.getElementById("modal-req");
  const offerModal = document.getElementById("modal-offer");
  const intModal = document.getElementById("modal-interview");
  const fbModal = document.getElementById("modal-feedback");

  document.getElementById("btn-create-req").addEventListener("click", async () => {
    // Populate departments
    const res = await fetch(`${API_BASE}/departments/`);
    if (res.ok) {
      const depts = await res.json();
      const sel = document.getElementById("req-dept");
      sel.innerHTML = depts.map(d => `<option value="${d.department_id}">${d.name}</option>`).join("");
    }
    reqModal.classList.add("active");
  });

  document.getElementById("btn-propose-offer-modal").addEventListener("click", () => {
    offerModal.classList.add("active");
  });

  // Schedule interview modal
  document.getElementById("btn-schedule-modal").addEventListener("click", () => {
    const now = new Date();
    now.setDate(now.getDate() + 1);
    now.setHours(10, 0, 0, 0);
    const end = new Date(now);
    end.setHours(11, 0, 0, 0);

    const pad = n => String(n).padStart(2, '0');
    const toLocalISO = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;

    document.getElementById("int-start-time").value = toLocalISO(now);
    document.getElementById("int-end-time").value = toLocalISO(end);
    intModal.classList.add("active");
  });

  // Submit feedback modal
  document.getElementById("btn-submit-feedback-modal").addEventListener("click", () => {
    fbModal.classList.add("active");
  });

  document.querySelectorAll(".modal-close").forEach(btn => {
    btn.addEventListener("click", () => {
      reqModal.classList.remove("active");
      offerModal.classList.remove("active");
      intModal.classList.remove("active");
      fbModal.classList.remove("active");
    });
  });

  // Schedule Interview submission
  document.getElementById("btn-save-interview").addEventListener("click", async (e) => {
    e.preventDefault();
    const appId = parseInt(document.getElementById("int-app-id").value);
    const roundName = document.getElementById("int-round-name").value;
    const startTime = document.getElementById("int-start-time").value;
    const endTime = document.getElementById("int-end-time").value;

    if (!appId || !startTime || !endTime) {
      alert("Please fill in Application ID and schedule times.");
      return;
    }

    const payload = {
      application_id: appId,
      round_name: roundName,
      scheduled_start: new Date(startTime).toISOString(),
      scheduled_end: new Date(endTime).toISOString()
    };

    try {
      const res = await fetch(`${API_BASE}/interviews/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Interview scheduled successfully! Code: ${data.interview_code}`);
        intModal.classList.remove("active");
        loadInterviews();
        loadApplications();
        loadDashboardData();
      } else {
        const err = await res.json();
        alert(`Failed to schedule interview:\n${err.detail || "Error"}`);
      }
    } catch (err) {
      alert("Scheduling request failed.");
    }
  });

  // Submit Feedback submission
  document.getElementById("btn-save-feedback").addEventListener("click", async (e) => {
    e.preventDefault();
    const intId = parseInt(document.getElementById("fb-int-id").value);
    const ivrId = parseInt(document.getElementById("fb-ivr-id").value);
    const tech = parseFloat(document.getElementById("fb-tech").value);
    const prob = parseFloat(document.getElementById("fb-problem").value);
    const comm = parseFloat(document.getElementById("fb-comm").value);
    const rec = document.getElementById("fb-rec").value;
    const comments = document.getElementById("fb-comments").value;

    if (!intId || !ivrId) {
      alert("Please provide both Interview ID and Interviewer ID.");
      return;
    }

    const payload = {
      interview_id: intId,
      interviewer_id: ivrId,
      technical_score: tech,
      problem_solving_score: prob,
      communication_score: comm,
      recommendation: rec,
      comments: comments
    };

    try {
      const res = await fetch(`${API_BASE}/feedback/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Feedback submitted successfully! Code: ${data.feedback_code}\nOverall Score: ${data.overall_score}/10`);
        fbModal.classList.remove("active");
        loadFeedback();
      } else {
        const err = await res.json();
        alert(`Cannot submit feedback:\n${err.detail || "Error"}`);
      }
    } catch (err) {
      alert("Feedback submission failed.");
    }
  });

  document.getElementById("btn-save-req").addEventListener("click", async (e) => {
    e.preventDefault();
    const payload = {
      job_title: document.getElementById("req-title").value,
      department_id: parseInt(document.getElementById("req-dept").value),
      openings: parseInt(document.getElementById("req-openings").value),
      min_salary: parseFloat(document.getElementById("req-min-sal").value),
      max_salary: parseFloat(document.getElementById("req-max-sal").value),
      experience_required: parseFloat(document.getElementById("req-exp").value)
    };

    try {
      const res = await fetch(`${API_BASE}/requisitions/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("Requisition created successfully.");
        reqModal.classList.remove("active");
        loadRequisitions();
        loadDashboardData();
      } else {
        const err = await res.json();
        alert(`Error creating requisition: ${err.detail || "Validation error"}`);
      }
    } catch (err) {
      alert("Failed to submit requisition.");
    }
  });

  document.getElementById("btn-save-offer").addEventListener("click", async (e) => {
    e.preventDefault();
    const payload = {
      application_id: parseInt(document.getElementById("offer-app-id").value),
      offered_salary: parseFloat(document.getElementById("offer-sal").value),
      joining_date: document.getElementById("offer-joining").value ? new Date(document.getElementById("offer-joining").value).toISOString() : null
    };

    try {
      const res = await fetch(`${API_BASE}/offers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("Offer proposed successfully within approved salary band.");
        offerModal.classList.remove("active");
        loadOffers();
        loadDashboardData();
      } else {
        const err = await res.json();
        alert(`Offer Policy Blocked:\n${err.detail || "Validation error"}`);
      }
    } catch (err) {
      alert("Failed to submit offer proposal.");
    }
  });
}
