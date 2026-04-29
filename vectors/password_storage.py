import hashlib
import time

DATABASE = [
     {"email":"admin@test.ro","hash": hashlib.md5("admin".encode()).hexdigest()},
     {"email":"analyst@test.ro", "hash":hashlib.md5("password".encode()).hexdigest()},
     {"email":"eu@test.ro", "hash":hashlib.md5("123456".encode()).hexdigest()}
]

WORDLIST = [
    "123456", "password", "12345678", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine",
    "michael", "shadow", "123123", "654321", "admin123",
    "admin", "root", "toor", "pass", "test",
]

def crack_md5_hashes(db_dump, wordlist):
    for row in db_dump:
        print(f"{row['email']:<30} -> {row['hash']}")
    start= time.time()
    rainbow = {}

    for pwd in wordlist:
        h = hashlib.md5(pwd.encode()).hexdigest()
        rainbow[h] = pwd
    cracked = 0
    for row in db_dump:
        if row["hash"] in rainbow:
            cracked += 1
            print(f"A fost spart {row['email']:<30} -> Parola: '{rainbow[row['hash']]}'")
        else:
            print(f"{row['email']:<30} -> Nu s-a gasit in dictionar")
    
    elapsed = time.time() - start

    print()
    print(f"Parole sparte: {cracked}/{len(db_dump)}")
    print(f"Timp {elapsed*1000:.1f} ms")
    print(f"Vitez: {len(wordlist)/(elapsed+0.001):.0f} parole/sec")

    return cracked


def demonstrate_bcrypt_resistance():
    print("Comparatie: Bcrypt")

    password = "password"

    start = time.time()
    for _ in range(10000):
        hashlib.md5(password.encode()).hexdigest()
    md5_time = time.time() - start
    md5_per_sec = 10000 / md5_time

    print(f"10 mii de hash-uri in {md5_time*1000:.1f}ms")
    print(f"Viteza: {md5_per_sec:,.0f} hash/sec")

    try:
        import bcrypt
        start = time.time()
        bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
        bcrypt_one = time.time() - start
        bcrypt_per_sec = 1 / bcrypt_one

        print(f"1 hash in {bcrypt_one*1000:.1f}ms")
        print(f"Viteza: {bcrypt_per_sec:.1f}hash/sec")
    except ImportError:
        print("Eroare")
    
    h1 = hashlib.md5(b"password").hexdigest()
    h2 = hashlib.md5(b"password").hexdigest()

    print(f"h1: {h1}")
    print(f"h2: {h2}")

    if h1 == h2:
        print("Rainbow tables functioneaza pe md5")
    
    try:
        import bcrypt
        b1 = bcrypt.hashpw(b"password", bcrypt.gensalt()).decode()
        b2 = bcrypt.hashpw(b"password", bcrypt.gensalt()).decode()
        print(f"b1: {b1}")
        print(f"b2: {b2}")
        if b1 == b2:
            print("Rainbow tables functioneaza pe bcrypt")
    except:
        print("Eroare")


crack_md5_hashes(DATABASE, WORDLIST)
demonstrate_bcrypt_resistance()