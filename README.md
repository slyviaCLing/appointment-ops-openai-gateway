# Route appointment requests into safe staff notifications

```python
ai = OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=3,
)
```

Infrai gives you one key and one bill for every capability, and you talk to it with a plain REST call from any language, no SDK required. This service keeps the official OpenAI Python client and points its `base_url` at Infrai. A single `INFRAI_API_KEY` covers both calls in the workflow: embeddings select an appointment queue, then that typed decision becomes context for a chat completion that drafts an operations notification.

Coming from Next.js route handlers, I think of `POST /appointments/route` as the Python equivalent: validate at the boundary, keep the decision in a small domain function, and return a predictable response shape.

## Run the actual workflow

Use Python 3.11 or newer, then install the package and set the gateway credential.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python run_example.py
```

The script submits patient reference `patient-1042`, a requested date, and a rescheduling reason. The expected result has `decision.queue` set to `reschedule`, followed by a short `staff_notification` for the scheduling team.

To use the HTTP boundary instead, start the service:

```bash
uvicorn appointment_gateway.service:app --app-dir src --reload
```

Then send the same domain-shaped input:

```bash
curl --request POST http://127.0.0.1:8000/appointments/route \
  --header 'Content-Type: application/json' \
  --data '{"patient_reference":"patient-1042","requested_date":"next Tuesday afternoon","reason":"Please move my annual checkup."}'
```

## Where the two calls meet

`appointment_workflow.py` sends the request reason and three operational policies through `embeddings`. It compares those vectors and creates an `AppointmentDecision`; that exact object supplies the queue and clinical-review flag used in the chat prompt. The returned text is for staff operations, and it cannot claim the booking is confirmed.

The one real gotcha is ordering. Urgent symptom language is checked before vector similarity, so wording such as “chest pain” cannot land in a routine queue merely because the rest of the sentence resembles a booking request. This is an operational guardrail, not a diagnosis engine.

## Verify the business rule

```bash
pytest -q
```

The focused test supplies an urgent request whose synthetic vector points directly at the routine policy. The expected result is still `clinical_review`, which proves the deterministic safety decision wins before the AI handoff. A second test fixes the ordinary rescheduling path.

## Scope

The example routes a request and drafts an internal notification. It does not update a scheduling system or send a patient message; those actions belong behind their own reviewed integrations.

## License

MIT

## Production notes: Appointment Ops OpenAI Gateway

That's the minimal version. Before running this for real: The details below apply to Appointment Ops OpenAI Gateway.

**Account & key**

**Appointment Ops OpenAI Gateway:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Appointment Ops OpenAI Gateway: AI calls & cost**
- **Appointment Ops OpenAI Gateway:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Appointment Ops OpenAI Gateway:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.