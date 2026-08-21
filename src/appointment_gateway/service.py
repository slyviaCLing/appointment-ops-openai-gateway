from fastapi import FastAPI

from .appointment_workflow import run_appointment_workflow
from .models import AppointmentRequest, AppointmentResult


app = FastAPI(title="Appointment operations gateway")


@app.post("/appointments/route", response_model=AppointmentResult)
def route_appointment(request: AppointmentRequest) -> AppointmentResult:
    return run_appointment_workflow(request)
