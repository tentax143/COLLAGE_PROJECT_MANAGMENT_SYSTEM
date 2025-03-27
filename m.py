# arr=[1,2,3,7,5]
# target=12
# sn= set()
# for num in arr:
#     cmp=target-num
#     if cmp in sn:
#         print(num,cmp)
#         break
#     sn.add(num)

import hashlib
import itertools
import string

target_hash = "6c8ed326c8c0b302f0caa199ff6398389311a349ebfe40dcccb70e134a458102"

def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Characters to try (lowercase, uppercase, digits)
characters = string.ascii_lowercase + string.digits  # "abcdefghijklmnopqrstuvwxyz0123456789"

# Brute-force all 5-character combinations
for password in itertools.product(characters, repeat=5):
    password = "".join(password)
    if encrypt_password(password) == target_hash:
        print(f"✅ Password found: {password}")
        break
else:
    print("❌ Password not found.")

