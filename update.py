import hashlib
import secrets
from pymongo import MongoClient
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def generate_secret_key(password):
    salt = os.urandom(16)  # Generate a random salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Length of the key
        salt=salt,
        iterations=100000,  # Number of iterations
        backend=default_backend()
    )
    key = kdf.derive(password.encode())  # Derive a key from the password
    return salt, key

def F(ks, w):
    return hashlib.sha256(ks.encode() + w.encode()).hexdigest()

def H1(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).hexdigest()

def H2(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).digest()

def Update(sigma, ind, op, db_connection, file_path):
    password = input("Enter the password: ")
    salt, ks = generate_secret_key(password)

    # Read the contents of the file to generate the keyword
    with open(file_path, 'r') as file:
        data = file.read()

    # Use the first few characters of the file content as the keyword
    keyword_length = 20 
    w = data[:keyword_length]

    tw = F(ks.hex(), w)  
    stc, c = sigma.get(w, (0, 0))
    if stc == 1:
        sto, c = 0, 0

    kc_plus_1 = secrets.choice([0, 1])
    stc_plus_1 = H1(tw, kc_plus_1)

    sigma[w] = (stc_plus_1, c + 1)

    # Encode the file data
    encoded_data = hashlib.sha256(data.encode()).digest()

    e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
    e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

    u = H1(tw, stc_plus_1)

    # Store the encoded data in MongoDB
    encodedfiles = db_connection["encodedfiles"]
    document = {"KeyColumn": u, "EncodedData": encoded_data, "Keyword": w}  
    encodedfiles.insert_one(document)

    return sigma


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db_connection = client["project"]  

file_path = "C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt" 

sigma = {}
ind = 1
op = 1

sigma = Update(sigma, ind, op, db_connection, file_path)

print("Sigma:", sigma)

client.close()
