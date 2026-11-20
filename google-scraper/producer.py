import sys
import json
import pika
from urllib.parse import quote_plus

AMQP_URL = "amqp://admin:admin123@rabbitmq:5672/"
QUEUE = "search_tasks"


def main():

    if len(sys.argv) < 3:
        print('Usage: python producer.py "search query" 1-10 11-21')
        sys.exit(1)

    query = sys.argv[1]
    ranges = sys.argv[2:]

    connection = pika.BlockingConnection(
        pika.URLParameters(AMQP_URL)
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE,
        durable=True
    )

    total = 0

    for page_range in ranges:

        start, end = map(int, page_range.split("-"))

        if start < 1 or end < start:
            raise ValueError(f"Invalid page range: {page_range}")

        for page in range(start, end + 1):

            url = (
                "https://www.google.com/search"
                f"?q={quote_plus(query)}"
                f"&num=10&start={(page - 1) * 10}"
            )

            task = {
                "action": "download",
                "page": page,
                "url": url,
                "filename": f"google_page_{page:03d}.html"
            }

            channel.basic_publish(
                exchange="",
                routing_key=QUEUE,
                body=json.dumps(task),
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )

            total += 1

        print(f"Published range: {page_range}")

    connection.close()

    print(f"Successfully published {total} tasks.")


if __name__ == "__main__":
    main()
