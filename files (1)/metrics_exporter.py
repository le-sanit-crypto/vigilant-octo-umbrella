from prometheus_client import start_http_server, Summary, Counter

event_counter = Counter('event_total', 'Total events processed')
duration = Summary('event_processing_seconds', 'Time spent processing events')

def process_event(event):
    with duration.time():
        event_counter.inc()
        # Do work
        pass

def start_exporter(port=8000):
    start_http_server(port)