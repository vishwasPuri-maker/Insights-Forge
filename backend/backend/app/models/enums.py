from enum import Enum


class OrganizationStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class SubscriptionPlan(str, Enum):
    FREE = "Free"
    PRO = "Pro"
    ENTERPRISE = "Enterprise"


class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class WorkspaceStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Sector(str, Enum):
    """Business sector a workspace represents. Values are exposed directly in
    the frozen API contract (e.g. /api/v1/sectors/{sector}/...)."""

    RETAIL = "retail"
    SERVICE = "service"
    EDUCATION = "education"
    AGRICULTURE = "agriculture"


class DatasetProcessingStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class UploadStatus(str, Enum):
    COMPLETED = "Completed"
    PROCESSING = "Processing"
    FAILED = "Failed"


class DatasetStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"
    DELETED = "Deleted"


# ------------------------------------------------------------------
# Analytics Enums
# ------------------------------------------------------------------


class AnalysisJobStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class AnalysisJobType(str, Enum):
    DESCRIPTIVE = "Descriptive Analysis"
    DIAGNOSTIC = "Diagnostic Analysis"
    PREDICTIVE = "Predictive Analysis"
    PRESCRIPTIVE = "Prescriptive Analysis"
    FORECASTING = "Forecasting"
    ANOMALY_DETECTION = "Anomaly Detection"


class VisualizationType(str, Enum):
    BAR = "Bar"
    LINE = "Line"
    PIE = "Pie"
    SCATTER = "Scatter"
    HISTOGRAM = "Histogram"
    HEATMAP = "Heatmap"
    KPI = "KPI"
    TABLE = "Table"


class DashboardStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class WidgetStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class WidgetType(str, Enum):
    KPI = "KPI"
    CHART = "Chart"
    TABLE = "Table"
    TEXT = "Text"
    FILTER = "Filter"


class ChartType(str, Enum):
    BAR = "Bar"
    LINE = "Line"
    PIE = "Pie"
    AREA = "Area"
    SCATTER = "Scatter"
    DONUT = "Donut"
    HEATMAP = "Heatmap"
    KPI = "KPI"


class AIConversationStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"


class AIMessageSender(str, Enum):
    USER = "User"
    AI = "AI"


class AIRecommendationType(str, Enum):
    INSIGHT = "Insight"
    OPTIMIZATION = "Optimization"
    WARNING = "Warning"
    OPPORTUNITY = "Opportunity"
    FORECAST = "Forecast"


class AIRecommendationPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DecisionStatus(str, Enum):
    """Decision-card lifecycle (contract exposes these lowercase values)."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmailTokenType(str, Enum):
    """Purpose of a one-time email token."""

    VERIFY_EMAIL = "verify_email"
    PASSWORD_RESET = "password_reset"


class AIModel(str, Enum):
    GPT_4O = "GPT-4o"
    GPT_4_1 = "GPT-4.1"
    GPT_5 = "GPT-5"
    CLAUDE = "Claude"
    GEMINI = "Gemini"
    LLAMA = "Llama"
    CUSTOM = "Custom"


# ------------------------------------------------------------------
# Forecasting Enums
# ------------------------------------------------------------------


class ForecastModelStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ForecastAlgorithm(str, Enum):
    LINEAR_REGRESSION = "Linear Regression"
    RANDOM_FOREST = "Random Forest"
    XGBOOST = "XGBoost"
    ARIMA = "ARIMA"
    PROPHET = "Prophet"
    LSTM = "LSTM"


# ------------------------------------------------------------------
# Reporting Enums
# ------------------------------------------------------------------


class ReportType(str, Enum):
    DASHBOARD = "Dashboard"
    ANALYTICS = "Analytics"
    FORECAST = "Forecast"
    DATASET = "Dataset"
    CUSTOM = "Custom"


class ExportFormat(str, Enum):
    PDF = "PDF"
    XLSX = "XLSX"
    CSV = "CSV"


class ReportStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"


# ------------------------------------------------------------------
# Notification Enums
# ------------------------------------------------------------------


class NotificationType(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    SUCCESS = "Success"


class NotificationChannel(str, Enum):
    IN_APP = "In-App"
    EMAIL = "Email"
    SMS = "SMS"


class NotificationStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"


# ------------------------------------------------------------------
# System Enums
# ------------------------------------------------------------------


class AuditAction(str, Enum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    LOGIN = "Login"


class SettingDataType(str, Enum):
    STRING = "String"
    NUMBER = "Number"
    BOOLEAN = "Boolean"
    JSON = "JSON"
