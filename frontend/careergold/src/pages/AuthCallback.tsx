/**
 * Auth Callback Page
 * ==================
 * Handles OAuth/magic link redirects from Supabase.
 * 
 * Flow:
 * 1. User clicks magic link / completes OAuth
 * 2. Supabase redirects to this page
 * 3. Hook extracts session and validates redirect
 * 4. Page auto-redirects to original destination or dashboard
 * 
 * Security:
 * - No tokens displayed in UI or errors
 * - Generic error messages
 * - Protected against open redirects
 */

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, CircularProgress, Typography, Button, Alert } from '@mui/material'
import { useAuthCallback } from '../hooks/useAuthCallback'

export default function AuthCallback() {
    const navigate = useNavigate()
    const { status, redirectPath, errorMessage } = useAuthCallback()

    useEffect(() => {
        // Auto-redirect on success
        if (status === 'success') {
            navigate(redirectPath, { replace: true })
        }
    }, [status, redirectPath, navigate])

    // Loading state
    if (status === 'loading') {
        return (
            <Box
                sx={{
                    minHeight: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'surfaceVariant.main',
                    gap: 3,
                }}
            >
                <CircularProgress size={48} />
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Completing sign in...
                </Typography>
            </Box>
        )
    }

    // Error state
    if (status === 'error') {
        return (
            <Box
                sx={{
                    minHeight: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'surfaceVariant.main',
                    p: 3,
                }}
            >
                <Box sx={{ maxWidth: 420, width: '100%' }}>
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {errorMessage || 'Authentication failed. Please try again.'}
                    </Alert>
                    <Button
                        fullWidth
                        variant="contained"
                        onClick={() => navigate('/login')}
                        sx={{
                            py: 1.5,
                            fontWeight: 600,
                        }}
                    >
                        Return to Login
                    </Button>
                </Box>
            </Box>
        )
    }

    // Should never reach (auto-redirects on success)
    return null
}
