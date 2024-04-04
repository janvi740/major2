import pyrocksdb
import hashlib
import secrets

def F(ks, w):
    return hashlib.sha256(ks.encode() + w.encode()).hexdigest()

def H1(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).hexdigest()

def H2(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).digest()

def Update(ks, sigma, ind, w, op, db, file_path):
    tw = F(ks, w)
    stc, c = sigma.get(w, (0, 0))
    if stc == 1:
        sto, c = 0, 0
    
    kc_plus_1 = secrets.choice([0, 1])
    stc_plus_1 = H1(tw, kc_plus_1)

    sigma[w] = (stc_plus_1, c + 1)

    with open("C:\Users\Janvi Mittal\OneDrive\Desktop\project.txt", 'rb') as file:
        data = file.read()
    
    # Encode the file data
    encoded_data = hashlib.sha256(data).digest()

    e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
    e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

    u = H1(tw, stc_plus_1)

    # Convert bytes to string for key
    u_str = u.decode('utf-8')

    # Store the encoded data in RocksDB
    db.put(u_str.encode('utf-8'), encoded_data)

    return sigma

# Open RocksDB database
options = pyrocksdb.Options()
options.create_if_missing = True
db = pyrocksdb.DB("/tmp/testdb", options)

# Example usage:
ks = "dhairya"
sigma = {}

ind = 1
w = "janvi"
op = 1
file_path = "C:\Users\Janvi Mittal\OneDrive\Desktop\project.txt"

sigma = Update(ks, sigma, ind, w, op, db, file_path)

print("Sigma:", sigma)

# Close the database
db.close()
