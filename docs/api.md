# Backend API

## Supervisor API

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/supervisor |
| **DataType** | json |
| **Data sample** | {"message": "Give me a report on the sales of the past week"} |
| **Description** | Send the supervisor a prompt to handle. |

## Authentication

### Sign up

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/signup |
| **DataType** | json |
| **Data sample** | {"username": "user", "password": "password"} |
| **Description** | Create a user with the given username and password. |

### Sign in

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/signin |
| **DataType** | json |
| **Data sample** | {"username": "user", "password": "password"} |
| **Description** | Sign in with the given username and password. |

### Log out

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/logout |
| **DataType** | None |
| **Data sample** | |
| **Description** | Log the current user out. |

### Check authentication

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/check_auth |
| **DataType** | None |
| **Data sample** | |
| **Description** | Check if the current user is logged in. |
