from backend.utils.security import create_access_token, decode_access_token, hash_password, verify_password


def test_passwords_are_hashed_and_tokens_round_trip():
    encoded = hash_password("correct horse battery")
    assert encoded != "correct horse battery"
    assert verify_password("correct horse battery", encoded)
    assert not verify_password("wrong password", encoded)
    assert decode_access_token(create_access_token(7)) == 7