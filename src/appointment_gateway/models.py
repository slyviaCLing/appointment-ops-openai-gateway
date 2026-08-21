from typing import Literal

from pydantic import BaseModel, Field


class AppointmentRequest(BaseModel):
    patient_reference: str = Field(min_length=1, max_length=80)
    requested_date: str = Field(min_length=1, max_length=40)
    reason: str = Field(min_length=3, max_length=500)


class AppointmentDecision(BaseModel):
    queue: Literal["routine_booking", "reschedule", "cancellation", "clinical_review"]
    requires_clinical_review: bool
    matched_policy: str


class AppointmentResult(BaseModel):
    patient_reference: str
    decision: AppointmentDecision
    staff_notification: str
