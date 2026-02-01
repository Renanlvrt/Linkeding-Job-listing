/**
 * Login Page
 * ===========
 * Magic link authentication with Supabase.
 */

import { useState } from 'react'
import { Box, Card, CardContent, Typography, TextField, Button, Alert, CircularProgress } from '@mui/material'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
    const { signInWithMagicLink, user } = useAuth()
    const navigate = useNavigate()

    // If already logged in, redirect to dashboard
    if (user) {
        navigate('/dashboard')
        return null
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!email.trim()) return

        setLoading(true)
        setMessage(null)

        const { error } = await signInWithMagicLink(email)

        setLoading(false)

        if (error) {
            setMessage({ type: 'error', text: error.message })
        } else {
            setMessage({ type: 'success', text: 'Check your email for the magic link!' })
        }
    }

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
            <Card sx={{ maxWidth: 420, width: '100%', borderRadius: 4, boxShadow: '0 8px 32px rgba(0,0,0,0.08)' }}>
                <CardContent sx={{ p: 4 }}>
                    {/* Logo / Brand */}
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Box
                            sx={{
                                width: 64,
                                height: 64,
                                borderRadius: '50%',
                                bgcolor: 'primary.main',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mx: 'auto',
                                mb: 2,
                            }}
                        >
                            <span className="material-symbols-outlined" style={{ fontSize: 32, color: 'white' }}>
                                work
                            </span>
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
                            CareerGold
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
                            AI-powered job discovery & application
                        </Typography>
                    </Box>

                    {/* Login Form */}
                    <form onSubmit={handleSubmit}>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                            Sign in with Magic Link
                        </Typography>

                        <TextField
                            fullWidth
                            type="email"
                            label="Email address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            disabled={loading}
                            sx={{ mb: 2 }}
                        />

                        {message && (
                            <Alert severity={message.type} sx={{ mb: 2 }}>
                                {message.text}
                            </Alert>
                        )}

                        <Button
                            fullWidth
                            type="submit"
                            variant="contained"
                            size="large"
                            disabled={loading || !email.trim()}
                            sx={{
                                py: 1.5,
                                fontWeight: 600,
                                textTransform: 'none',
                            }}
                        >
                            {loading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'Send Magic Link'
                            )}
                        </Button>

                        <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 2, color: 'text.secondary' }}>
                            We'll email you a magic link for password-free sign in.
                        </Typography>
                    </form>

                    {/* Divider */}
                    <Box sx={{ my: 3, borderTop: 1, borderColor: 'divider' }} />

                    {/* Demo Mode */}
                    <Button
                        fullWidth
                        variant="outlined"
                        size="large"
                        onClick={() => navigate('/dashboard')}
                        sx={{
                            py: 1.5,
                            fontWeight: 600,
                            textTransform: 'none',
                            borderColor: 'divider',
                            color: 'text.secondary',
                        }}
                    >
                        Continue as Guest (Demo Mode)
                    </Button>
                </CardContent>
            </Card>
        </Box>
    )
}
