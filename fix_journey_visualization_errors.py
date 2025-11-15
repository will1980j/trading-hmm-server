"""
Fix journey visualization errors and add better debugging
"""

# Read dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add console logging to renderTradeJourney for debugging
old_render_start = '''        // Trade Journey Visualization with D3.js
        function renderTradeJourney(trade) {
            // Clear existing visualization
            d3.select('#journeyViz').selectAll('*').remove();'''

new_render_start = '''        // Trade Journey Visualization with D3.js
        function renderTradeJourney(trade) {
            console.log('renderTradeJourney called with trade:', trade);
            
            // Check if D3 is loaded
            if (typeof d3 === 'undefined') {
                console.error('D3.js is not loaded!');
                document.getElementById('journeyViz').innerHTML = '<div style="color: #ef4444; text-align: center; padding: 40px;">D3.js library not loaded</div>';
                return;
            }
            
            // Clear existing visualization
            d3.select('#journeyViz').selectAll('*').remove();'''

html = html.replace(old_render_start, new_render_start)

# Add error handling wrapper around the entire function
old_function_end = '''        }

        function closeTradeDetail()'''

new_function_end = '''            
            console.log('Journey visualization rendered successfully');
        }

        function closeTradeDetail()'''

# Find the last part of renderTradeJourney and wrap in try-catch
# Actually, let's add a simpler fallback if no events
old_events_check = '''            const events = trade.events;
            const latestEvent = events[events.length - 1];
            const isActive = !latestEvent.event_type.startsWith('EXIT_');'''

new_events_check = '''            const events = trade.events || [];
            
            // If no events, show message
            if (events.length === 0) {
                console.warn('No events found for trade');
                document.getElementById('journeyViz').innerHTML = '<div style="color: #fbbf24; text-align: center; padding: 40px;">No event data available for this trade</div>';
                return;
            }
            
            const latestEvent = events[events.length - 1];
            const isActive = !latestEvent.event_type.startsWith('EXIT_');
            
            console.log(`Trade has ${events.length} events, isActive: ${isActive}`);'''

html = html.replace(old_events_check, new_events_check)

# Write updated file
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Added debugging and error handling to journey visualization")
print("\nChanges made:")
print("1. Added console logging to track function calls")
print("2. Added D3.js loaded check")
print("3. Added fallback message if no events")
print("4. Added event count logging")
print("\nNow check browser console for errors when clicking a trade!")
