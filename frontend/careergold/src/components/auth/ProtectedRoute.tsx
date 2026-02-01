/**
 * Protected Route Component
 * ==========================
 * Wraps routes that require authentication.
 */

import { Navigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'

interface ProtectedRouteProps {
    children: React.ReactNode
    requireAuth?: boolean // Set to false to allow guest access but still show user if logged in
}

export default function ProtectedRoute({ children, requireAuth = false }: ProtectedRouteProps) {
    const { user, loading } = useAuth()
    const location = useLocation()

    // Show loading spinner while checking auth
    if (loading) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                }}
            >
                <CircularProgress />
            </Box>
        )
    }

    // If auth is required and user is not logged in, redirect to login
    if (requireAuth && !user) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return <>{children}</>
}
