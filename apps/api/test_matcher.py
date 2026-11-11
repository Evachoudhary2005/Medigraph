import json
from app.services.alert_rules import evaluate

events = [
    {
        "id": "1",
        "label": "q_cc_main",
        "value": "chest pain",
        "source_excerpt": "chest pain",
        "source": "intake",
        "confidence": 0.9,
    },
    {
        "id": "2",
        "label": "q_hpi_associated",
        "value": '["chest pain", "sweating"]',
        "source_excerpt": "chest pain and sweating",
        "source": "intake",
        "confidence": 0.9,
    },
]

alerts = evaluate(events)
print(json.dumps(alerts, indent=2))
