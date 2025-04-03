my_map = {}

# Agregar key-value pairs
my_map["name"] = "Alice"
my_map["age"] = 30

# Acceder valores en key "name"
print(my_map["name"]) # Output: Alice

# Checar si existe
if "age" in my_map:
    print("Age is in the map")

# Remover "age"
del my_map["age"]

# get
print(my_map.get("name", "Unknown"))

# Iteración
for key, value in my_map.items():
    print(f"{key}: {value}")
