import { useLocation } from 'react-router-dom'
import {
    Box,
    AppBar,
    Toolbar,
    Typography,
    InputBase,
    IconButton,
    Badge,
} from '@mui/material'

// Page titles for different routes
const pageTitles: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/search': 'Search',
    '/roles': 'Roles',
    '/applications': 'Applications',
    '/cv': 'CV Profile',
    '/settings': 'Settings',
}

export default function TopAppBar() {
    const location = useLocation()

    // Get page title from path
    const getPageTitle = () => {
        const basePath = '/' + location.pathname.split('/')[1]
        return pageTitles[basePath] || 'CareerGold'
    }

    return (
        <AppBar
            position="sticky"
            elevation={0}
            sx={{
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(12px)',
                borderBottom: 1,
                borderColor: 'divider',
            }}
        >
            <Toolbar sx={{ px: 4, py: 1.5 }}>
                {/* Page Title with Icon */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <span
                        className="material-symbols-outlined"
                        style={{ color: '#9ca3af', fontSize: 20 }}
                    >
                        dashboard
                    </span>
                    <Typography
                        variant="h2"
                        component="h1"
                        sx={{
                            color: 'text.primary',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            fontSize: '1.25rem',
                        }}
                    >
                        {getPageTitle()}
                    </Typography>
                </Box>

                <Box sx={{ flexGrow: 1 }} />

                {/* Global Search */}
                <Box
                    sx={{
                        display: { xs: 'none', md: 'flex' },
                        alignItems: 'center',
                        gap: 1,
                        px: 2,
                        py: 1,
                        bgcolor: 'grey.100',
                        borderRadius: 2,
                        border: 1,
                        borderColor: 'divider',
                        minWidth: 250,
                        mr: 3,
                        '&:focus-within': {
                            borderColor: 'primary.main',
                            boxShadow: '0 0 0 2px rgba(183, 134, 11, 0.1)',
                        },
                    }}
                >
                    <span
                        className="material-symbols-outlined"
                        style={{ color: '#9ca3af', fontSize: 20 }}
                    >
                        search
                    </span>
                    <InputBase
                        placeholder="Global search..."
                        sx={{
                            flex: 1,
                            fontSize: '0.875rem',
                            '& input::placeholder': {
                                color: 'text.secondary',
                                opacity: 1,
                            },
                        }}
                    />
                </Box>

                {/* Notifications */}
                <IconButton
                    sx={{
                        color: 'text.secondary',
                        '&:hover': {
                            bgcolor: 'grey.100',
                        },
                    }}
                >
                    <Badge
                        variant="dot"
                        color="error"
                        sx={{
                            '& .MuiBadge-dot': {
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                            },
                        }}
                    >
                        <span className="material-symbols-outlined">notifications</span>
                    </Badge>
                </IconButton>
            </Toolbar>
        </AppBar>
    )
}
