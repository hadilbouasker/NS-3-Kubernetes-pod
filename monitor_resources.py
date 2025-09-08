import requests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import argparse

def query_prometheus(prometheus_url, query):
    response = requests.get(prometheus_url + '/api/v1/query', params={'query': query})
    results = response.json()['data']['result']
    return results

def get_pod_metrics(prometheus_url, pod_name):
    cpu_query = f'sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}"}}[5m])) by (pod)'
    memory_query = f'sum(container_memory_usage_bytes{{pod="{pod_name}"}}) by (pod)'

    cpu_data = query_prometheus(prometheus_url, cpu_query)
    memory_data = query_prometheus(prometheus_url, memory_query)

    cpu_usage = float(cpu_data[0]['value'][1]) if cpu_data else 0
    memory_usage = float(memory_data[0]['value'][1]) / (1024 * 1024) if memory_data else 0  # Convert to MiB

    return cpu_usage, memory_usage

def update(frame, prometheus_url, pod_name, timestamps, cpu_values, memory_values):
    timestamp = datetime.now()
    cpu_usage, memory_usage = get_pod_metrics(prometheus_url, pod_name)

    timestamps.append(timestamp)
    cpu_values.append(cpu_usage)
    memory_values.append(memory_usage)

    if len(timestamps) > 7200:  # 2 hours of data in the window (you can change that)
        timestamps.pop(0)
        cpu_values.pop(0)
        memory_values.pop(0)

    ax1.clear()
    ax2.clear()

    ax1.plot(timestamps, cpu_values, label='CPU Usage (cores)')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Usage (cores)')
    ax1.legend()

    ax2.plot(timestamps, memory_values, label='Memory Usage (MiB)')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Memory Usage (MiB)')
    ax2.legend()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Live plot CPU and Memory usage of a pod over time')
    parser.add_argument('--prometheus-url', type=str, required=True, help='Prometheus URL')
    parser.add_argument('--pod-name', type=str, required=True, help='Pod name')
    args = parser.parse_args()

    fig, (ax1, ax2) = plt.subplots(2, 1)
    timestamps = []
    cpu_values = []
    memory_values = []

    ani = FuncAnimation(fig, update, fargs=(args.prometheus_url, args.pod_name, timestamps, cpu_values, memory_values), interval=1000)
    plt.show()

# python3 prom_plot.py --prometheus-url http://157.159.68.41:30000 --pod-name hamster-d487488f-sshwg
