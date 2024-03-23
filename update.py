import hashlib
import secrets

def F(ks, w):
    return hashlib.sha256(ks.encode() + w.encode()).hexdigest()

def H1(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).hexdigest()

def H2(tw, st):
    return hashlib.sha256(tw.encode() + str(st).encode()).digest()

def Update(ks, sigma, ind, w, op, T):
    tw = F(ks, w)
    stc, c = sigma.get(w, (0, 0))
    if stc == 1:
        sto, c = 0, 0
    
    kc_plus_1 = secrets.choice([0, 1])
    stc_plus_1 = H1(tw, kc_plus_1)

    sigma[w] = (stc_plus_1, c + 1)

    e = bytearray(ind.to_bytes(1, 'big')) + op.to_bytes(1, 'big') + kc_plus_1.to_bytes(1, 'big')
    e_xor = bytes(a ^ b for a, b in zip(e, H2(tw, stc_plus_1)))

    u = H1(tw, stc_plus_1)

    T[u] = e_xor

    return sigma, T

# Example usage:
ks = "dhairya"
sigma = {}
T = {}

ind = 1
w = "janvi"
op = 1

sigma, T = Update(ks, sigma, ind, w, op, T)

print("Sigma:", sigma)
print("T:", T)