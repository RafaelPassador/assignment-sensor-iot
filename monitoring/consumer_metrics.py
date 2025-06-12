from prometheus_client import Counter, Gauge, start_http_server
import logging

# Métricas específicas do Consumer
messages_consumed = Counter('sensor_messages_consumed_total', 'Total de mensagens consumidas')
consumer_failures = Counter('sensor_consumer_failures_total', 'Total de falhas no consumo')
messages_consumed_per_minute = Gauge('sensor_messages_consumed_per_minute', 'Mensagens consumidas por minuto')
validation_failures = Counter('sensor_validation_failures_total', 'Total de falhas na validação')

def start_consumer_metrics_server(port=8001):
    """Inicia o servidor de métricas do Consumer."""
    try:
        start_http_server(port)
        logging.info(f"Servidor de métricas do consumer iniciado na porta {port}")
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor de métricas do consumer: {e}")
