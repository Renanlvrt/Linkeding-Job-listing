import {
    Box,
    Typography,
    TextField,
    Button,
    Card,
    CardContent,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
    const navigate = useNavigate()

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault()
        navigate('/dashboard')
    }

    return (
        <Box
            sx={{
                minHeight: '100vh',
                bgcolor: 'background.default',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                p: 3,
            }}
        >
            <Card sx={{ width: '100%', maxWidth: 400 }}>
                <CardContent sx={{ p: 4 }}>
                    {/* Logo */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 4 }}>
                        <Box
                            sx={{
                                width: 48,
                                height: 48,
                                borderRadius: 2,
                                bgcolor: 'primary.main',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                mr: 2,
                            }}
                        >
                            <span className="material-symbols-outlined">auto_awesome</span>
                        </Box>
                        <Typography variant="h3" sx={{ fontWeight: 800 }}>
                            CareerGold
                        </Typography>
                    </Box>

                    <Typography variant="body1" sx={{ color: 'text.secondary', textAlign: 'center', mb: 4 }}>
                        Sign in to discover your perfect career matches
                    </Typography>

                    {/* Login Form */}
                    <Box component="form" onSubmit={handleLogin} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <TextField
                            label="Email"
                            type="email"
                            fullWidth
                            defaultValue="renan.lavirotte@gmail.com"
                        />
                        <TextField
                            label="Password"
                            type="password"
                            fullWidth
                            defaultValue="••••••••"
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            fullWidth
                            sx={{ height: 48 }}
                        >
                            Sign In
                        </Button>
                    </Box>

                    <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', mt: 3 }}>
                        Demo mode • Click Sign In to continue
                    </Typography>
                </CardContent>
            </Card>
        </Box>
    )
}
