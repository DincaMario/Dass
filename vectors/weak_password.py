import argparse
import requests
import random
import string

WEAK_PASSWORDS = [("1", "Un singur caracter"), ("123", "Parola simpla"), ("password", "Parola generica"), ("", "Parola goala"), ("123456789", "Parola simpla")]

def test_password_policy(target_url):
    accepted = []
    rejected = []

    for password, description in WEAK_PASSWORDS:
        rand = ''.join(random.choices(string.ascii_lowercase, k=8))
        email = f"test_{rand}@poc.ro"

        try:
            res = requests.post(
                f"{target_url}/api/register",
                json={"email": email, "password": password, "role": "ANALYST", "confirmPassword": password},
                timeout=10
            )
            data = res.json()

            if res.status_code in (200, 201):
                accepted.append((password, description))
                print(f"A intrat:{password} ( {description} )")
            else:
                rejected.append((password, description))
                error = data.get("error", "")
                details = data.get("details", [])
                print(f"A respins:{password} ( {description} )")

                if details:
                    for d in details:
                        print(d)
        
        except requests.exceptions.RequestException as e:
            print(f"Eroare {e}")

    
    print()
    print()
    print(f"Parole acceptate: {accepted}")
    print()
    print(f"Parole respinse: {rejected}")

    if accepted:
        print(f"Urmatoarele parole slabe au fost acceptate")
        for pwd, desc in accepted:
            print(f"{pwd} | {desc}")
        
        print()
        print("Impactul: Utilizatorii pot face conturi cu parole banale, expunandu-si astfel conturile sa fie sparte prin brute force")
    
    print()
    return len(accepted), len(rejected)

parser = argparse.ArgumentParser(description="Weak Password")
parser.add_argument("--target", default="http://localhost:5000")
args = parser.parse_args()

test_password_policy(args.target)