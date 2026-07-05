"""
Central SQLAlchemy metadata registry.
"""

from app.db.database import Base

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_session import UserSession
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.dataset_column import DatasetColumn
from app.models.dataset_upload import DatasetUpload
from app.models.analysis_job import AnalysisJob
from app.models.analysis_result import AnalysisResult
from app.models.dashboard import Dashboard
from app.models.dashboard_widget import DashboardWidget
from app.models.ai_conversation import AIConversation
from app.models.ai_message import AIMessage
from app.models.ai_recommendation import AIRecommendation
from app.models.forecast_model import ForecastModel
from app.models.forecast_result import ForecastResult
from app.models.report import Report
from app.models.report_export import ReportExport
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting
from app.models.record import Record
from app.models.threshold import Threshold
from app.models.email_token import EmailToken

__all__ = [
    "Base",
    "Organization",
    "User",
    "Role",
    "Permission",
    "UserRole",
    "UserSession",
    "Workspace",
    "WorkspaceMember",
    "Dataset",
    "DatasetVersion",
    "DatasetColumn",
    "DatasetUpload",
    "AnalysisJob",
    "AnalysisResult",
    "Dashboard",
    "DashboardWidget",
    "AIConversation",
    "AIMessage",
    "AIRecommendation",
    "ForecastModel",
    "ForecastResult",
    "Report",
    "ReportExport",
    "Notification",
    "AuditLog",
    "SystemSetting",
    "Record",
    "Threshold",
    "EmailToken",
]
