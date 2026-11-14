"""CR-001 additive AI-first schema. Never mutate schema_v1 or old revisions."""
from uuid import uuid4
import sqlalchemy as s
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = s.MetaData()

def col(name, typ, nullable=False, default=None):
    return s.Column(name, typ, nullable=nullable, server_default=s.text(default) if default is not None else None)

def table(name, *cols):
    return s.Table(name, metadata, s.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4), *cols)

def fk(cols, target, name, deferred=False):
    return s.ForeignKeyConstraint(cols, target, name=name, use_alter=deferred,
                                  deferrable=True if deferred else None, initially='DEFERRED' if deferred else None)

business_settings_versions = table('business_settings_versions',
    col('revision', s.Integer), col('display_name', s.String(200)), col('language', s.String(16)),
    col('tone', s.String(24)), col('optional_roles', JSONB, default="'[]'::jsonb"),
    col('review_threshold', s.Numeric(4,3), True), col('actor', s.String(100)), col('note', s.String(2000)),
    col('created_at', s.DateTime(timezone=True), default='now()'),
    s.UniqueConstraint('revision', name='uq_settings_revision'),
    s.CheckConstraint("revision>=1 AND length(btrim(display_name))>0 AND language IN ('vi','en') AND tone IN ('neutral','friendly','formal')", name='ck_settings_values'),
    s.CheckConstraint('review_threshold IS NULL OR review_threshold BETWEEN 0 AND 1', name='ck_settings_threshold'),
    s.CheckConstraint("jsonb_typeof(optional_roles)='array' AND optional_roles <@ '[\"evidence_analysis\"]'::jsonb", name='ck_settings_roles'))
business_settings = s.Table('business_settings', metadata, s.Column('id', s.Integer, primary_key=True, autoincrement=False),
    col('current_version_id', UUID(as_uuid=True)), col('updated_at', s.DateTime(timezone=True), default='now()'),
    fk(['current_version_id'], ['business_settings_versions.id'], 'fk_settings_current'),
    s.CheckConstraint('id=1', name='ck_business_singleton'))
knowledge_articles = table('knowledge_articles', col('current_published_revision_id', UUID(as_uuid=True), True),
    col('events', JSONB, default="'[]'::jsonb"), col('created_at', s.DateTime(timezone=True), default='now()'),
    col('updated_at', s.DateTime(timezone=True), default='now()'),
    fk(['current_published_revision_id','id'], ['knowledge_revisions.id','knowledge_revisions.article_id'], 'fk_knowledge_published', True))
knowledge_revisions = table('knowledge_revisions', col('article_id', UUID(as_uuid=True)), col('revision', s.Integer),
    col('title', s.String(300)), col('body', s.Text), col('topic', s.String(100)), col('source_label', s.String(200)),
    col('source_reference', s.Text, True), col('status', s.String(20), default="'draft'"),
    col('valid_until', s.DateTime(timezone=True), True), col('review_due_at', s.DateTime(timezone=True), True),
    col('has_conflict', s.Boolean, default='false'), col('conflict_note', s.String(2000), True),
    col('author', s.String(100)), col('approved_by', s.String(100), True), col('approved_at', s.DateTime(timezone=True), True),
    col('created_at', s.DateTime(timezone=True), default='now()'), col('updated_at', s.DateTime(timezone=True), default='now()'),
    fk(['article_id'], ['knowledge_articles.id'], 'fk_knowledge_article'),
    s.UniqueConstraint('article_id','revision', name='uq_knowledge_version'),
    s.UniqueConstraint('id','article_id', name='uq_knowledge_revision_owner'),
    s.CheckConstraint("status IN ('draft','pending_review','approved','archived') AND revision>=1 AND length(btrim(title)) BETWEEN 1 AND 300 AND length(btrim(body)) BETWEEN 1 AND 50000", name='ck_knowledge_values'),
    s.CheckConstraint("status<>'approved' OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)", name='ck_knowledge_approval'))
