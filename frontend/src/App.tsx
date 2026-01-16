import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RunDetail from './pages/RunDetail'
import Projects from './pages/Projects'
import Configuration from './pages/Configuration'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Landing from './pages/Landing'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/welcome" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/projects" element={
          <ProtectedRoute>
            <Layout><Projects /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/configuration" element={
          <ProtectedRoute>
            <Layout><Configuration /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/analysis/:id" element={
          <ProtectedRoute>
            <Layout><RunDetail /></Layout>
          </ProtectedRoute>
        } />
        
        {/* Fallback for unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
