# Backend API

## Supervisor API

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/supervisor |
| **DataType (Request)** | json |
| **DataType (Response)** | json |
| **Parameters** | message |
| **Sample request** | {"message":"hello"} |
| **Sample response** | data: [{"subgraph": null, "node": "model", "kind": "other", "messages": [{"content": "Hello! How can I assist you today?", "tool_calls": []}]}] |
| **Description** | Login required. Send the supervisor a prompt to handle. |

## Authentication

### Sign up

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/signup |
| **DataType (Request)** | json |
| **DataType (Response)** | json |
| **Sample request** | {"username": "user", "password": "password"} |
| **Sample response** | {"message": "User created", "user": {"username": "username"}} |
| **Description** | Create a user with the given username and password. |

### Sign in

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/signin |
| **DataType (Request)** | json |
| **DataType (Response)** | json |
| **Sample request** | {"username": "user", "password": "password"} |
| **Sample response** | {"message": "Login successful! Welcome", "user": {"username": "user"}} |
| **Description** | Sign in with the given username and password. |

### Log out

|      |      |
| ---- | ---- |
| **Type** | POST |
| **URI** | /api/logout |
| **DataType (Request)** | None |
| **DataType (Response)** | json |
| **Sample response** | {"message": "Logged out successfully"} |
| **Description** | Log the current user out. |

### Check authentication

|      |      |
| ---- | ---- |
| **Type** | GET |
| **URI** | /api/check_auth |
| **DataType (Request)** | None |
| **DataType (Response)** | json |
| **Sample response** | {"authenticated": True, "user": {"username": "user"}} |
| **Description** | Check if the current user is logged in. |

### User info

|      |      |
| ---- | ---- |
| **Type** | GET |
| **URI** | /api/me |
| **DataType (Request)** | None |
| **DataType (Response)** | json |
| **Sample response** | {"user_id":1} |
| **Description** | Login required. Get information for current user. |

## Chat

|      |      |
| ---- | ---- |
| **Type** | GET |
| **URI** | /api/fetch_chats |
| **DataType (Request)** | None |
| **DataType (Response)** | json |
| **Sample response** | {"chats": [...]} |
| **Description** | Login required. Fetch chats for the current user. |

## Data

### Dashboard data
|      |      |
| ---- | ---- |
| **Type** | GET |
| **URI** | /api/dashboard-data |
| **DataType (Request)** | None |
| **DataType (Response)** | json |
| **Sample response** | {"revenue": ...} |
| **Description** | Get data for the dashboard. |

### Sales data
|      |      |
| ---- | ---- |
| **Type** | GET |
| **URI** | /api/sales-data |
| **Parameters** | start_date, end_date |
| **DataType (Request)** | string date (yyyy-mm-dd) |
| **DataType (Response)** | json |
| **Sample request** | /api/sales-data?start_date=2025-06-01&end_date=2025-06-03 |
| **Sample response** | {"revenue":98317.46,"sales":3168,"transactions":300} |
| **Description** | Get sales data for a specific day or date range. Returns error if date range is not supplied.|

