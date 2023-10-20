import threading
import time


class MessageQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def enqueue(self, message):
        with self.lock:
            self.queue.append(message)

    def dequeue(self):
        with self.lock:
            if not self.is_empty():
                return self.queue.pop(0)
            else:
                return None

    def is_empty(self):
        return len(self.queue) == 0


def producer(queue, messages):
    for message in messages:
        print(f"Producing: {message}")
        queue.enqueue(message)
        time.sleep(1)


def consumer(queue):
    while True:
        message = queue.dequeue()
        if message is not None:
            print(f"Consuming: {message}")
        time.sleep(2)


# if __name__ == "__main__":
#     message_queue = MessageQueue()
#     producer_thread = threading.Thread(target=producer, args=(message_queue, ["Message 1", "Message 2", "Message 3"]))
#     consumer_thread = threading.Thread(target=consumer, args=(message_queue,))
#
#     producer_thread.start()
#     consumer_thread.start()
#
#     producer_thread.join()
#     consumer_thread.join()
