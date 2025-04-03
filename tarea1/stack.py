class Stack:
    """
    Stack, supports the following operations:
    - push
    - pop
    - peek
    - list
    - clear
    """
    
    def __init__(self):
        self.stash = []
    
    def push(self, state):
        self.stash.append(state.copy())
        
    def pop(self):
        if not self.stash:
            raise IndexError("Stack is empty")
        return self.stash.pop()
        
    def peek(self):
        if not self.stash:
            return None
        return self.stash[-1]
    
    def list(self):
        return self.stash.copy()
    
    def clear(self):
        self.stash.clear()
        

# ========== Ejemplos    
    
stash = Stack()

state1 = {"var": 1}
state2 = {"var": 2}

stash.push(state1)
stash.push(state2)

print(stash.peek()) # {'var': 2}
print(stash.pop()) # {'var': 2}
print(stash.list()) # [{'var': 1}]
