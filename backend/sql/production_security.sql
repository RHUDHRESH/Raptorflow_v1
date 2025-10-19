-- Production Security Configuration for RaptorFlow ADAPT
-- This script implements comprehensive database security measures

-- Enable Row Level Security on all tables
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE positioning_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE icps ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE sostac_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_ladder ENABLE ROW LEVEL SECURITY;
ALTER TABLE trend_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE route_back_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "Businesses can view own business" ON businesses;
DROP POLICY IF EXISTS "Businesses can create own business" ON businesses;
DROP POLICY IF EXISTS "Businesses can update own business" ON businesses;
DROP POLICY IF EXISTS "Businesses can delete own business" ON businesses;

-- Businesses table policies
CREATE POLICY "Businesses can view own business" ON businesses
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Businesses can create own business" ON businesses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Businesses can update own business" ON businesses
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Businesses can delete own business" ON businesses
    FOR DELETE USING (auth.uid()::text = user_id);

-- Subscriptions table policies
DROP POLICY IF EXISTS "Users can view own subscriptions" ON subscriptions;
DROP POLICY IF EXISTS "System can create subscriptions" ON subscriptions;
DROP POLICY IF EXISTS "System can update subscriptions" ON subscriptions;

CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "System can create subscriptions" ON subscriptions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "System can update subscriptions" ON subscriptions
    FOR UPDATE USING (true);

-- Positioning analyses policies
DROP POLICY IF EXISTS "Businesses can view own positioning" ON positioning_analyses;
DROP POLICY IF EXISTS "Businesses can create own positioning" ON positioning_analyses;
DROP POLICY IF EXISTS "Businesses can update own positioning" ON positioning_analyses;

CREATE POLICY "Businesses can view own positioning" ON positioning_analyses
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own positioning" ON positioning_analyses
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can update own positioning" ON positioning_analyses
    FOR UPDATE USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- ICPs policies
DROP POLICY IF EXISTS "Businesses can view own ICPs" ON icps;
DROP POLICY IF EXISTS "Businesses can create own ICPs" ON icps;
DROP POLICY IF EXISTS "Businesses can update own ICPs" ON icps;
DROP POLICY IF EXISTS "Businesses can delete own ICPs" ON icps;

CREATE POLICY "Businesses can view own ICPs" ON icps
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own ICPs" ON icps
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can update own ICPs" ON icps
    FOR UPDATE USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can delete own ICPs" ON icps
    FOR DELETE USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Moves policies
DROP POLICY IF EXISTS "Businesses can view own moves" ON moves;
DROP POLICY IF EXISTS "Businesses can create own moves" ON moves;
DROP POLICY IF EXISTS "Businesses can update own moves" ON moves;
DROP POLICY IF EXISTS "Businesses can delete own moves" ON moves;

CREATE POLICY "Businesses can view own moves" ON moves
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own moves" ON moves
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can update own moves" ON moves
    FOR UPDATE USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can delete own moves" ON moves
    FOR DELETE USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Evidence nodes policies
DROP POLICY IF EXISTS "Businesses can view own evidence" ON evidence_nodes;
DROP POLICY IF EXISTS "Businesses can create own evidence" ON evidence_nodes;

CREATE POLICY "Businesses can view own evidence" ON evidence_nodes
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own evidence" ON evidence_nodes
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Evidence edges policies
DROP POLICY IF EXISTS "Businesses can view own evidence edges" ON evidence_edges;
DROP POLICY IF EXISTS "Businesses can create own evidence edges" ON evidence_edges;

CREATE POLICY "Businesses can view own evidence edges" ON evidence_edges
    FOR SELECT USING (
        source_node_id IN (
            SELECT id FROM evidence_nodes WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        ) AND target_node_id IN (
            SELECT id FROM evidence_nodes WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        )
    );

CREATE POLICY "Businesses can create own evidence edges" ON evidence_edges
    FOR INSERT WITH CHECK (
        source_node_id IN (
            SELECT id FROM evidence_nodes WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        ) AND target_node_id IN (
            SELECT id FROM evidence_nodes WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        )
    );

-- SOSTAC analyses policies
DROP POLICY IF EXISTS "Businesses can view own SOSTAC" ON sostac_analyses;
DROP POLICY IF EXISTS "Businesses can create own SOSTAC" ON sostac_analyses;

CREATE POLICY "Businesses can view own SOSTAC" ON sostac_analyses
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own SOSTAC" ON sostac_analyses
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Competitor ladder policies
DROP POLICY IF EXISTS "Businesses can view own competitor ladder" ON competitor_ladder;
DROP POLICY IF EXISTS "Businesses can create own competitor ladder" ON competitor_ladder;

CREATE POLICY "Businesses can view own competitor ladder" ON competitor_ladder
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own competitor ladder" ON competitor_ladder
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Trend checks policies
DROP POLICY IF EXISTS "Businesses can view own trend checks" ON trend_checks;
DROP POLICY IF EXISTS "Businesses can create own trend checks" ON trend_checks;

CREATE POLICY "Businesses can view own trend checks" ON trend_checks
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own trend checks" ON trend_checks
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Performance metrics policies
DROP POLICY IF EXISTS "Businesses can view own performance metrics" ON performance_metrics;
DROP POLICY IF EXISTS "Businesses can create own performance metrics" ON performance_metrics;

CREATE POLICY "Businesses can view own performance metrics" ON performance_metrics
    FOR SELECT USING (
        move_id IN (
            SELECT id FROM moves WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        )
    );

CREATE POLICY "Businesses can create own performance metrics" ON performance_metrics
    FOR INSERT WITH CHECK (
        move_id IN (
            SELECT id FROM moves WHERE business_id IN (
                SELECT id FROM businesses WHERE user_id = auth.uid()::text
            )
        )
    );

