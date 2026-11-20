import os
import json
import subprocess
import pika

AMQP_URL = os.environ["AMQP_URL"]
OUTPUT_DIR = "/data"

QUEUE = "search_tasks"

connection = pika.BlockingConnection(
    pika.URLParameters(AMQP_URL)
)

channel = connection.channel()
channel.queue_declare(queue=QUEUE, durable=True)
channel.basic_qos(prefetch_count=1)


def process_task(ch, method, properties, body):
    task = json.loads(body)

    page = task["page"]
    url = task["url"]
    filename = task["filename"]

    print(f"Downloading page {page}")

    output_file = f"/usr/src/app/out/{filename}"

    command = [
        "docker", "run", "--rm",
        "-v",
        f"{os.path.abspath(OUTPUT_DIR)}:/usr/src/app/out",
        "capsulecode/singlefile",
        url,
        output_file
    ]

    try:
        subprocess.run(command, check=True, timeout=180)
        print(f"Saved: {filename}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        print(f"Failed page {page}: {error}")
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


channel.basic_consume(
    queue=QUEUE,
    on_message_callback=process_task,
    auto_ack=False
)

print("Worker waiting for tasks...")
channel.start_consuming()