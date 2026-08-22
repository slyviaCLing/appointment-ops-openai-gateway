from dataclasses import dataclass
from typing import Literal

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    BaseModel = None


Queue = Literal["routine_booking", "reschedule", "cancellation", "clinical_review"]


if BaseModel is not None:

    class AppointmentRequest(BaseModel):
        patient_reference: str = Field(min_length=1, max_length=80)
        requested_date: str = Field(min_length=1, max_length=40)
        reason: str = Field(min_length=3, max_length=500)


    class AppointmentDecision(BaseModel):
        queue: Queue
        requires_clinical_review: bool
        matched_policy: str


    class AppointmentResult(BaseModel):
        patient_reference: str
        decision: AppointmentDecision
        staff_notification: str

else:

    def _validate_length(name: str, value: str, minimum: int, maximum: int) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        if not minimum <= len(value) <= maximum:
            raise ValueError(
                f"{name} must contain between {minimum} and {maximum} characters"
            )


    @dataclass(frozen=True)
    class AppointmentRequest:
        patient_reference: str
        requested_date: str
        reason: str

        def __post_init__(self) -> None:
            _validate_length("patient_reference", self.patient_reference, 1, 80)
            _validate_length("requested_date", self.requested_date, 1, 40)
            _validate_length("reason", self.reason, 3, 500)


    @dataclass(frozen=True)
    class AppointmentDecision:
        queue: Queue
        requires_clinical_review: bool
        matched_policy: str


    @dataclass(frozen=True)
    class AppointmentResult:
        patient_reference: str
        decision: AppointmentDecision
        staff_notification: str
