import hashlib
import secrets
from pymongo import MongoClient

def F(ks, w):
    return hashlib.sha256(ks.encode() + w.encode()).hexdigest()

def H1(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).hexdigest()

def H2(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).digest()

def Update(sigma, ind, op, db_connection, file_path):
    ks = input("Enter the value of 'ks': ")
    w = input("Enter the value of 'w': ")

    tw = F(ks, w)
    stc, c = sigma.get(w, (0, 0))
    if stc == 1:
        sto, c = 0, 0

    kc_plus_1 = secrets.choice([0, 1])
    stc_plus_1 = H1(tw, kc_plus_1)

    sigma[w] = (stc_plus_1, c + 1)

    with open(file_path, 'rb') as file:
        data = file.read()

    # Encode the file data
    encoded_data = hashlib.sha256(data).digest()

    e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
    e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

    u = H1(tw, stc_plus_1)

    # Store the encoded data in MongoDB
    encodedfiles = db_connection["encodedfiles"]
    document = {"KeyColumn": u, "EncodedData": encoded_data, "Keyword": w}  # Add the keyword to the document
    encodedfiles.insert_one(document)

    return sigma


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db_connection = client["project"]  # Update with your MongoDB database name

file_path = "C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt"  # Update with your file path

sigma = {}
ind = 1
op = 1

sigma = Update(sigma, ind, op, db_connection, file_path)

print("Sigma:", sigma)

# Close the database connection
client.close()
