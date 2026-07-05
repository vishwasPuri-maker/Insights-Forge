from typing import Optional
import datetime
import decimal
import enum
import uuid

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AiConversationStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'


class AiMessageSenderEnum(str, enum.Enum):
    USER = 'User'
    AI = 'AI'


class AiModelEnum(str, enum.Enum):
    GPT_4O = 'GPT-4o'
    GPT_4_1 = 'GPT-4.1'
    GPT_5 = 'GPT-5'
    CLAUDE = 'Claude'
    GEMINI = 'Gemini'
    LLAMA = 'Llama'
    CUSTOM = 'Custom'


class AiRecommendationPriorityEnum(str, enum.Enum):
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'


class AiRecommendationTypeEnum(str, enum.Enum):
    INSIGHT = 'Insight'
    OPTIMIZATION = 'Optimization'
    WARNING = 'Warning'
    OPPORTUNITY = 'Opportunity'
    FORECAST = 'Forecast'


class AnalysisJobStatusEnum(str, enum.Enum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    CANCELLED = 'Cancelled'


class AnalysisJobTypeEnum(str, enum.Enum):
    DESCRIPTIVE_ANALYSIS = 'Descriptive Analysis'
    DIAGNOSTIC_ANALYSIS = 'Diagnostic Analysis'
    PREDICTIVE_ANALYSIS = 'Predictive Analysis'
    PRESCRIPTIVE_ANALYSIS = 'Prescriptive Analysis'
    FORECASTING = 'Forecasting'
    ANOMALY_DETECTION = 'Anomaly Detection'


class AuditActionEnum(str, enum.Enum):
    CREATE = 'Create'
    UPDATE = 'Update'
    DELETE = 'Delete'
    LOGIN = 'Login'


class ChartTypeEnum(str, enum.Enum):
    BAR = 'Bar'
    LINE = 'Line'
    PIE = 'Pie'
    AREA = 'Area'
    SCATTER = 'Scatter'
    DONUT = 'Donut'
    HEATMAP = 'Heatmap'
    KPI = 'KPI'


class DashboardStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class DatasetProcessingStatusEnum(str, enum.Enum):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    COMPLETED = 'Completed'
    FAILED = 'Failed'


class DatasetStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'
    DELETED = 'Deleted'


class ExportFormatEnum(str, enum.Enum):
    PDF = 'PDF'
    XLSX = 'XLSX'
    CSV = 'CSV'


class ForecastAlgorithmEnum(str, enum.Enum):
    LINEAR_REGRESSION = 'Linear Regression'
    RANDOM_FOREST = 'Random Forest'
    XGBOOST = 'XGBoost'
    ARIMA = 'ARIMA'
    PROPHET = 'Prophet'
    LSTM = 'LSTM'


class ForecastModelStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class NotificationChannelEnum(str, enum.Enum):
    IN_APP = 'In-App'
    EMAIL = 'Email'
    SMS = 'SMS'


class NotificationStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'


class NotificationTypeEnum(str, enum.Enum):
    INFO = 'Info'
    WARNING = 'Warning'
    ERROR = 'Error'
    SUCCESS = 'Success'


class OrganizationStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    SUSPENDED = 'Suspended'


class ReportStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'


class ReportTypeEnum(str, enum.Enum):
    DASHBOARD = 'Dashboard'
    ANALYTICS = 'Analytics'
    FORECAST = 'Forecast'
    DATASET = 'Dataset'
    CUSTOM = 'Custom'


class SubscriptionPlanEnum(str, enum.Enum):
    FREE = 'Free'
    PRO = 'Pro'
    ENTERPRISE = 'Enterprise'


class UploadStatusEnum(str, enum.Enum):
    COMPLETED = 'Completed'
    PROCESSING = 'Processing'
    FAILED = 'Failed'


class UserStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    SUSPENDED = 'Suspended'


class VisualizationTypeEnum(str, enum.Enum):
    BAR = 'Bar'
    LINE = 'Line'
    PIE = 'Pie'
    SCATTER = 'Scatter'
    HISTOGRAM = 'Histogram'
    HEATMAP = 'Heatmap'
    KPI = 'KPI'
    TABLE = 'Table'


class WidgetStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class WidgetTypeEnum(str, enum.Enum):
    KPI = 'KPI'
    CHART = 'Chart'
    TABLE = 'Table'
    TEXT = 'Text'
    FILTER = 'Filter'


class WorkspaceStatusEnum(str, enum.Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_organizations'),
        UniqueConstraint('slug', name='uq_organizations_slug'),
        Index('ix_organizations_industry', 'industry'),
        Index('ix_organizations_status', 'status')
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    subscription_plan: Mapped[SubscriptionPlanEnum] = mapped_column(Enum(SubscriptionPlanEnum, values_callable=lambda cls: [member.value for member in cls], name='subscription_plan_enum'), nullable=False, server_default=text("'Free'::subscription_plan_enum"))
    status: Mapped[OrganizationStatusEnum] = mapped_column(Enum(OrganizationStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='organization_status_enum'), nullable=False, server_default=text("'Active'::organization_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    roles: Mapped[list['Roles']] = relationship('Roles', back_populates='organization')
    users: Mapped[list['Users']] = relationship('Users', back_populates='organization')
    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='organization')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='organization')
    system_settings: Mapped[list['SystemSettings']] = relationship('SystemSettings', back_populates='organization')
    workspaces: Mapped[list['Workspaces']] = relationship('Workspaces', back_populates='organization')
    ai_conversations: Mapped[list['AiConversations']] = relationship('AiConversations', back_populates='organization')
    dashboards: Mapped[list['Dashboards']] = relationship('Dashboards', back_populates='organization')
    datasets: Mapped[list['Datasets']] = relationship('Datasets', back_populates='organization')
    reports: Mapped[list['Reports']] = relationship('Reports', back_populates='organization')
    forecast_models: Mapped[list['ForecastModels']] = relationship('ForecastModels', back_populates='organization')
    ai_recommendations: Mapped[list['AiRecommendations']] = relationship('AiRecommendations', back_populates='organization')


class Permissions(Base):
    __tablename__ = 'permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_permissions'),
        UniqueConstraint('permission_name', name='uq_permissions_permission_name')
    )

    permission_name: Mapped[str] = mapped_column(String(100), nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_roles_organization_id_organizations'),
        PrimaryKeyConstraint('id', name='pk_roles'),
        UniqueConstraint('organization_id', 'name', name='uq_roles_organization_name'),
        Index('ix_roles_organization_id', 'organization_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='roles')
    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='role')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_users_organization_id_organizations'),
        PrimaryKeyConstraint('id', name='pk_users'),
        UniqueConstraint('email', name='uq_users_email'),
        Index('ix_users_organization_id', 'organization_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    status: Mapped[UserStatusEnum] = mapped_column(Enum(UserStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='user_status_enum'), nullable=False, server_default=text("'Active'::user_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    profile_image: Mapped[Optional[str]] = mapped_column(Text)

    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='users')
    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='user')
    notifications_created_by: Mapped[list['Notifications']] = relationship('Notifications', foreign_keys='[Notifications.created_by]', back_populates='users')
    notifications_updated_by: Mapped[list['Notifications']] = relationship('Notifications', foreign_keys='[Notifications.updated_by]', back_populates='users_')
    notifications_user: Mapped[list['Notifications']] = relationship('Notifications', foreign_keys='[Notifications.user_id]', back_populates='user')
    system_settings: Mapped[list['SystemSettings']] = relationship('SystemSettings', back_populates='users')
    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='user')
    user_sessions: Mapped[list['UserSessions']] = relationship('UserSessions', back_populates='user')
    workspaces_created_by: Mapped[list['Workspaces']] = relationship('Workspaces', foreign_keys='[Workspaces.created_by]', back_populates='users')
    workspaces_updated_by: Mapped[list['Workspaces']] = relationship('Workspaces', foreign_keys='[Workspaces.updated_by]', back_populates='users_')
    ai_conversations_created_by: Mapped[list['AiConversations']] = relationship('AiConversations', foreign_keys='[AiConversations.created_by]', back_populates='users')
    ai_conversations_updated_by: Mapped[list['AiConversations']] = relationship('AiConversations', foreign_keys='[AiConversations.updated_by]', back_populates='users_')
    ai_conversations_user: Mapped[list['AiConversations']] = relationship('AiConversations', foreign_keys='[AiConversations.user_id]', back_populates='user')
    dashboards_created_by: Mapped[list['Dashboards']] = relationship('Dashboards', foreign_keys='[Dashboards.created_by]', back_populates='users')
    dashboards_updated_by: Mapped[list['Dashboards']] = relationship('Dashboards', foreign_keys='[Dashboards.updated_by]', back_populates='users_')
    datasets_created_by: Mapped[list['Datasets']] = relationship('Datasets', foreign_keys='[Datasets.created_by]', back_populates='users')
    datasets_updated_by: Mapped[list['Datasets']] = relationship('Datasets', foreign_keys='[Datasets.updated_by]', back_populates='users_')
    datasets_uploaded_by: Mapped[list['Datasets']] = relationship('Datasets', foreign_keys='[Datasets.uploaded_by]', back_populates='users1')
    reports_created_by: Mapped[list['Reports']] = relationship('Reports', foreign_keys='[Reports.created_by]', back_populates='users')
    reports_updated_by: Mapped[list['Reports']] = relationship('Reports', foreign_keys='[Reports.updated_by]', back_populates='users_')
    workspace_members: Mapped[list['WorkspaceMembers']] = relationship('WorkspaceMembers', back_populates='user')
    analysis_jobs_created_by: Mapped[list['AnalysisJobs']] = relationship('AnalysisJobs', foreign_keys='[AnalysisJobs.created_by]', back_populates='users')
    analysis_jobs_initiated_by: Mapped[list['AnalysisJobs']] = relationship('AnalysisJobs', foreign_keys='[AnalysisJobs.initiated_by]', back_populates='users_')
    analysis_jobs_updated_by: Mapped[list['AnalysisJobs']] = relationship('AnalysisJobs', foreign_keys='[AnalysisJobs.updated_by]', back_populates='users1')
    dashboard_widgets_created_by: Mapped[list['DashboardWidgets']] = relationship('DashboardWidgets', foreign_keys='[DashboardWidgets.created_by]', back_populates='users')
    dashboard_widgets_updated_by: Mapped[list['DashboardWidgets']] = relationship('DashboardWidgets', foreign_keys='[DashboardWidgets.updated_by]', back_populates='users_')
    dataset_uploads: Mapped[list['DatasetUploads']] = relationship('DatasetUploads', back_populates='users')
    dataset_versions_created_by: Mapped[list['DatasetVersions']] = relationship('DatasetVersions', foreign_keys='[DatasetVersions.created_by]', back_populates='users')
    dataset_versions_updated_by: Mapped[list['DatasetVersions']] = relationship('DatasetVersions', foreign_keys='[DatasetVersions.updated_by]', back_populates='users_')
    forecast_models_created_by: Mapped[list['ForecastModels']] = relationship('ForecastModels', foreign_keys='[ForecastModels.created_by]', back_populates='users')
    forecast_models_updated_by: Mapped[list['ForecastModels']] = relationship('ForecastModels', foreign_keys='[ForecastModels.updated_by]', back_populates='users_')
    report_exports: Mapped[list['ReportExports']] = relationship('ReportExports', back_populates='users')
    ai_recommendations_created_by: Mapped[list['AiRecommendations']] = relationship('AiRecommendations', foreign_keys='[AiRecommendations.created_by]', back_populates='users')
    ai_recommendations_updated_by: Mapped[list['AiRecommendations']] = relationship('AiRecommendations', foreign_keys='[AiRecommendations.updated_by]', back_populates='users_')


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_audit_logs_organization_id_organizations'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_logs_user_id_users'),
        PrimaryKeyConstraint('id', name='pk_audit_logs'),
        Index('ix_audit_logs_organization_id', 'organization_id'),
        Index('ix_audit_logs_user_id', 'user_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[AuditActionEnum] = mapped_column(Enum(AuditActionEnum, values_callable=lambda cls: [member.value for member in cls], name='audit_action_enum'), nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='audit_logs')
    user: Mapped['Users'] = relationship('Users', back_populates='audit_logs')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_notifications_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_notifications_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_notifications_updated_by_users'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_notifications_user_id_users'),
        PrimaryKeyConstraint('id', name='pk_notifications'),
        Index('ix_notifications_organization_id', 'organization_id'),
        Index('ix_notifications_user_id', 'user_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[NotificationTypeEnum] = mapped_column(Enum(NotificationTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='notification_type_enum'), nullable=False)
    delivery_channel: Mapped[NotificationChannelEnum] = mapped_column(Enum(NotificationChannelEnum, values_callable=lambda cls: [member.value for member in cls], name='notification_channel_enum'), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    status: Mapped[NotificationStatusEnum] = mapped_column(Enum(NotificationStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='notification_status_enum'), nullable=False, server_default=text("'Active'::notification_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='notifications_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='notifications')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='notifications_updated_by')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='notifications_user')


class SystemSettings(Base):
    __tablename__ = 'system_settings'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_system_settings_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_system_settings_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_system_settings'),
        Index('ix_system_settings_organization_id', 'organization_id'),
        Index('ix_system_settings_updated_by', 'updated_by')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    setting_key: Mapped[str] = mapped_column(String(100), nullable=False)
    setting_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='system_settings')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='system_settings')


class UserRoles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_user_roles_role_id_roles'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_roles_user_id_users'),
        PrimaryKeyConstraint('id', name='pk_user_roles'),
        UniqueConstraint('user_id', 'role_id', name='uq_user_roles_user_role'),
        Index('ix_user_roles_role_id', 'role_id'),
        Index('ix_user_roles_user_id', 'user_id')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    role: Mapped['Roles'] = relationship('Roles', back_populates='user_roles')
    user: Mapped['Users'] = relationship('Users', back_populates='user_roles')


class UserSessions(Base):
    __tablename__ = 'user_sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_sessions_user_id_users'),
        PrimaryKeyConstraint('id', name='pk_user_sessions'),
        Index('ix_user_sessions_user_id', 'user_id')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    user: Mapped['Users'] = relationship('Users', back_populates='user_sessions')


