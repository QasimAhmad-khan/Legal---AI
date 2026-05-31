# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.user import User  # noqa
from app.models.document import Org, Document  # noqa
from app.models.chunk import Chunk, Precedent, PrecedentChunk  # noqa
from app.models.analysis import Analysis, ComplianceRule, AuditLog  # noqa
