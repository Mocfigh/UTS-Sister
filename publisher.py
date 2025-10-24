import requests
import time
import random
import uuid

AGGREGATOR_URL = "http://127.0.0.1:8080"  # sesuaikan kalau beda host
TOTAL_EVENTS = 5000
BATCH_SIZE = 50
DUPLICATION_RATE = 0.2
SLEEP_TIME = 0.05

def generate_event(i):
    topic = f"topic.{i % 10}"  # 10 topic berbeda
    event_id = str(uuid.uuid4())
    payload = {"value": random.randint(1, 100)}
    return {
        "topic": topic,
        "event_id": event_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "publisher_5000",
        "payload": payload
    }

# buat beberapa duplikat awal
events_pool = [generate_event(i) for i in range(int(TOTAL_EVENTS*(1-DUPLICATION_RATE)))]
duplicates = random.choices(events_pool, k=int(TOTAL_EVENTS*DUPLICATION_RATE))
all_events = events_pool + duplicates
random.shuffle(all_events)

sent_count = 0
print(f"Starting event publisher...\nSending {TOTAL_EVENTS} events with {DUPLICATION_RATE*100}% duplication rate...")

for i in range(0, TOTAL_EVENTS, BATCH_SIZE):
    batch = all_events[i:i+BATCH_SIZE]
    for event in batch:
        try:
            r = requests.post(f"{AGGREGATOR_URL}/publish", json=event, timeout=5)
            if r.status_code != 200:
                print(f"Error sending event: {r.status_code} {r.text}")
        except Exception as e:
            print(f"Error sending event: {e}")
        sent_count += 1
    print(f"Sent {sent_count}/{TOTAL_EVENTS} events")
    time.sleep(0.05)  # jeda sebentar tiap batch supaya server gak kelebihan

print("\nCompleted! Sent all events.")
