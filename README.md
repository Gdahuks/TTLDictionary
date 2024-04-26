# Time-to-live python dictionary

This repository contains the implementation of a simple dictionary with Time-To-Live (TTL) functionality in Python. This code was created as a part of side project.

## Overview

The `TTLDictionary` is a dictionary-like object where each key-value pair has a time-to-live (TTL). The key-value pairs are automatically removed from the dictionary when their TTL expires. This is achieved by using a daemon thread that continuously checks for expired key-value pairs and removes them.

## Features

- Thread-safe operations: The `TTLDictionary` uses a `threading.RLock()` to ensure thread-safe operations.
- Automatic cleanup: A daemon thread is used to continuously clean up expired key-value pairs.
- Flexible TTL: Each key-value pair can have a different TTL. If no TTL is provided, the key-value pair will not expire.
- The repository also includes a set of unit tests (`ttl_dictionary_ut.py`) to verify the functionality of the `TTLDictionary`

## Example of Usage

```python
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
```

## License

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg