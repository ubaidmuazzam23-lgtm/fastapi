import jwt
from datetime import datetime, timedelta

def create_test_token():
    payload = {
        'sub': 'user_clerk_12345',
        'email': 'clerk@test.com',
        'first_name': 'Clerk',
        'last_name': 'User',
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return token

if __name__ == "__main__":
    print(create_test_token())