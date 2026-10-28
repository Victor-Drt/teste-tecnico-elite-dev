from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password):
    return password_hash.hash(password)


def verify_password(plain_password, password):
    return password_hash.verify(plain_password, password)
