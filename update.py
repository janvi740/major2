import mysql.connector
import hashlib
import secrets

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

    with open("C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt", 'rb') as file:
        data = file.read()
    
    # Encode the file data
    encoded_data = hashlib.sha256(data).digest()

    e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
    e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

    u = H1(tw, stc_plus_1)

    # Store the encoded data in MySQL
    cursor = db_connection.cursor()
    sql = "INSERT INTO encodedfiles (KeyColumn, EncodedData) VALUES (%s, %s)"
    val = (u, encoded_data)
    cursor.execute(sql, val)
    db_connection.commit()

    return sigma

# Open MySQL database connection
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="janvi",
    database="mysql"
)

file_path = "C:/Users/Janvi Mittal/OneDrive/Desktop/project.txt"  # Update with your file path

sigma = {}
ind = 1
op = 1

sigma = Update(sigma, ind, op, db_connection, file_path)

print("Sigma:", sigma)

# Close the database connection
db_connection.close()
