
-- ============================================================================
-- DUAL INDICATOR SYSTEM DATABASE FUNCTIONS
-- Run this SQL after creating the tables above
-- ============================================================================

-- Function to process real-time price updates
CREATE OR REPLACE FUNCTION process_realtime_price_update(
    p_symbol VARCHAR,
    p_price DECIMAL,
    p_timestamp BIGINT,
    p_session VARCHAR,
    p_volume INTEGER DEFAULT 0,
    p_bid DECIMAL DEFAULT 0,
    p_ask DECIMAL DEFAULT 0,
    p_change DECIMAL DEFAULT 0
) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
    v_active_trades INTEGER;
BEGIN
    -- Insert price update
    INSERT INTO realtime_prices (
        symbol, price, timestamp, session, volume, bid, ask, price_change
    ) VALUES (
        p_symbol, p_price, p_timestamp, p_session, p_volume, p_bid, p_ask, p_change
    );
    
    -- Count active trades that need MFE updates
    SELECT COUNT(*) INTO v_active_trades
    FROM enhanced_signals_v2
    WHERE confirmation_received = TRUE
    AND resolved = FALSE
    AND entry_price IS NOT NULL;
    
    -- Update MFE for active trades if any exist
    IF v_active_trades > 0 THEN
        PERFORM update_active_trades_mfe(p_price, p_timestamp);
    END IF;
    
    -- Return success result
    v_result := jsonb_build_object(
        'success', TRUE,
        'price_recorded', p_price,
        'active_trades_updated', v_active_trades,
        'timestamp', p_timestamp
    );
    
    RETURN v_result;
    
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object(
        'success', FALSE,
        'error', SQLERRM
    );
END;
$$ LANGUAGE plpgsql;

-- Function to update MFE for active trades
CREATE OR REPLACE FUNCTION update_active_trades_mfe(
    p_current_price DECIMAL,
    p_timestamp BIGINT
) RETURNS JSONB AS $$
DECLARE
    v_trade RECORD;
    v_new_mfe DECIMAL;
    v_is_new_high BOOLEAN;
    v_updates_count INTEGER := 0;
BEGIN
    -- Loop through all active trades
    FOR v_trade IN 
        SELECT trade_uuid, signal_type, entry_price, stop_loss_price, 
               risk_distance, current_mfe, max_mfe
        FROM enhanced_signals_v2
        WHERE confirmation_received = TRUE
        AND resolved = FALSE
        AND entry_price IS NOT NULL
        AND stop_loss_price IS NOT NULL
        AND risk_distance IS NOT NULL
        AND risk_distance > 0
    LOOP
        -- Calculate new MFE
        IF v_trade.signal_type = 'Bullish' THEN
            v_new_mfe := (p_current_price - v_trade.entry_price) / v_trade.risk_distance;
        ELSE -- Bearish
            v_new_mfe := (v_trade.entry_price - p_current_price) / v_trade.risk_distance;
        END IF;
        
        -- Check if this is a new MFE high
        v_is_new_high := v_new_mfe > COALESCE(v_trade.max_mfe, 0);
        
        -- Update enhanced_signals_v2 table
        UPDATE enhanced_signals_v2 SET
            current_mfe = v_new_mfe,
            max_mfe = CASE WHEN v_is_new_high THEN v_new_mfe ELSE max_mfe END
        WHERE trade_uuid = v_trade.trade_uuid;
        
        -- Insert MFE update record (only if significant change or new high)
        IF v_is_new_high OR ABS(v_new_mfe - COALESCE(v_trade.current_mfe, 0)) > 0.1 THEN
            INSERT INTO realtime_mfe_updates (
                trade_uuid, price, mfe_value, is_new_high, timestamp
            ) VALUES (
                v_trade.trade_uuid, p_current_price, v_new_mfe, v_is_new_high, p_timestamp
            );
        END IF;
        
        v_updates_count := v_updates_count + 1;
    END LOOP;
    
    RETURN jsonb_build_object(
        'success', TRUE,
        'trades_updated', v_updates_count,
        'current_price', p_current_price
    );
    
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object(
        'success', FALSE,
        'error', SQLERRM
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get latest price
CREATE OR REPLACE FUNCTION get_latest_price(p_symbol VARCHAR DEFAULT 'NQ') 
RETURNS TABLE(price DECIMAL, timestamp BIGINT, session VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT rp.price, rp.timestamp, rp.session
    FROM realtime_prices rp
    WHERE rp.symbol = p_symbol
    ORDER BY rp.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to clean old price data (keep last 24 hours)
CREATE OR REPLACE FUNCTION cleanup_old_price_data() RETURNS void AS $$
BEGIN
    DELETE FROM realtime_prices 
    WHERE created_at < NOW() - INTERVAL '24 hours';
    
    DELETE FROM realtime_mfe_updates 
    WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Log cleanup
    RAISE NOTICE 'Cleaned up old price data and MFE updates';
END;
$$ LANGUAGE plpgsql;