class Workspaces(Base):
    __tablename__ = 'workspaces'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_workspaces_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_workspaces_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_workspaces_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_workspaces'),
        Index('ix_workspaces_organization_id', 'organization_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[WorkspaceStatusEnum] = mapped_column(Enum(WorkspaceStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='workspace_status_enum'), nullable=False, server_default=text("'Active'::workspace_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='workspaces_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='workspaces')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='workspaces_updated_by')
    ai_conversations: Mapped[list['AiConversations']] = relationship('AiConversations', back_populates='workspace')
    dashboards: Mapped[list['Dashboards']] = relationship('Dashboards', back_populates='workspace')
    datasets: Mapped[list['Datasets']] = relationship('Datasets', back_populates='workspace')
    reports: Mapped[list['Reports']] = relationship('Reports', back_populates='workspace')
    workspace_members: Mapped[list['WorkspaceMembers']] = relationship('WorkspaceMembers', back_populates='workspace')


class AiConversations(Base):
    __tablename__ = 'ai_conversations'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_ai_conversations_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_ai_conversations_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_ai_conversations_updated_by_users'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_ai_conversations_user_id_users'),
        ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_ai_conversations_workspace_id_workspaces'),
        PrimaryKeyConstraint('id', name='pk_ai_conversations'),
        Index('ix_ai_conversations_organization_id', 'organization_id'),
        Index('ix_ai_conversations_user_id', 'user_id'),
        Index('ix_ai_conversations_workspace_id', 'workspace_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[AiModelEnum] = mapped_column(Enum(AiModelEnum, values_callable=lambda cls: [member.value for member in cls], name='ai_model_enum'), nullable=False)
    status: Mapped[AiConversationStatusEnum] = mapped_column(Enum(AiConversationStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='ai_conversation_status_enum'), nullable=False, server_default=text("'Active'::ai_conversation_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='ai_conversations_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='ai_conversations')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='ai_conversations_updated_by')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='ai_conversations_user')
    workspace: Mapped['Workspaces'] = relationship('Workspaces', back_populates='ai_conversations')
    ai_messages: Mapped[list['AiMessages']] = relationship('AiMessages', back_populates='conversation')


class Dashboards(Base):
    __tablename__ = 'dashboards'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_dashboards_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_dashboards_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_dashboards_updated_by_users'),
        ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_dashboards_workspace_id_workspaces'),
        PrimaryKeyConstraint('id', name='pk_dashboards'),
        Index('ix_dashboards_organization_id', 'organization_id'),
        Index('ix_dashboards_workspace_id', 'workspace_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    layout: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    status: Mapped[DashboardStatusEnum] = mapped_column(Enum(DashboardStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='dashboard_status_enum'), nullable=False, server_default=text("'Active'::dashboard_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='dashboards_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='dashboards')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='dashboards_updated_by')
    workspace: Mapped['Workspaces'] = relationship('Workspaces', back_populates='dashboards')
    dashboard_widgets: Mapped[list['DashboardWidgets']] = relationship('DashboardWidgets', back_populates='dashboard')


class Datasets(Base):
    __tablename__ = 'datasets'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_datasets_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_datasets_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_datasets_updated_by_users'),
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='fk_datasets_uploaded_by_users'),
        ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_datasets_workspace_id_workspaces'),
        PrimaryKeyConstraint('id', name='pk_datasets'),
        Index('ix_datasets_organization_id', 'organization_id'),
        Index('ix_datasets_uploaded_by', 'uploaded_by'),
        Index('ix_datasets_workspace_id', 'workspace_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'Neon Storage'::character varying"))
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_columns: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    processing_status: Mapped[DatasetProcessingStatusEnum] = mapped_column(Enum(DatasetProcessingStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='dataset_processing_status_enum'), nullable=False, server_default=text("'Pending'::dataset_processing_status_enum"))
    status: Mapped[DatasetStatusEnum] = mapped_column(Enum(DatasetStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='dataset_status_enum'), nullable=False, server_default=text("'Active'::dataset_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    checksum: Mapped[Optional[str]] = mapped_column(String(255))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='datasets_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='datasets')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='datasets_updated_by')
    users1: Mapped['Users'] = relationship('Users', foreign_keys=[uploaded_by], back_populates='datasets_uploaded_by')
    workspace: Mapped['Workspaces'] = relationship('Workspaces', back_populates='datasets')
    analysis_jobs: Mapped[list['AnalysisJobs']] = relationship('AnalysisJobs', back_populates='dataset')
    dataset_columns: Mapped[list['DatasetColumns']] = relationship('DatasetColumns', back_populates='dataset')
    dataset_uploads: Mapped[list['DatasetUploads']] = relationship('DatasetUploads', back_populates='dataset')
    dataset_versions: Mapped[list['DatasetVersions']] = relationship('DatasetVersions', back_populates='dataset')
    forecast_models: Mapped[list['ForecastModels']] = relationship('ForecastModels', back_populates='dataset')
    analysis_results: Mapped[list['AnalysisResults']] = relationship('AnalysisResults', back_populates='dataset')
    ai_recommendations: Mapped[list['AiRecommendations']] = relationship('AiRecommendations', back_populates='dataset')


class Reports(Base):
    __tablename__ = 'reports'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_reports_created_by_users'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_reports_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_reports_updated_by_users'),
        ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_reports_workspace_id_workspaces'),
        PrimaryKeyConstraint('id', name='pk_reports'),
        Index('ix_reports_organization_id', 'organization_id'),
        Index('ix_reports_workspace_id', 'workspace_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    report_name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[ReportTypeEnum] = mapped_column(Enum(ReportTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='report_type_enum'), nullable=False)
    report_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[ReportStatusEnum] = mapped_column(Enum(ReportStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='report_status_enum'), nullable=False, server_default=text("'Active'::report_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='reports_created_by')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='reports')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='reports_updated_by')
    workspace: Mapped['Workspaces'] = relationship('Workspaces', back_populates='reports')
    report_exports: Mapped[list['ReportExports']] = relationship('ReportExports', back_populates='report')


class WorkspaceMembers(Base):
    __tablename__ = 'workspace_members'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_workspace_members_user_id_users'),
        ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_workspace_members_workspace_id_workspaces'),
        PrimaryKeyConstraint('id', name='pk_workspace_members'),
        UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_member'),
        Index('ix_workspace_members_user_id', 'user_id'),
        Index('ix_workspace_members_workspace_id', 'workspace_id')
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_role: Mapped[str] = mapped_column(String(50), nullable=False)
    joined_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    user: Mapped['Users'] = relationship('Users', back_populates='workspace_members')
    workspace: Mapped['Workspaces'] = relationship('Workspaces', back_populates='workspace_members')


class AiMessages(Base):
    __tablename__ = 'ai_messages'
    __table_args__ = (
        ForeignKeyConstraint(['conversation_id'], ['ai_conversations.id'], name='fk_ai_messages_conversation_id_ai_conversations'),
        PrimaryKeyConstraint('id', name='pk_ai_messages'),
        Index('ix_ai_messages_conversation_id', 'conversation_id')
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    sender_type: Mapped[AiMessageSenderEnum] = mapped_column(Enum(AiMessageSenderEnum, values_callable=lambda cls: [member.value for member in cls], name='ai_message_sender_enum'), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    conversation: Mapped['AiConversations'] = relationship('AiConversations', back_populates='ai_messages')


class AnalysisJobs(Base):
    __tablename__ = 'analysis_jobs'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_analysis_jobs_created_by_users'),
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_analysis_jobs_dataset_id_datasets'),
        ForeignKeyConstraint(['initiated_by'], ['users.id'], name='fk_analysis_jobs_initiated_by_users'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_analysis_jobs_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_analysis_jobs'),
        Index('ix_analysis_jobs_dataset_id', 'dataset_id'),
        Index('ix_analysis_jobs_initiated_by', 'initiated_by')
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    initiated_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    job_type: Mapped[AnalysisJobTypeEnum] = mapped_column(Enum(AnalysisJobTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='analysis_job_type_enum'), nullable=False)
    status: Mapped[AnalysisJobStatusEnum] = mapped_column(Enum(AnalysisJobStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='analysis_job_status_enum'), nullable=False, server_default=text("'Pending'::analysis_job_status_enum"))
    progress: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='analysis_jobs_created_by')
    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='analysis_jobs')
    users_: Mapped['Users'] = relationship('Users', foreign_keys=[initiated_by], back_populates='analysis_jobs_initiated_by')
    users1: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='analysis_jobs_updated_by')
    analysis_results: Mapped[list['AnalysisResults']] = relationship('AnalysisResults', back_populates='job')


class DashboardWidgets(Base):
    __tablename__ = 'dashboard_widgets'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_dashboard_widgets_created_by_users'),
        ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], name='fk_dashboard_widgets_dashboard_id_dashboards'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_dashboard_widgets_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_dashboard_widgets'),
        Index('ix_dashboard_widgets_dashboard_id', 'dashboard_id')
    )

    dashboard_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    widget_type: Mapped[WidgetTypeEnum] = mapped_column(Enum(WidgetTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='widget_type_enum'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chart_type: Mapped[ChartTypeEnum] = mapped_column(Enum(ChartTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='chart_type_enum'), nullable=False)
    data_source: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[WidgetStatusEnum] = mapped_column(Enum(WidgetStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='widget_status_enum'), nullable=False, server_default=text("'Active'::widget_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    settings: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='dashboard_widgets_created_by')
    dashboard: Mapped['Dashboards'] = relationship('Dashboards', back_populates='dashboard_widgets')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='dashboard_widgets_updated_by')


class DatasetColumns(Base):
    __tablename__ = 'dataset_columns'
    __table_args__ = (
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_dataset_columns_dataset_id_datasets'),
        PrimaryKeyConstraint('id', name='pk_dataset_columns'),
        Index('ix_dataset_columns_dataset_id', 'dataset_id')
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    nullable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    unique_values: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    missing_values: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='dataset_columns')


class DatasetUploads(Base):
    __tablename__ = 'dataset_uploads'
    __table_args__ = (
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_dataset_uploads_dataset_id_datasets'),
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='fk_dataset_uploads_uploaded_by_users'),
        PrimaryKeyConstraint('id', name='pk_dataset_uploads'),
        Index('ix_dataset_uploads_dataset_id', 'dataset_id'),
        Index('ix_dataset_uploads_uploaded_by', 'uploaded_by')
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    upload_status: Mapped[UploadStatusEnum] = mapped_column(Enum(UploadStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='upload_status_enum'), nullable=False, server_default=text("'Completed'::upload_status_enum"))
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='dataset_uploads')
    users: Mapped['Users'] = relationship('Users', back_populates='dataset_uploads')


class DatasetVersions(Base):
    __tablename__ = 'dataset_versions'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_dataset_versions_created_by_users'),
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_dataset_versions_dataset_id_datasets'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_dataset_versions_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_dataset_versions'),
        UniqueConstraint('dataset_id', 'version', name='uq_dataset_version'),
        Index('ix_dataset_versions_dataset_id', 'dataset_id')
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    change_summary: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='dataset_versions_created_by')
    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='dataset_versions')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='dataset_versions_updated_by')


class ForecastModels(Base):
    __tablename__ = 'forecast_models'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_forecast_models_created_by_users'),
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_forecast_models_dataset_id_datasets'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_forecast_models_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_forecast_models_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_forecast_models'),
        Index('ix_forecast_models_dataset_id', 'dataset_id'),
        Index('ix_forecast_models_organization_id', 'organization_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm: Mapped[ForecastAlgorithmEnum] = mapped_column(Enum(ForecastAlgorithmEnum, values_callable=lambda cls: [member.value for member in cls], name='forecast_algorithm_enum'), nullable=False)
    target_column: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ForecastModelStatusEnum] = mapped_column(Enum(ForecastModelStatusEnum, values_callable=lambda cls: [member.value for member in cls], name='forecast_model_status_enum'), nullable=False, server_default=text("'Active'::forecast_model_status_enum"))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    accuracy: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='forecast_models_created_by')
    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='forecast_models')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='forecast_models')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='forecast_models_updated_by')
    forecast_results: Mapped[list['ForecastResults']] = relationship('ForecastResults', back_populates='forecast_model')


