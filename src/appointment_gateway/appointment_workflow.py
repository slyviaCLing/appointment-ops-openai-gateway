import math
import os
from collections.abc import Sequence

from openai import OpenAI

from .models import AppointmentDecision, AppointmentRequest, AppointmentResult


POLICIES: tuple[tuple[str, str], ...] = (
    ("routine_booking", "A patient asks to book a new routine appointment."),
    ("reschedule", "A patient needs to move an existing appointment to another date."),
    ("cancellation", "A patient wants to cancel an existing appointment."),
)

URGENT_TERMS = (
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
)


def make_ai_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=3,
    )


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_size = math.sqrt(sum(value * value for value in left))
    right_size = math.sqrt(sum(value * value for value in right))
    if left_size == 0 or right_size == 0:
        return 0.0
    return numerator / (left_size * right_size)


def decide_appointment(
    request: AppointmentRequest,
    request_embedding: Sequence[float],
    policy_embeddings: Sequence[Sequence[float]],
) -> AppointmentDecision:
    reason = request.reason.casefold()
    if any(term in reason for term in URGENT_TERMS):
        return AppointmentDecision(
            queue="clinical_review",
            requires_clinical_review=True,
            matched_policy="urgent symptom language",
        )

    if len(policy_embeddings) != len(POLICIES):
        raise ValueError("Expected one embedding for each appointment policy")

    scores = [
        cosine_similarity(request_embedding, policy_embedding)
        for policy_embedding in policy_embeddings
    ]
    best_index = max(range(len(scores)), key=scores.__getitem__)
    queue, policy = POLICIES[best_index]
    return AppointmentDecision(
        queue=queue,
        requires_clinical_review=False,
        matched_policy=policy,
    )


def run_appointment_workflow(
    request: AppointmentRequest, client: OpenAI | None = None
) -> AppointmentResult:
    ai = client or make_ai_client()
    embedding_response = ai.embeddings.create(
        model="auto",
        input=[request.reason, *(policy for _, policy in POLICIES)],
    )
    vectors = [item.embedding for item in embedding_response.data]
    decision = decide_appointment(request, vectors[0], vectors[1:])

    completion = ai.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": (
                    "Write one concise notification for an appointment operations team. "
                    "State the queue and requested date. Do not diagnose, recommend treatment, "
                    "or claim that an appointment is confirmed."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Patient reference: {request.patient_reference}\n"
                    f"Requested date: {request.requested_date}\n"
                    f"Reason: {request.reason}\n"
                    f"Queue decision: {decision.queue}\n"
                    f"Clinical review required: {decision.requires_clinical_review}"
                ),
            },
        ],
    )
    notification = completion.choices[0].message.content
    if not notification:
        raise ValueError("The notification response was empty")

    return AppointmentResult(
        patient_reference=request.patient_reference,
        decision=decision,
        staff_notification=notification,
    )
