import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Recipients from './pages/Recipients.jsx'
import CreateCapsule from './pages/CreateCapsule.jsx'
import CapsuleDetail from './pages/CapsuleDetail.jsx'
import './App.css'

/**
 * Main Application Component
 * 
 * Sets up routing for all pages and includes the navigation bar.
 * Protected routes are wrapped with ProtectedRoute component.
 */
function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/recipients" 
            element={
              <ProtectedRoute>
                <Recipients />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/capsules/new" 
            element={
              <ProtectedRoute>
                <CreateCapsule />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/capsules/:id" 
            element={
              <ProtectedRoute>
                <CapsuleDetail />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
    </div>
  )
}

export default App
