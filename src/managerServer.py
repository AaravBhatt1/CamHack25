from multiprocessing.managers import BaseManager
from queue import Queue

queue = Queue()

class QueueManager(BaseManager): pass

QueueManager.register('get_queue', callable=lambda: queue)

if __name__ == "__main__":
    manager = QueueManager(address=('localhost', 50000), authkey=b'abc')
    server = manager.get_server()
    print("Manager server running...")
    server.serve_forever()
