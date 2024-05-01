from flask import Flask, request, jsonify
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import secrets
from cryptography.hazmat.primitives import hashes
import re

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db_connection = client["project"]
encodedfiles = db_connection["encodedfiles"]
filename_index = db_connection["filename_index"]  # Inverted index collection

def generate_secret_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  
        salt=salt,
        iterations=100000,  
        backend=default_backend()
    )
    key = kdf.derive(password.encode())  
    return key

def extract_keywords(text):
    return re.findall(r'\b\w{4,}\b', text.lower())  # Extract words with 4 or more characters

@app.route('/upload', methods=['POST'])
def upload_file():
    # Extract file from request
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    
    file_path = os.path.join(os.getcwd(), file.filename)
    file.save(file_path)

    # Perform encryption
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Generate a secret key and salt for encryption
    password = getpass.getpass("Enter encryption password: ")
    salt = secrets.token_bytes(16)
    key = generate_secret_key(password, salt)

    # Encrypt the file data
    cipher = Cipher(algorithms.AES(key), modes.CBC(salt), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = padding.PKCS7(128).padder().update(file_data) + padding.PKCS7(128).padder().finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Extract keywords from the document
    keywords = extract_keywords(file_data.decode('utf-8'))

    # Insert encrypted file and keywords into MongoDB
    file_doc = {
        "filename": file.filename,
        "data": encrypted_data,
        "salt": salt,
        "keywords": keywords,
       
    }
    encodedfiles.insert_one(file_doc)

    
    filename_index.insert_one({"filename": file.filename, "file_id": file_doc["_id"]})

    # Delete the file from the server
    os.remove(file_path)

    return jsonify({'message': 'File uploaded and encrypted successfully'}), 200

@app.route('/search', methods=['GET'])
def search_files():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400

    
    files = list(encodedfiles.find({"keywords": {"$in": [keyword.lower()]}}))

    if not files:
        return jsonify({'message': 'No files found with the provided keyword'}), 404

    response = []
    for file in files:
        response.append({
            'Filename': file['filename'],
            'FileID': str(file['_id']),
         
        })

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
