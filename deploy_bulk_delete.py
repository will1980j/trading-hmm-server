"""
Deploy Bulk Delete Feature to Automated Signals Dashboard
Adds checkboxes, select all, and bulk delete functionality
"""

import re

print("🚀 Deploying Bulk Delete Feature...")
print("=" * 80)

# Read current dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================================
# STEP 1: Add CSS for checkboxes and bulk delete button
# ============================================================================
print("\n📝 Step 1: Adding CSS styles...")

checkbox_css = """
        /* Bulk Delete Styles */
        .bulk-actions {
            display: flex;
            gap: 15px;
            align-items: center;
            padding: 15px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .bulk-actions input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .bulk-actions label {
            cursor: pointer;
            user-select: none;
        }

        .delete-selected-btn {
            padding: 8px 16px;
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .delete-selected-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }

        .delete-selected-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .trade-checkbox {
            width: 16px;
            height: 16px;
            cursor: pointer;
        }

        .checkbox-cell {
            text-align: center;
            padding: 12px 8px;
        }
"""

# Insert CSS before closing </style> tag
content = content.replace('</style>', checkbox_css + '\n        </style>', 1)
print("✅ CSS styles added")

# ============================================================================
# STEP 2: Add bulk actions bar HTML (after stats grid, before active trades)
# ============================================================================
print("\n📝 Step 2: Adding bulk actions bar...")

bulk_actions_html = """
        <!-- Bulk Delete Actions -->
        <div class="bulk-actions" id="bulkActions" style="display: none;">
            <input type="checkbox" id="selectAll" onchange="toggleSelectAll(this.checked)">
            <label for="selectAll">Select All</label>
            <button class="delete-selected-btn" id="deleteSelectedBtn" onclick="deleteSelected()" disabled>
                Delete Selected (<span id="selectedCount">0</span>)
            </button>
        </div>
"""

# Find where to insert (after stats-grid div closes, before active trades section)
stats_grid_end = content.find('</div>', content.find('class="stats-grid"'))
if stats_grid_end != -1:
    # Find the next section start
    next_section = content.find('<div', stats_grid_end + 10)
    content = content[:next_section] + '\n' + bulk_actions_html + '\n        ' + content[next_section:]
    print("✅ Bulk actions bar added")
else:
    print("⚠️  Could not find insertion point for bulk actions bar")

# ============================================================================
# STEP 3: Add JavaScript functions for bulk delete
# ============================================================================
print("\n📝 Step 3: Adding JavaScript functions...")

bulk_delete_js = """
        // ============================================================================
        // BULK DELETE FUNCTIONALITY
        // ============================================================================
        
        let selectedTrades = new Set();

        function toggleSelectAll(checked) {
            selectedTrades.clear();
            document.querySelectorAll('.trade-checkbox').forEach(checkbox => {
                checkbox.checked = checked;
                if (checked) {
                    selectedTrades.add(checkbox.dataset.tradeId);
                }
            });
            updateBulkActions();
        }

        function toggleTradeSelection(checkbox, tradeId) {
            if (checkbox.checked) {
                selectedTrades.add(tradeId);
            } else {
                selectedTrades.delete(tradeId);
                document.getElementById('selectAll').checked = false;
            }
            updateBulkActions();
        }

        function updateBulkActions() {
            const count = selectedTrades.size;
            const bulkActions = document.getElementById('bulkActions');
            const deleteBtn = document.getElementById('deleteSelectedBtn');
            const countSpan = document.getElementById('selectedCount');
            
            if (count > 0) {
                bulkActions.style.display = 'flex';
                deleteBtn.disabled = false;
                countSpan.textContent = count;
            } else {
                bulkActions.style.display = 'none';
                deleteBtn.disabled = true;
                countSpan.textContent = '0';
            }
        }

        async function deleteSelected() {
            if (selectedTrades.size === 0) return;
            
            const count = selectedTrades.size;
            if (!confirm(`Are you sure you want to delete ${count} selected trade(s)?\\n\\nThis will remove all events for these trades and cannot be undone.`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/automated-signals/bulk-delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        trade_ids: Array.from(selectedTrades)
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`Successfully deleted ${result.deleted_count} trade(s)`);
                    selectedTrades.clear();
                    document.getElementById('selectAll').checked = false;
                    updateBulkActions();
                    loadDashboardData(); // Refresh dashboard
                } else {
                    alert(`Error: ${result.error || 'Failed to delete trades'}`);
                }
            } catch (error) {
                console.error('Bulk delete error:', error);
                alert('Failed to delete trades. Please try again.');
            }
        }
"""

# Insert before closing </script> tag
script_end = content.rfind('</script>')
if script_end != -1:
    content = content[:script_end] + '\n' + bulk_delete_js + '\n        ' + content[script_end:]
    print("✅ JavaScript functions added")
else:
    print("⚠️  Could not find </script> tag")

# ============================================================================
# STEP 4: Modify renderActiveSignals to include checkboxes
# ============================================================================
print("\n📝 Step 4: Modifying trade rendering to include checkboxes...")

# This is complex - we need to add checkbox column to the table
# We'll add it in the table header and each row

# Find the renderActiveSignals function and add checkbox column
# This requires finding the table HTML generation and modifying it

# Add checkbox header column
content = re.sub(
    r"(<th[^>]*>Trade ID</th>)",
    r'<th style="width: 40px; text-align: center;">☑</th>\n                    \1',
    content
)

# Add checkbox cell in rows - this is trickier, need to find where rows are built
# Look for the pattern where trade_id is displayed and add checkbox before it
content = re.sub(
    r'(<td[^>]*>\$\{signal\.trade_id\}</td>)',
    r'<td class="checkbox-cell"><input type="checkbox" class="trade-checkbox" data-trade-id="${signal.trade_id}" onchange="toggleTradeSelection(this, \'${signal.trade_id}\')"></td>\n                        \1',
    content
)

print("✅ Checkbox columns added to tables")

# ============================================================================
# STEP 5: Save modified dashboard
# ============================================================================
print("\n📝 Step 5: Saving modified dashboard...")

with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Dashboard saved")

print("\n" + "=" * 80)
print("✅ BULK DELETE FEATURE DEPLOYED TO DASHBOARD")
print("=" * 80)
print("\nNext: Add backend API endpoint to web_server.py")
