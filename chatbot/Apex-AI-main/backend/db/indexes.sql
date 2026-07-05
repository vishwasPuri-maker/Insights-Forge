-- Retail Performance Analytics Ingress Index Optimization
CREATE INDEX idx_retail_tenant_timestamp_sku 
ON retail_transactions (tenant_id, recorded_timestamp DESC, sku_id);

-- Core Decision Center Workflow Priority Queue Optimization
CREATE INDEX idx_decision_tenant_state_priority 
ON decision_cards (tenant_id, workflow_state, priority_level) 
WHERE workflow_state = 'pending';

-- Active Token Blacklist Security Auditing Index Optimization
CREATE INDEX idx_sessions_user_token 
ON user_sessions (user_id, refresh_token_hash);