class ReportExports(Base):
    __tablename__ = 'report_exports'
    __table_args__ = (
        ForeignKeyConstraint(['exported_by'], ['users.id'], name='fk_report_exports_exported_by_users'),
        ForeignKeyConstraint(['report_id'], ['reports.id'], name='fk_report_exports_report_id_reports'),
        PrimaryKeyConstraint('id', name='pk_report_exports'),
        Index('ix_report_exports_exported_by', 'exported_by'),
        Index('ix_report_exports_report_id', 'report_id')
    )

    report_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    exported_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    export_format: Mapped[ExportFormatEnum] = mapped_column(Enum(ExportFormatEnum, values_callable=lambda cls: [member.value for member in cls], name='export_format_enum'), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)

    users: Mapped['Users'] = relationship('Users', back_populates='report_exports')
    report: Mapped['Reports'] = relationship('Reports', back_populates='report_exports')


class AnalysisResults(Base):
    __tablename__ = 'analysis_results'
    __table_args__ = (
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_analysis_results_dataset_id_datasets'),
        ForeignKeyConstraint(['job_id'], ['analysis_jobs.id'], name='fk_analysis_results_job_id_analysis_jobs'),
        PrimaryKeyConstraint('id', name='pk_analysis_results'),
        Index('ix_analysis_results_dataset_id', 'dataset_id'),
        Index('ix_analysis_results_job_id', 'job_id')
    )

    job_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    visualization_type: Mapped[Optional[VisualizationTypeEnum]] = mapped_column(Enum(VisualizationTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='visualization_type_enum'))

    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='analysis_results')
    job: Mapped['AnalysisJobs'] = relationship('AnalysisJobs', back_populates='analysis_results')
    ai_recommendations: Mapped[list['AiRecommendations']] = relationship('AiRecommendations', back_populates='analytics_result')


