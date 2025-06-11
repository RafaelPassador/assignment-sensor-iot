from prometheus_client import Counter, Gauge, start_http_server
import logging

# Métricas do Producer
messages_produced = Counter('sensor_messages_produced_total', 'Total de mensagens produzidas')
producer_failures = Counter('sensor_producer_failures_total', 'Total de falhas na produção')
messages_produced_per_minute = Gauge('sensor_messages_produced_per_minute', 'Mensagens produzidas por minuto')

# Métricas do Consumer
messages_consumed = Counter('sensor_messages_consumed_total', 'Total de mensagens consumidas')
consumer_failures = Counter('sensor_consumer_failures_total', 'Total de falhas no consumo')
messages_consumed_per_minute = Gauge('sensor_messages_consumed_per_minute', 'Mensagens consumidas por minuto')
validation_failures = Counter('sensor_validation_failures_total', 'Total de falhas na validação')

def start_metrics_server(port=8000):
    """Inicia o servidor de métricas do Prometheus."""
    try:
        start_http_server(port)
        logging.info(f"Servidor de métricas iniciado na porta {port}")
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor de métricas: {e}")
