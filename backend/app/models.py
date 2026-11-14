"""ORM mappings for the shared, versioned MVP database baseline.

Feature owners add services/DTOs around these mappings; schema changes require
an agreed migration rather than creating tables from application startup.
"""
from sqlalchemy.orm import Mapped, relationship
from app.database import Base
from app.schema_v1 import metadata as baseline_metadata

for _table in baseline_metadata.tables.values():
    _table.to_metadata(Base.metadata)


class Order(Base):
    __table__ = Base.metadata.tables['orders']


class Complaint(Base):
    __table__ = Base.metadata.tables['complaints']
    verified_order: Mapped[Order | None] = relationship(foreign_keys=[__table__.c.verified_order_id])


class CaseMessage(Base):
    __table__ = Base.metadata.tables['case_messages']


class TextAnalysisRun(Base):
    __table__ = Base.metadata.tables['text_analysis_runs']


class ComplaintDecision(Base):
    __table__ = Base.metadata.tables['complaint_decisions']


class CaseReply(Base):
    __table__ = Base.metadata.tables['case_replies']


class ReplyOperation(Base):
    __table__ = Base.metadata.tables['reply_operations']


class AuditEvent(Base):
    __table__ = Base.metadata.tables['audit_events']


class EvidenceAsset(Base):
    __table__ = Base.metadata.tables['evidence_assets']


class EvidenceAnalysis(Base):
    __table__ = Base.metadata.tables['evidence_analyses']


class StaffSession(Base):
    __table__ = Base.metadata.tables['staff_sessions']


class IntegrationState(Base):
    __table__ = Base.metadata.tables['integration_state']


class GmailIntakeFailure(Base):
    __table__ = Base.metadata.tables['gmail_intake_failures']


from app.schema_v2 import attach
attach(Base.metadata)

class BusinessSettings(Base):
    __table__ = Base.metadata.tables['business_settings']
class SettingsVersion(Base):
    __table__ = Base.metadata.tables['business_settings_versions']
class KnowledgeArticle(Base):
    __table__ = Base.metadata.tables['knowledge_articles']
class KnowledgeRevision(Base):
    __table__ = Base.metadata.tables['knowledge_revisions']
class AgentRun(Base):
    __table__ = Base.metadata.tables['agent_runs']
class AgentStep(Base):
    __table__ = Base.metadata.tables['agent_steps']
class ReplyCheck(Base):
    __table__ = Base.metadata.tables['reply_checks']
