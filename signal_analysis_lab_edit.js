// Edit functionality for signal analysis lab

let editingSignalId = null;

function editSignal(id) {
    const signal = signals.find(s => s.id === id);
    if (!signal) return;
    
    // Populate form with signal data
    document.getElementById('signalDate').value = signal.date;
    document.getElementById('entryTime').value = signal.time;
    document.getElementById('bias').value = signal.bias;
    document.getElementById('session').value = signal.session;
    document.getElementById('signalType').value = signal.signalType;
    document.getElementById('openPrice').value = signal.openPrice;
    document.getElementById('entryPrice').value = signal.entryPrice;
    document.getElementById('stopLoss').value = signal.stopLoss;
    document.getElementById('takeProfit').value = signal.takeProfit;
    document.getElementById('beAchieved').checked = signal.beAchieved;
    document.getElementById('breakeven').value = signal.breakeven;
    document.getElementById('mfe').value = signal.mfe;
    document.getElementById('positionSize').value = signal.positionSize;
    document.getElementById('commission').value = signal.commission;
    document.getElementById('newsProximity').value = signal.newsProximity;
    
    // Handle news events
    if (signal.newsEvent) {
        const events = signal.newsEvent.split(', ');
        const checkboxes = document.querySelectorAll('#newsEventDropdown input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = events.includes(cb.value));
        updateNewsSelection();
    }
    
    // Set editing mode
    editingSignalId = id;
    
    // Change button text
    const addBtn = document.querySelector('.add-signal-btn');
    addBtn.textContent = 'Update';
    addBtn.style.background = 'linear-gradient(45deg, #ffa502, #ff6348)';
    
    // Scroll to form
    document.querySelector('.data-input').scrollIntoView({ behavior: 'smooth' });
}

function updateSignal() {
    const signalIndex = signals.findIndex(s => s.id === editingSignalId);
    if (signalIndex === -1) return;
    
    const updatedSignal = {
        id: editingSignalId,
        date: document.getElementById('signalDate').value,
        time: document.getElementById('entryTime').value,
        bias: document.getElementById('bias').value,
        session: document.getElementById('session').value,
        signalType: document.getElementById('signalType').value,
        openPrice: parseFloat(document.getElementById('openPrice').value) || 0,
        entryPrice: parseFloat(document.getElementById('entryPrice').value) || 0,
        stopLoss: parseFloat(document.getElementById('stopLoss').value) || 0,
        takeProfit: parseFloat(document.getElementById('takeProfit').value) || 0,
        beAchieved: document.getElementById('beAchieved').checked,
        breakeven: parseFloat(document.getElementById('breakeven').value) || 0,
        mfe: parseFloat(document.getElementById('mfe').value) || 0,
        positionSize: parseInt(document.getElementById('positionSize').value) || 1,
        commission: parseFloat(document.getElementById('commission').value) || 0,
        newsProximity: document.getElementById('newsProximity').value,
        newsEvent: getSelectedNewsEvents(),
        screenshot: window.currentScreenshot || signals[signalIndex].screenshot
    };
    
    if (!updatedSignal.date || !updatedSignal.entryPrice || !updatedSignal.stopLoss) {
        // Use safer notification instead of alert
        if (typeof showNotification === 'function') {
            showNotification('Please fill in Date, Entry Price, and Stop Loss', 'error');
        } else {
            console.warn('Please fill in Date, Entry Price, and Stop Loss');
        }
        return;
    }
    
    signals[signalIndex] = updatedSignal;
    updateDisplay();
    cancelEdit();
}

function cancelEdit() {
    editingSignalId = null;
    clearInputs();
    
    // Reset button
    const addBtn = document.querySelector('.add-signal-btn');
    addBtn.textContent = 'Add';
    addBtn.style.background = 'linear-gradient(45deg, #00ff88, #00d4aa)';
}

// Override the original addSignal function
function addSignal() {
    if (editingSignalId) {
        updateSignal();
        return;
    }
    
    const signal = {
        id: Date.now(),
        date: document.getElementById('signalDate').value,
        time: document.getElementById('entryTime').value,
        bias: document.getElementById('bias').value,
        session: document.getElementById('session').value,
        signalType: document.getElementById('signalType').value,
        openPrice: parseFloat(document.getElementById('openPrice').value) || 0,
        entryPrice: parseFloat(document.getElementById('entryPrice').value) || 0,
        stopLoss: parseFloat(document.getElementById('stopLoss').value) || 0,
        takeProfit: parseFloat(document.getElementById('takeProfit').value) || 0,
        beAchieved: document.getElementById('beAchieved').checked,
        breakeven: parseFloat(document.getElementById('breakeven').value) || 0,
        mfe: parseFloat(document.getElementById('mfe').value) || 0,
        positionSize: parseInt(document.getElementById('positionSize').value) || 1,
        commission: parseFloat(document.getElementById('commission').value) || 0,
        newsProximity: document.getElementById('newsProximity').value,
        newsEvent: getSelectedNewsEvents(),
        screenshot: window.currentScreenshot || null
    };
    
    if (!signal.date || !signal.entryPrice || !signal.stopLoss) {
        // Use safer notification instead of alert
        if (typeof showNotification === 'function') {
            showNotification('Please fill in Date, Entry Price, and Stop Loss', 'error');
        } else {
            console.warn('Please fill in Date, Entry Price, and Stop Loss');
        }
        return;
    }
    
    signals.push(signal);
    updateDisplay();
    clearInputs();
}

// Override the updateTable function to include edit buttons
function updateTable() {
    const tbody = document.getElementById('signalsBody');
    tbody.innerHTML = '';
    
    signals.slice().reverse().forEach(signal => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${signal.date}</td>
            <td>${signal.time}</td>
            <td>${signal.bias}</td>
            <td>${signal.session}</td>
            <td>${signal.signalType}</td>
            <td>${signal.openPrice.toFixed(2)}</td>
            <td>${signal.entryPrice.toFixed(2)}</td>
            <td>${signal.stopLoss.toFixed(2)}</td>
            <td>${signal.takeProfit.toFixed(2)}</td>
            <td>${signal.beAchieved ? '✓' : '✗'}</td>
            <td>${signal.breakeven}R</td>
            <td class="${signal.mfe > 0 ? 'positive' : signal.mfe < 0 ? 'negative' : 'neutral'}">${signal.mfe.toFixed(1)}R</td>
            <td>${signal.positionSize}</td>
            <td>$${signal.commission.toFixed(2)}</td>
            <td>${signal.newsProximity}</td>
            <td>${signal.newsEvent}</td>
            <td>
                <button onclick="editSignal(${signal.id})" style="background: #3742fa; border: none; padding: 4px 8px; border-radius: 4px; color: white; cursor: pointer; font-size: 10px; margin-right: 4px;">Edit</button>
                <button onclick="deleteSignal(${signal.id})" style="background: #ff4757; border: none; padding: 4px 8px; border-radius: 4px; color: white; cursor: pointer; font-size: 10px;">Del</button>
            </td>
        `;
    });
}