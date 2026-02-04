/**
 * Login Page
 * ===========
 * Uses official Supabase Auth UI for secure authentication.
 * 
 * Features:
 * - Password login
 * - Magic link email
 * - Branded with Supabase for trust
 * - Auto-redirects to ?next= param after login
 * 
 * Security:
 * - Leverages Supabase's built-in XSS/CSRF protection
 * - No custom password handling
 * - Rate-limited by Supabase (30 attempts/hour)
 */

import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Box, Typography, Container, Paper } from '@mui/material'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { supabase } from '../lib/supabase'
import { useAuth } from '../contexts/AuthContext'
import { sanitizeNextPath } from '../utils/redirectValidation'

export default function LoginPage() {
    const navigate = useNavigate()
    const { user } = useAuth()
    const [searchParams] = useSearchParams()

    // Get redirect target from URL
    const next = sanitizeNextPath(searchParams.get('next'))

    // Redirect if already logged in
    useEffect(() => {
        if (user) {
            navigate(next, { replace: true })
        }
    }, [user, next, navigate])

    // Show login UI if not authenticated
    if (user) return null

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'surfaceVariant.main',
                p: 2,
            }}
        >
            <Container maxWidth="sm">
                <Paper
                    elevation={0}
                    sx={{
                        p: 4,
                        borderRadius: 3,
                        border: 1,
                        borderColor: 'divider',
                    }}
                >
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
                            Welcome to CareerGold
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                            Sign in to continue
                        </Typography>
                    </Box>

                    {/* Supabase Auth UI */}
                    <Auth
                        supabaseClient={supabase}
                        appearance={{
                            theme: ThemeSupa,
                            variables: {
                                default: {
                                    colors: {
                                        brand: '#6750A4',
                                        brandAccent: '#5840A0',
                                    },
                                    radii: {
                                        borderRadiusButton: '8px',
                                        buttonBorderRadius: '8px',
                                        inputBorderRadius: '8px',
                                    },
                                },
                            },
                        }}
                        theme="light"
                        providers={[]} // No social login for now
                        redirectTo={`${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`}
                        view="sign_in" // Start with sign in view
                        showLinks={true} // Show "Don't have an account? Sign up"
                    />

                    {/* Security badge */}
                    <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>lock</span>
                            Secure login powered by Supabase
                        </Typography>
                    </Box>
                </Paper>
            </Container>
        </Box>
    )
}