class ForecastResults(Base):
    __tablename__ = 'forecast_results'
    __table_args__ = (
        ForeignKeyConstraint(['forecast_model_id'], ['forecast_models.id'], name='fk_forecast_results_forecast_model_id_forecast_models'),
        PrimaryKeyConstraint('id', name='pk_forecast_results'),
        Index('ix_forecast_results_forecast_model_id', 'forecast_model_id')
    )

    forecast_model_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    prediction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    predicted_value: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    confidence_interval: Mapped[Optional[dict]] = mapped_column(JSONB)
    actual_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 4))

    forecast_model: Mapped['ForecastModels'] = relationship('ForecastModels', back_populates='forecast_results')


class AiRecommendations(Base):
    __tablename__ = 'ai_recommendations'
    __table_args__ = (
        ForeignKeyConstraint(['analytics_result_id'], ['analysis_results.id'], name='fk_ai_recommendations_analytics_result_id_analysis_results'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_ai_recommendations_created_by_users'),
        ForeignKeyConstraint(['dataset_id'], ['datasets.id'], name='fk_ai_recommendations_dataset_id_datasets'),
        ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_ai_recommendations_organization_id_organizations'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_ai_recommendations_updated_by_users'),
        PrimaryKeyConstraint('id', name='pk_ai_recommendations'),
        Index('ix_ai_recommendations_analytics_result_id', 'analytics_result_id'),
        Index('ix_ai_recommendations_dataset_id', 'dataset_id'),
        Index('ix_ai_recommendations_organization_id', 'organization_id')
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    analytics_result_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recommendation_type: Mapped[AiRecommendationTypeEnum] = mapped_column(Enum(AiRecommendationTypeEnum, values_callable=lambda cls: [member.value for member in cls], name='ai_recommendation_type_enum'), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority: Mapped[AiRecommendationPriorityEnum] = mapped_column(Enum(AiRecommendationPriorityEnum, values_callable=lambda cls: [member.value for member in cls], name='ai_recommendation_priority_enum'), nullable=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    analytics_result: Mapped['AnalysisResults'] = relationship('AnalysisResults', back_populates='ai_recommendations')
    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='ai_recommendations_created_by')
    dataset: Mapped['Datasets'] = relationship('Datasets', back_populates='ai_recommendations')
    organization: Mapped['Organizations'] = relationship('Organizations', back_populates='ai_recommendations')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='ai_recommendations_updated_by')
