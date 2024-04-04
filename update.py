import hashlib
import secrets
from pymongo import MongoClient
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import getpass  # Import getpass for secure password input
from textblob import TextBlob

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
  # Use raw key bytes
  return hashlib.sha256(ks + w.encode()).hexdigest()

def H1(tw, st):
  return hashlib.sha256(tw.encode() + str(st).encode()).hexdigest()

def H2(tw, st):
  return hashlib.sha256(tw.encode() + str(st).encode()).digest()

def Update(sigma, ind, op, db_connection, file_path):
  # Secure password handling
  password = getpass.getpass("Enter password: ")

  salt, ks = generate_secret_key(password)

  # Consider a more robust keyword generation method
  with open("C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt", 'r') as file:
    data = file.read()
    text = TextBlob(data)
    # Choose appropriate method for keyword extraction
    # Options: noun_phrases, keywords (default), nlp.extract_keywords
    keywords = text.noun_phrases  # Example: extract noun phrases

  # Select the first keyword (adjust as needed)
  keyword = keywords[0] if keywords else ""

    # Extract meaningful keyword or use a keyword extraction library
  # Replace with your keyword extraction logic

  # Update logic according to your state transition requirements
  tw = F(ks, keyword)
  stc, c = sigma.get(keyword, (0, 0))

  kc_plus_1 = secrets.choice([0, 1])
  stc_plus_1 = H1(tw, kc_plus_1)

  sigma[keyword] = (stc_plus_1, c + 1)

  # Stronger encryption with AES-GCM
  iv = os.urandom(12)  # Initialization vector for encryption
  encryptor = Cipher(algorithms.AES(ks), modes.GCM(iv)).encryptor()
  padder = padding.PKCS7(128).padder()
  encoded_data = encryptor.update(padder.update(data.encode()) + padder.finalize()) + encryptor.finalize()
  tag = encryptor.tag

  e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
  e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

  u = H1(tw, stc_plus_1)

  # Store the encoded data in MongoDB
  encodedfiles = db_connection["encodedfiles"]
  document = {"KeyColumn": u, "EncodedData": encoded_data, "Tag": tag, "IV": iv, "Keyword": keyword}
  encodedfiles.insert_one(document)

  return sigma


# Connect to MongoDB
# ... (update with your MongoDB connection details)
client = MongoClient("mongodb://localhost:27017")
db_connection = client["project"]  # Update with your MongoDB database name

file_path = "C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt"  # Update with your file path

sigma = {}
ind = 1
op = 1

sigma = Update(sigma, ind, op, db_connection, file_path)

print("Sigma:", sigma)

# Close the database connection
# ... (close the connection)
client.close()