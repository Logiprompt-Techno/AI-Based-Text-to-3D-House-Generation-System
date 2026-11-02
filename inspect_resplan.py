import pickle
from pprint import pprint

path = "backend/dataset/house_dataset/ResPlan.pkl"

with open(path, "rb") as f:
    data = pickle.load(f)

print("=" * 60)
print("DATA TYPE:", type(data))
print("=" * 60)

if isinstance(data, dict):
    print("Dictionary Keys:")
    print(list(data.keys()))

    first_key = next(iter(data))
    print("\nFirst Key:", first_key)
    print("\nFirst Value Type:", type(data[first_key]))
    pprint(data[first_key])

elif isinstance(data, list):
    print("Total Items:", len(data))

    if len(data):
        print("\nFirst Item Type:", type(data[0]))
        pprint(data[0])

else:
    print(data)