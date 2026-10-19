"""
`column_metric` ORM 模型
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ColumnMetricMySQL(Base):
    """
    `column_metric` ORM 模型
    """

    __tablename__ = "column_metric"

    column_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, comment="列编号"
    )
    metric_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, comment="指标编号"
    )
