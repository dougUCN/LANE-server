# User Authentication

## Creating new user accounts

User data is stored in `db/users.sqlite3`

## Settings

JWT token settings may be adjusted in `user_auth/settings.py`

## Usage

In your Django application code,

```
from apps.user_auth.utils import requires_auth
```

Simply apply the decorator `@requires_auth` to any ariadne graphql resolver that requires authentication protection.

```
@query.field("query")
@requires_auth
async def resolve_query(*_):
    ...
```

## Using Json Web Token (JWT) Authentication

Whenever the user wants to access a protected graphql api call, the user agent should send the JWT, typically in the Authorization header using the Bearer schema. The content of the header should look like the following:

```
Authorization: Bearer <token>
```