agent_runs = table('agent_runs', col('complaint_id', s.Integer), col('basis_case_version', s.Integer),
    col('settings_version_id', UUID(as_uuid=True)), col('status', s.String(20), default="'queued'"),
    col('required_roles', JSONB), col('trigger', s.String(20)), col('created_at', s.DateTime(timezone=True), default='now()'),
    col('finished_at', s.DateTime(timezone=True), True),
    fk(['settings_version_id'], ['business_settings_versions.id'], 'fk_runs_settings'),
    s.CheckConstraint("basis_case_version>=1 AND status IN ('queued','running','completed','review_required','failed','stale') AND trigger IN ('inbound','retry','manual','prepare')", name='ck_agent_run_values'))
agent_steps = table('agent_steps', col('run_id', UUID(as_uuid=True)), col('role', s.String(32)), col('attempt', s.Integer),
    col('status', s.String(20)), col('source_refs', JSONB, default="'[]'::jsonb"),
    col('input_snapshot', JSONB, default="'{}'::jsonb"), col('output', JSONB, True),
    col('confidence', s.Numeric(4,3), True), col('error_code', s.String(100), True), col('skip_reason', s.String(200), True),
    col('started_at', s.DateTime(timezone=True), True), col('finished_at', s.DateTime(timezone=True), True),
    col('created_at', s.DateTime(timezone=True), default='now()'),
    fk(['run_id'], ['agent_runs.id'], 'fk_steps_run'),
    s.UniqueConstraint('run_id','role','attempt', name='uq_step_attempt'),
    s.CheckConstraint("attempt>=1 AND status IN ('queued','running','completed','failed','waiting_data','stale','skipped')", name='ck_step_values'),
    s.CheckConstraint('confidence IS NULL OR confidence BETWEEN 0 AND 1', name='ck_step_confidence'))
reply_checks = table('reply_checks', col('reply_id', UUID(as_uuid=True)), col('run_id', UUID(as_uuid=True)),
    col('basis_case_version', s.Integer), col('reply_revision', s.Integer), col('settings_version_id', UUID(as_uuid=True)),
    col('status', s.String(20)), col('source_refs', JSONB, default="'[]'::jsonb"),
    col('dependency_hash', s.CHAR(64)), col('content_hash', s.CHAR(64)), col('findings', JSONB, default="'[]'::jsonb"),
    col('checker_version', s.String(60)), col('created_at', s.DateTime(timezone=True), default='now()'),
    fk(['run_id'], ['agent_runs.id'], 'fk_checks_run'),
    fk(['settings_version_id'], ['business_settings_versions.id'], 'fk_checks_settings'),
    s.CheckConstraint("status IN ('passed','blocked','stale','failed') AND basis_case_version>=1 AND reply_revision>=1", name='ck_check_values'))

def attach(target):
    for t in metadata.tables.values():
        if t.name not in target.tables:
            t.to_metadata(target)
    for name, local, remote, cname in [('agent_runs','complaint_id','complaints.id','fk_runs_case'),
                                      ('reply_checks','reply_id','case_replies.id','fk_checks_reply')]:
        t = target.tables[name]
        if cname not in {c.name for c in t.foreign_key_constraints}:
            t.append_constraint(fk([local], [remote], cname))
    for name, cols in [('knowledge_revisions',['article_id','status']),('agent_runs',['complaint_id','created_at']),
                       ('agent_steps',['run_id','role','attempt']),('reply_checks',['reply_id','reply_revision','created_at'])]:
        t=target.tables[name]
        index_name='ix_v4_'+name
        if not any(i.name==index_name for i in t.indexes):
            s.Index(index_name, *[t.c[c] for c in cols])
    t=target.tables['agent_steps']
    if not any(i.name=='uq_step_running' for i in t.indexes):
        s.Index('uq_step_running',t.c.run_id,t.c.role,unique=True,postgresql_where=s.text("status='running'"))
