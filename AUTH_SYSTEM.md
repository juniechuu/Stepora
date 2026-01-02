# Stepora Authentication System

## Overview
This document describes the authentication system implemented in Stepora using SQLite and Flask.

## Backend Structure

### Database (`services/database.py`)
- **Users table**: Stores user credentials and profile information
  - `id`: Primary key
  - `username`: Unique username
  - `email`: Unique email address
  - `password_hash`: SHA-256 hashed password
  - `full_name`: Optional full name
  - `created_at`: Account creation timestamp
  - `last_login`: Last login timestamp
  - `is_active`: Account status flag

- **User Sessions table**: Manages login sessions
  - `id`: Primary key
  - `user_id`: Foreign key to users table
  - `session_token`: Unique session token
  - `created_at`: Session creation time
  - `expires_at`: Session expiration time (7 days)
  - `is_active`: Session status flag

### API Endpoints (`services/routes/auth_routes.py`)

1. **POST /api/auth/register**
   - Register a new user
   - Body: `{ username, email, password, full_name? }`
   - Returns: User info on success

2. **POST /api/auth/login**
   - Authenticate user and create session
   - Body: `{ username, password }`
   - Returns: Session token and user info

3. **GET /api/auth/verify**
   - Verify session token validity
   - Header: `Authorization: Bearer <token>`
   - Returns: User info if valid

4. **POST /api/auth/logout**
   - Invalidate user session
   - Header: `Authorization: Bearer <token>`
   - Returns: Success message

5. **GET /api/auth/me**
   - Get current user information
   - Header: `Authorization: Bearer <token>`
   - Returns: User profile data

## Frontend Structure

### Service (`web/src/app/endpoints/auth.service.ts`)
- Handles all authentication operations
- Manages session token in localStorage
- Provides observable for current user state
- Methods:
  - `register()`
  - `login()`
  - `logout()`
  - `verifyToken()`
  - `getCurrentUser()`
  - `isLoggedIn()`

### Components

1. **Login Page** (`web/src/app/pages/login/`)
   - User login form
   - Validation for username and password
   - Error handling
   - Redirect to home after login

2. **Register Page** (`web/src/app/pages/register/`)
   - New user registration form
   - Field validation (username length, email format, password match)
   - Success message and redirect to login

3. **Updated Navbar** (`web/src/app/core/navbar/`)
   - Shows Login/Sign Up buttons when not authenticated
   - Shows user avatar and dropdown menu when authenticated
   - Logout functionality

## Security Features

1. **Password Hashing**: SHA-256 hashing for passwords
2. **Session Tokens**: Secure random tokens (32 bytes)
3. **Session Expiration**: 7-day expiry for sessions
4. **Authorization Headers**: Bearer token authentication
5. **Input Validation**: Both frontend and backend validation

## Usage Flow

### Registration
1. User fills registration form
2. Frontend validates input
3. POST request to `/api/auth/register`
4. Backend creates user in database
5. Redirect to login page

### Login
1. User enters credentials
2. POST request to `/api/auth/login`
3. Backend verifies credentials
4. Session token generated and returned
5. Token stored in localStorage
6. User redirected to home page

### Authentication Check
1. On app load, service checks for existing token
2. Verifies token with backend
3. Updates user state accordingly
4. Navbar updates to show user info

### Logout
1. User clicks logout
2. POST request to `/api/auth/logout`
3. Session invalidated in database
4. Token removed from localStorage
5. User state reset

## Running the Application

### Backend
```bash
cd services
python app.py
```
Database will be automatically initialized at `services/stepora.db`

### Frontend
```bash
cd web
npm run start
```

## Next Steps

Once this authentication system is tested and working:
1. Add chat history linked to user accounts
2. Implement leaderboard with user scores
3. Add process/task tracking per user
4. Cache scraped articles
5. Add user profile management
