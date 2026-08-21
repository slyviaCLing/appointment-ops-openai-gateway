from appointment_gateway.appointment_workflow import run_appointment_workflow
from appointment_gateway.models import AppointmentRequest


def main() -> None:
    result = run_appointment_workflow(
        AppointmentRequest(
            patient_reference="patient-1042",
            requested_date="next Tuesday afternoon",
            reason="I need to move my annual checkup to a later date.",
        )
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
