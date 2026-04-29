import argparse
import requests
import time


TEST_EMAILS = [
    # "admin@test.ro",
    "analyst@test.ro",
    "john@test.ro",
    "test@test.ro",
    "manager@test.ro",
    "ceo@test.ro",
    "hr@test.ro",
    "nonexistent@test.ro",
]

def enumerate_users(target_url, emails):
    print("Testam email-uri")

    found = []
    not_found = []
    responses = {}

    for email in emails:
        try:
            start = time.time()
            res = requests.post(
                f"{target_url}//api/login",
                json={"email": email, "password": "wrong_password_123"},
                timeout=10
            )
            elapsed = time.time() - start


            status = res.status_code
            data = res.json()
            error_msg = data.get("error", "")

            responses[email] = {
                "status": status,
                "message": error_msg,

            }

            if status == 404:
                print(f"email: {email} nu exista ( status = {status}, {elapsed * 1000}ms)")
                print(f"Eroare: {error_msg}")
                not_found.append(email)
            elif status == 401:
                print(f"email: {email} exista ( status = {status}, {elapsed * 1000}ms)")
                print(f"Eroare: {error_msg}")
                found.append(email)
            else:
                print(f"Mesaj: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f" {email}: Eroare - {e}")
    
    print("Rezultate:")

    unique_messages = set(r["message"] for r in responses.values())
    unique_statuses = set(r["status"] for r in responses.values())

    if len( unique_messages ) > 1 or len(unique_statuses) > 1:
        print(f"Mesaje diferite detectate")
        for msg in unique_messages:
            print(f"{msg}")
        print(f"Utilizatorii confirmati: {found}")
        print(f"Un atacator poate determina ce conturi exista in sistem")

    else:
        print("Toate raspunsurile sunt identice")

    return found

parser = argparse.ArgumentParser(description="User Enumeration")
parser.add_argument("--target", default="http://localhost:5000")
args = parser.parse_args()

enumerate_users(args.target, TEST_EMAILS)