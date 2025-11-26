# Time Capsule Frontend

React SPA frontend for the Time Capsule Digital Legacy application.

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router DOM v6
- **HTTP Client**: Axios
- **State Management**: React Context API

## Project Structure

```
frontend/
├── public/                # Static assets
├── src/
│   ├── api/               # API client and services
│   │   ├── apiClient.js   # Configured Axios instance
│   │   └── authApi.js     # Authentication API functions
│   ├── components/        # Reusable components
│   │   ├── Navbar.jsx     # Navigation bar
│   │   ├── Navbar.css
│   │   ├── ProtectedRoute.jsx  # Route protection
│   ├── context/           # React Context providers
│   │   └── AuthContext.jsx     # Authentication state
│   ├── pages/             # Page components
│   │   ├── Home.jsx       # Landing page
│   │   ├── Home.css
│   │   ├── Login.jsx      # Login page
│   │   ├── Register.jsx   # Registration page
│   │   ├── Auth.css       # Shared auth styles
│   │   ├── Dashboard.jsx  # User dashboard
│   │   └── Dashboard.css
│   ├── App.jsx            # Main app component
│   ├── App.css
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── index.html             # HTML template
├── package.json           # Dependencies
├── vite.config.js         # Vite configuration
├── .env.example           # Environment template
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Node.js 18 or higher
- npm or yarn

### 2. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:5000` |

### 4. Run Development Server

```bash
npm run dev

# Or with yarn
yarn dev
```

The application will be available at `http://localhost:5173`

### 5. Build for Production

```bash
npm run build

# Preview production build
npm run preview
```

## Features

### Implemented (Part 1)

- ✅ User Registration
- ✅ User Login
- ✅ JWT-based Authentication
- ✅ Protected Routes
- ✅ Session Persistence
- ✅ Responsive Navigation
- ✅ User Dashboard

### Coming in Part 2

- ⏳ Create Time Capsules
- ⏳ Manage Recipients
- ⏳ Manage Guardians
- ⏳ Schedule Deliveries
- ⏳ Attach Files
- ⏳ Message Encryption

## Pages

### Home (`/`)
Landing page with project description and call-to-action buttons.

### Login (`/login`)
User authentication form. Redirects to dashboard on success.

### Register (`/register`)
New user registration form with validation.

### Dashboard (`/dashboard`)
Protected page showing user information and placeholder for future capsule management.

## Authentication Flow

1. **Registration**: User submits name, email, password → Backend creates account and returns JWT → Auto-login and redirect to dashboard

2. **Login**: User submits credentials → Backend verifies and returns JWT → Token stored in localStorage → Redirect to dashboard

3. **Session Restoration**: On app load → Check for token in localStorage → Call `/api/auth/me` to validate → If valid, restore user state

4. **Protected Routes**: ProtectedRoute component checks auth state → If not authenticated, redirect to login with return path

5. **Logout**: Clear token from localStorage → Clear user from context → Redirect to login

## Code Organization

### API Client (`src/api/apiClient.js`)
- Configured Axios instance
- Automatic JWT token attachment
- Error handling interceptors

### Auth Context (`src/context/AuthContext.jsx`)
- Global authentication state
- `user`: Current user object
- `token`: JWT token
- `login(user, token)`: Set auth state
- `logout()`: Clear auth state
- `isAuthenticated`: Boolean check

### Protected Route (`src/components/ProtectedRoute.jsx`)
- Wraps routes requiring authentication
- Shows loading state while checking auth
- Redirects to login if not authenticated

## Styling

The application uses CSS with CSS variables for consistent theming:

```css
:root {
  --color-primary: #6366f1;
  --color-secondary: #64748b;
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-text: #1e293b;
  /* ... more variables */
}
```

## Development

### Linting

```bash
npm run lint
```

### File Naming Conventions

- Components: PascalCase (e.g., `Navbar.jsx`)
- API files: camelCase (e.g., `authApi.js`)
- CSS files: Same name as component (e.g., `Navbar.css`)

### Adding New Pages

1. Create page component in `src/pages/`
2. Create corresponding CSS file
3. Add route in `src/App.jsx`
4. If protected, wrap with `<ProtectedRoute>`

### Adding New API Functions

1. Add function in appropriate file under `src/api/`
2. Import `apiClient` for HTTP requests
3. Handle errors appropriately

## License

MIT License
