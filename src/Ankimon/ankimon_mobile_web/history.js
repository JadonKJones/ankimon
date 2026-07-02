// Escape HTML metacharacters before interpolating user-controlled strings
// (Pokemon nicknames) into innerHTML — prevents stored-XSS from malicious names.
function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
}

function showConfirm(message, onConfirm, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.zIndex = '1000';

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.maxWidth = '400px';

    const head = document.createElement('div');
    head.className = 'modal-head';
    const title = document.createElement('h3');
    title.textContent = 'Confirmation';
    head.appendChild(title);

    const body = document.createElement('div');
    body.className = 'modal-body';
    body.style.padding = '18px';
    body.style.fontSize = '0.95rem';
    body.style.lineHeight = '1.4';
    body.style.color = 'var(--text-main)';
    body.textContent = message;

    const foot = document.createElement('div');
    foot.className = 'modal-foot';
    foot.style.gap = '10px';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-secondary';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.onclick = function() {
        document.body.removeChild(overlay);
        if (onCancel) onCancel();
    };

    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'btn btn-primary';
    confirmBtn.textContent = 'Confirm';
    confirmBtn.onclick = function() {
        document.body.removeChild(overlay);
        onConfirm();
    };

    foot.appendChild(cancelBtn);
    foot.appendChild(confirmBtn);

    modal.appendChild(head);
    modal.appendChild(body);
    modal.appendChild(foot);
    overlay.appendChild(modal);

    document.body.appendChild(overlay);
}

function showAlert(message, onOk = null) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.zIndex = '1000';

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.maxWidth = '400px';

    const head = document.createElement('div');
    head.className = 'modal-head';
    const title = document.createElement('h3');
    title.textContent = 'Notification';
    head.appendChild(title);

    const body = document.createElement('div');
    body.className = 'modal-body';
    body.style.padding = '18px';
    body.style.fontSize = '0.95rem';
    body.style.lineHeight = '1.4';
    body.style.color = 'var(--text-main)';
    body.textContent = message;

    const foot = document.createElement('div');
    foot.className = 'modal-foot';

    const okBtn = document.createElement('button');
    okBtn.className = 'btn btn-primary';
    okBtn.textContent = 'OK';
    okBtn.onclick = function() {
        document.body.removeChild(overlay);
        if (onOk) onOk();
    };

    foot.appendChild(okBtn);

    modal.appendChild(head);
    modal.appendChild(body);
    modal.appendChild(foot);
    overlay.appendChild(modal);

    document.body.appendChild(overlay);
}

let mobileBridge = null;
let nav = null;


new QWebChannel(qt.webChannelTransport, function(channel) {
    mobileBridge = channel.objects.mobile;
    nav = channel.objects && channel.objects.nav;
    window.nav = nav;
    loadHistory();
    if (window.wireNavSwitcher) {
        window.wireNavSwitcher(nav);
    }
});

function goToMobileReviews() {
    if (nav && typeof nav.openMobile === 'function') {
        nav.openMobile();
    }
}

function goToHistory() {
    // Already on History tab
}

function loadHistory() {
    if (!mobileBridge || typeof mobileBridge.getMobileHistory !== 'function') return;
    mobileBridge.getMobileHistory(function(historyList) {
        initializeHistory(historyList);
    });
}

window.initializeHistory = function(historyList) {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
    renderHistory(historyList);
};

window.liveRefreshHistory = function(historyList) {
    renderHistory(historyList);
};

function renderHistory(historyList) {
    const emptyEl = document.getElementById('history-empty');
    const listEl = document.getElementById('history-list');
    
    if (!historyList || historyList.length === 0) {
        if (emptyEl) emptyEl.classList.remove('hidden');
        if (listEl) listEl.classList.add('hidden');
        return;
    }
    
    if (emptyEl) emptyEl.classList.add('hidden');
    if (listEl) listEl.classList.remove('hidden');
    
    listEl.innerHTML = '';
    
    historyList.forEach(entry => {
        const item = document.createElement('div');
        item.className = `history-item outcome-${entry.outcome}`;
        
        let outcomeBadge = '';
        if (entry.outcome === 'caught') {
            outcomeBadge = '<span class="outcome-badge badge-caught">CAUGHT</span>';
        } else if (entry.outcome === 'defeated') {
            outcomeBadge = '<span class="outcome-badge badge-defeated">DEFEATED</span>';
        } else if (entry.outcome === 'lost') {
            outcomeBadge = '<span class="outcome-badge badge-lost">LOST</span>';
        } else if (entry.outcome === 'escaped') {
            outcomeBadge = '<span class="outcome-badge badge-escaped">ESCAPED</span>';
        }
        
        const shinyTag = entry.enemy_shiny ? '✨ ' : '';
        const companionName = escapeHtml(entry.companion_name || 'Companion');
        const enemyName = escapeHtml(entry.enemy_name || '???');
        const vsDetails = `Your <strong>${companionName}</strong> (Lv.${entry.companion_level || 5}) vs wild <strong>${shinyTag}${enemyName}</strong> (Lv.${entry.enemy_level || 5})`;
        
        let rewards = [];
        if (entry.xp_gained > 0) {
            rewards.push(`<span class="reward-val reward-xp">+${entry.xp_gained} XP</span>`);
        }
        if (entry.trainer_xp_gained > 0) {
            rewards.push(`<span class="reward-val reward-txp">+${entry.trainer_xp_gained} Trainer XP</span>`);
        }
        if (entry.cash_gained > 0) {
            rewards.push(`<span class="reward-val reward-cash">+${entry.cash_gained}¥</span>`);
        }
        
        const rewardsSection = rewards.length > 0 
            ? `<div class="history-item-rewards">${rewards.join(' ')}</div>`
            : '';
            
        item.innerHTML = `
            <div class="history-item-main">
                <div class="history-item-left">
                    ${outcomeBadge}
                    <span class="history-item-details">${vsDetails}</span>
                </div>
                <span class="history-item-time">${formatTime(entry.timestamp)}</span>
            </div>
            ${rewardsSection}
        `;
        
        listEl.appendChild(item);
    });
}

function clearHistory() {
    if (!mobileBridge || typeof mobileBridge.clearMobileHistory !== 'function') return;
    showConfirm("Are you sure you want to clear your mobile battle history?", function() {
        mobileBridge.clearMobileHistory(function(success) {
            if (success) {
                loadHistory();
            } else {
                showAlert("Failed to clear mobile history.");
            }
        });
    });
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    try {
        const date = new Date(timestamp);
        const now = new Date();
        
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return '';
    }
}