-- Route back logs policies
DROP POLICY IF EXISTS "Businesses can view own route back logs" ON route_back_logs;
DROP POLICY IF EXISTS "Businesses can create own route back logs" ON route_back_logs;

CREATE POLICY "Businesses can view own route back logs" ON route_back_logs
    FOR SELECT USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Businesses can create own route back logs" ON route_back_logs
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()::text
        )
    );

-- Create security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    business_id UUID,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    severity TEXT DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'critical'))
);

-- Enable RLS on audit log
ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;

-- Audit log policies
DROP POLICY IF EXISTS "System can insert audit logs" ON security_audit_log;
DROP POLICY IF EXISTS "Users can view own audit logs" ON security_audit_log;

CREATE POLICY "System can insert audit logs" ON security_audit_log
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view own audit logs" ON security_audit_log
    FOR SELECT USING (auth.uid()::text = user_id);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO security_audit_log (
        user_id,
        business_id,
        action,
        table_name,
        record_id,
        old_values,
        new_values
    ) VALUES (
        COALESCE(current_setting('app.current_user_id', true), 'anonymous'),
        COALESCE(NEW.business_id, OLD.business_id),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create audit triggers for sensitive tables
DROP TRIGGER IF EXISTS audit_businesses ON businesses;
CREATE TRIGGER audit_businesses
    AFTER INSERT OR UPDATE OR DELETE ON businesses
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

DROP TRIGGER IF EXISTS audit_subscriptions ON subscriptions;
CREATE TRIGGER audit_subscriptions
    AFTER INSERT OR UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

DROP TRIGGER IF EXISTS audit_icps ON icps;
CREATE TRIGGER audit_icps
    AFTER INSERT OR UPDATE OR DELETE ON icps
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

DROP TRIGGER IF EXISTS audit_moves ON moves;
CREATE TRIGGER audit_moves
    AFTER INSERT OR UPDATE OR DELETE ON moves
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_security_audit_log_user_id ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_business_id ON security_audit_log(business_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_timestamp ON security_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_action ON security_audit_log(action);

-- Create function to check subscription limits
CREATE OR REPLACE FUNCTION check_subscription_limits(
    p_user_id TEXT,
    p_business_id UUID,
    p_resource_type TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    current_subscription RECORD;
    current_count INTEGER;
    max_limit INTEGER;
BEGIN
    -- Get current subscription
    SELECT s.* INTO current_subscription
    FROM subscriptions s
    JOIN businesses b ON s.business_id = b.id
    WHERE b.id = p_business_id AND b.user_id = p_user_id
    ORDER BY s.created_at DESC
    LIMIT 1;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No subscription found for business';
    END IF;
    
    -- Check limits based on resource type
    CASE p_resource_type
        WHEN 'icps' THEN
            SELECT COUNT(*) INTO current_count
            FROM icps
            WHERE business_id = p_business_id;
            
            max_limit := current_subscription.max_icps;
            
        WHEN 'moves' THEN
            SELECT COUNT(*) INTO current_count
            FROM moves
            WHERE business_id = p_business_id AND status != 'deleted';
            
            max_limit := current_subscription.max_moves;
            
        ELSE
            RAISE EXCEPTION 'Unknown resource type: %', p_resource_type;
    END CASE;
    
    RETURN current_count < max_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function for user authentication
CREATE OR REPLACE FUNCTION authenticate_user(
    p_email TEXT,
    p_password_hash TEXT
)
RETURNS TABLE(user_id TEXT, business_id UUID, tier TEXT) AS $$
DECLARE
    user_record RECORD;
BEGIN
    -- This would integrate with your authentication system
    -- For now, return a placeholder
    SELECT 'user_id'::TEXT, gen_random_uuid()::UUID, 'basic'::TEXT
    INTO user_id, business_id, tier;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT INSERT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT DELETE ON ALL TABLES IN SCHEMA public TO authenticated;

-- Grant specific permissions for anonymous users (for business creation)
GRANT INSERT ON businesses TO anon;
GRANT INSERT ON subscriptions TO anon;

-- Create view for user dashboard
CREATE OR REPLACE VIEW user_dashboard AS
SELECT 
    b.id as business_id,
    b.name as business_name,
    b.industry,
    b.location,
    s.tier,
    s.max_icps,
    s.max_moves,
    (SELECT COUNT(*) FROM icps WHERE business_id = b.id) as current_icps,
    (SELECT COUNT(*) FROM moves WHERE business_id = b.id AND status != 'deleted') as current_moves,
    (SELECT COUNT(*) FROM positioning_analyses WHERE business_id = b.id) as positioning_count,
    b.created_at
FROM businesses b
JOIN subscriptions s ON b.id = s.business_id
WHERE b.user_id = auth.uid()::text;

-- Enable RLS on view
ALTER TABLE user_dashboard ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own dashboard" ON user_dashboard
    FOR SELECT USING (true);

-- Create stored procedure for secure data cleanup
CREATE OR REPLACE FUNCTION secure_cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete audit logs older than 1 year
    DELETE FROM security_audit_log 
    WHERE timestamp < NOW() - INTERVAL '1 year';
    
    -- Delete old trend checks (older than 6 months)
    DELETE FROM trend_checks 
    WHERE created_at < NOW() - INTERVAL '6 months';
    
    -- Archive old performance metrics (older than 1 year)
    -- This would move to an archive table in production
    
    RAISE NOTICE 'Data cleanup completed';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule cleanup function (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * 0', 'SELECT secure_cleanup_old_data();');

COMMIT;
