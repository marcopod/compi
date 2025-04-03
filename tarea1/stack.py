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
        self.stack = []
    
    def push(self, state):
        self.stack.append(state.copy())
        
    def pop(self):
        if not self.stack:
            raise IndexError("Stack is empty")
        return self.stack.pop()
        
    def peek(self):
        if not self.stack:
            return None
        return self.stack[-1]
    
    def list(self):
        return self.stack.copy()
    
    def clear(self):
        self.stack.clear()
        

# ========== Ejemplos    
    
stack = Stack()

state1 = {"var": 1}
state2 = {"var": 2}

stack.push(state1)
stack.push(state2)

print(stack.peek()) # {'var': 2}
print(stack.pop()) # {'var': 2}
print(stack.list()) # [{'var': 1}]
