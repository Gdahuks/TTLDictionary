from ttl_dictionary import TTLDictionary

__all__ = ["TTLDictionary"]

from ttl_dictionary import TTLDictionary
import time

# Create a new TTLDictionary
ttl_dict = TTLDictionary()

# Add a key-value pair with a TTL of 5 seconds
ttl_dict["key1"] = ("value1", 5)

# Add a key-value pair with no TTL (it will not expire)
ttl_dict["key2"] = "value2"

# Get a value
print(ttl_dict["key1"])  # Outputs: value1

# Wait for 6 seconds
time.sleep(6)

# Try to get the value of "key1" again
try:
    print(ttl_dict["key1"])
except KeyError:
    print("Key1 is not in the dictionary")  # Outputs: Key1 is not in the dictionary

# Check if "key2" is in the dictionary
if "key2" in ttl_dict:
    print("Key2 is in the dictionary")  # Outputs: Key2 is in the dictionary

# Get the number of key-value pairs in the dictionary
print(len(ttl_dict))  # Outputs: 1