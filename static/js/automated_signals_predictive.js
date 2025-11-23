// PATCH 9 — Predictive Dashboard JS
(function () {
"use strict";

function $(id) { return document.getElementById(id); }

async function loadSummary() {
    const target = $("predictiveSummaryContent");
    try {
        const r = await fetch("/api/automated-signals/predictive/summary");
        const j = await r.json();
        
        if (!j.success) {
            target.textContent = "Error: " + j.error;
            return;
        }
        
        let html = "";
        j.trades.forEach(t => {
            html += `<div style="padding:4px 0; cursor:pointer;" data-tid="${t.trade_id}">`;
            html += `<strong>${t.trade_id}</strong><br/>`;
            html += `AI: ${JSON.stringify(t.ai_detail)}</div>`;
        });
        
        target.innerHTML = html;
        
        Array.from(target.querySelectorAll("[data-tid]")).forEach(el => {
            el.addEventListener("click", () => loadTrade(el.dataset.tid));
        });
        
    } catch (e) {
        target.textContent = "Error loading summary.";
    }
}

async function loadTrade(tid) {
    const lifecycle = $("predictiveLifecycleBox");
    const ai = $("predictiveAIBox");
    const reasoning = $("predictiveReasoningBox");
    
    lifecycle.textContent = "Loading...";
    ai.textContent = "Loading...";
    reasoning.textContent = "Loading...";
    
    try {
        const r = await fetch("/api/automated-signals/predictive/" + tid);
        const j = await r.json();
        
        if (!j.success) {
            lifecycle.textContent = "Error: " + j.error;
            ai.textContent = "{}";
            reasoning.textContent = "";
            return;
        }
        
        lifecycle.textContent = JSON.stringify(j.lifecycle_events, null, 2);
        ai.textContent = JSON.stringify(j.ai_detail, null, 2);
        
        if (j.ai_detail && j.ai_detail.ai_reasoning) {
            reasoning.textContent = j.ai_detail.ai_reasoning;
        } else {
            reasoning.textContent = "No reasoning available.";
        }
        
    } catch (e) {
        lifecycle.textContent = "Error loading trade.";
        ai.textContent = "{}";
        reasoning.textContent = "";
    }
}

document.addEventListener("DOMContentLoaded", loadSummary);

})();
