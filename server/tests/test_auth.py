from finance_flow.auth import create_access_token, decode_access_token


def test_create_and_decode_access_token() -> None:
    user_id = 123

    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert decode_access_token(token) == user_id


def test_decode_invalid_token() -> None:
    assert decode_access_token("invalid-token") is None