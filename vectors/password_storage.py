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


crack_md5_hashes(DATABASE, WORDLIST)