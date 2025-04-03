class Queue():
    def __init__(self):
        self.queue = []
        
    def enqueue(self, item):
        self.queue.append(item)
        
    def dequeue(self):
        if not self.queue:
            return IndexError("Queue is empty")
        return self.queue.pop(0)
        
    def peek(self):
        if not self.queue:
            None
        return self.queue[0]
    
    def is_empty(self):
        return not self.queue
    
    def size(self):
        return len(self.queue)
    
# ========== Ejemplos

q = Queue()
q.enqueue("a")
q.enqueue("b")
q.enqueue("c")

print(q.is_empty()) # False
print(q.peek()) # 'a'
print(q.dequeue()) # 'a'
print(q.peek()) # 'b'
print(q.size()) # 2
print(q.is_empty()) # False

q.dequeue()
q.dequeue()
q.dequeue()

print(q.is_empty()) # True