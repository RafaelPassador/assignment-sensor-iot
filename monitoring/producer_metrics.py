from prometheus_client import Counter, Gauge, start_http_server
import logging

# Métricas específicas do Producer
messages_produced = Counter('sensor_messages_produced_total', 'Total de mensagens produzidas')
producer_failures = Counter('sensor_producer_failures_total', 'Total de falhas na produção')
messages_produced_per_minute = Gauge('sensor_messages_produced_per_minute', 'Mensagens produzidas por minuto')

def start_producer_metrics_server(port=8000):
    """Inicia o servidor de métricas do Producer."""
    try:
        start_http_server(port)
        logging.info(f"Servidor de métricas do producer iniciado na porta {port}")
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor de métricas do producer: {e}")
