# app/schemas/violation_type.py
from typing import List, Optional

from pydantic import BaseModel, Field


class ViolationTypeBase(BaseModel):
    label_name: str = Field(
        ..., min_length=1, max_length=100,
        examples=["no_helmet"],
        description="Label YOLO untuk jenis pelanggaran"
    )
    penalty_score: int = Field(..., ge=0, examples=[3], description="Skor penalti (0+)")


class ViolationTypeCreate(ViolationTypeBase):
    pass


class ViolationTypeUpdate(BaseModel):
    label_name: Optional[str] = Field(None, min_length=1, max_length=100)
    penalty_score: Optional[int] = Field(None, ge=0)


class ViolationTypeRead(ViolationTypeBase):
    id: int

    model_config = {"from_attributes": True}


class ViolationTypeList(BaseModel):
    total: int
    items: List[ViolationTypeRead]
