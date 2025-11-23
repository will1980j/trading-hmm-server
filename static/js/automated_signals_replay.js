// STAGE 10: Automated Signals Replay JS (READ-ONLY)

(function() {
  let replayCandles = [];
  let currentIndex = 0;
  let isPlaying = false;
  let playTimer = null;
  
  function asReplaySetStatus(msg) {
    const el = document.getElementById('as-replay-status');
    if (el) el.textContent = msg || '';
  }
  
  function asReplaySetCurrent(info) {
    const el = document.getElementById('as-replay-current');
    if (!el) return;
    el.textContent = info || 'No candle selected';
  }
  
  function asReplayRenderCandle(idx) {
    if (!replayCandles || replayCandles.length === 0) {
      asReplaySetCurrent('No candles loaded');
      return;
    }
    if (idx < 0 || idx >= replayCandles.length) {
      idx = 0;
    }
    currentIndex = idx;
    const c = replayCandles[idx];
    asReplaySetCurrent(
      `#${idx + 1}/${replayCandles.length} ` +
      ` ${c.candle_time || ''}  O:${c.open} H:${c.high} L:${c.low} C:${c.close} Vol:${c.volume}`
    );
    const slider = document.getElementById('as-replay-slider');
    if (slider) {
      slider.max = replayCandles.length - 1;
      slider.value = String(idx);
    }
    // Placeholder: future chart rendering can hook into #as-replay-chart here.
  }
  
  function asReplayStop() {
    isPlaying = false;
    if (playTimer) {
      clearInterval(playTimer);
      playTimer = null;
    }
  }
  
  function asReplayPlay() {
    if (!replayCandles || replayCandles.length === 0) return;
    asReplayStop();
    isPlaying = true;
    playTimer = setInterval(() => {
      if (!isPlaying) return;
      const next = currentIndex + 1;
      if (next >= replayCandles.length) {
        asReplayStop();
        return;
      }
      asReplayRenderCandle(next);
    }, 250); // 4 candles/sec as an initial speed
  }
  
  async function asReplayLoad() {
    const symbolEl = document.getElementById('as-replay-symbol');
    const dateEl = document.getElementById('as-replay-date');
    const btn = document.getElementById('as-replay-load');
    
    if (!symbolEl || !dateEl || !btn) return;
    
    const symbol = symbolEl.value || 'NQ1!';
    const date = dateEl.value;
    if (!date) {
      asReplaySetStatus('Please select a date');
      return;
    }
    
    asReplayStop();
    asReplaySetStatus('Loading replay candles...');
    btn.disabled = true;
    
    try {
      const params = new URLSearchParams({
        symbol: symbol,
        date: date,
        timeframe: '1m'
      });
      const resp = await fetch(`/api/automated-signals/replay-candles?${params.toString()}`, {
        method: 'GET',
        headers: {'Accept': 'application/json'}
      });
      const data = await resp.json();
      if (!data.success) {
        asReplaySetStatus(`Error: ${data.error || 'Unknown error'}`);
        replayCandles = [];
        asReplayRenderCandle(0);
        return;
      }
      replayCandles = data.candles || [];
      if (replayCandles.length === 0) {
        asReplaySetStatus('No candles returned for that date');
        asReplayRenderCandle(0);
        return;
      }
      asReplaySetStatus(`Loaded ${replayCandles.length} candles for ${symbol} ${date}`);
      asReplayRenderCandle(0);
    } catch (err) {
      console.error('Replay load error:', err);
      asReplaySetStatus('Replay load error (see console)');
      replayCandles = [];
      asReplayRenderCandle(0);
    } finally {
      btn.disabled = false;
    }
  }
  
  function asReplayInit() {
    const loadBtn = document.getElementById('as-replay-load');
    const slider = document.getElementById('as-replay-slider');
    
    if (loadBtn) {
      loadBtn.addEventListener('click', asReplayLoad);
    }
    
    if (slider) {
      slider.addEventListener('input', function(e) {
        const idx = parseInt(e.target.value || '0', 10);
        asReplayRenderCandle(idx);
      });
    }
    
    // Auto-fill date to "today in NY" if applicable (optional)
    const dateEl = document.getElementById('as-replay-date');
    if (dateEl && !dateEl.value) {
      const today = new Date();
      const y = today.getFullYear();
      const m = String(today.getMonth() + 1).padStart(2, '0');
      const d = String(today.getDate()).padStart(2, '0');
      dateEl.value = `${y}-${m}-${d}`;
    }
    
    asReplaySetStatus('Select date and click "Load Session" to begin');
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', asReplayInit);
  } else {
    asReplayInit();
  }
})();
