"""llm usage

Revision ID: 0002
Revises: 0001
Create Date: 2023-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
    -- Ensure ventures can be uniquely identified by tenant_id and id
    ALTER TABLE ventures ADD CONSTRAINT uq_ventures_tenant_id_id UNIQUE (tenant_id, id);

    CREATE TABLE llm_usage (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        venture_id UUID,
        agent TEXT NOT NULL,
        model TEXT NOT NULL,
        input_tokens INT NOT NULL DEFAULT 0,
        output_tokens INT NOT NULL DEFAULT 0,
        cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0.0,
        run_id TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tenant_id, venture_id) REFERENCES ventures(tenant_id, id) ON DELETE CASCADE
    );
    
    ALTER TABLE llm_usage ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY tenant_isolation_policy ON llm_usage
        USING (tenant_id = current_setting('app.current_tenant', TRUE)::UUID);
        
    GRANT SELECT, INSERT ON llm_usage TO swarn_app;
    """)

def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS llm_usage CASCADE;
    ALTER TABLE ventures DROP CONSTRAINT IF EXISTS uq_ventures_tenant_id_id;
    """)
