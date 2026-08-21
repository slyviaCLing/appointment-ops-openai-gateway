from appointment_gateway.appointment_workflow import decide_appointment
from appointment_gateway.models import AppointmentRequest


def test_urgent_language_routes_to_clinical_review_before_similarity() -> None:
    request = AppointmentRequest(
        patient_reference="patient-urgent",
        requested_date="tomorrow",
        reason="I have chest pain and want a routine appointment.",
    )

    decision = decide_appointment(
        request,
        request_embedding=[1.0, 0.0],
        policy_embeddings=[[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]],
    )

    assert decision.queue == "clinical_review"
    assert decision.requires_clinical_review is True


def test_similarity_hands_reschedule_request_to_reschedule_queue() -> None:
    request = AppointmentRequest(
        patient_reference="patient-1042",
        requested_date="next Tuesday afternoon",
        reason="Please move my annual checkup.",
    )

    decision = decide_appointment(
        request,
        request_embedding=[0.0, 1.0],
        policy_embeddings=[[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]],
    )

    assert decision.queue == "reschedule"
    assert decision.requires_clinical_review is False
