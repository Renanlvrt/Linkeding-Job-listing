import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
    Box,
    IconButton,
    Tooltip,
    Avatar,
} from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'

// Navigation items matching Stitch wireframe
const navItems = [
    { icon: 'dashboard', label: 'Dashboard', path: '/dashboard' },
    { icon: 'radar', label: 'Lead Scraper', path: '/scraper' },
    { icon: 'search', label: 'Search', path: '/search' },
    { icon: 'work', label: 'Roles', path: '/roles' },
    { icon: 'description', label: 'Applications', path: '/applications' },
    { icon: 'person', label: 'CV', path: '/cv' },
    { icon: 'settings', label: 'Settings', path: '/settings' },
]

export default function NavigationRail() {
    const navigate = useNavigate()
    const location = useLocation()
    const [hoveredItem, setHoveredItem] = useState<string | null>(null)
    const { user, signOut } = useAuth()

    const isActive = (path: string) => location.pathname.startsWith(path)

    const handleLogout = async () => {
        await signOut()
        navigate('/login')
    }

    // Get user initial for avatar
    const userInitial = user?.email?.charAt(0).toUpperCase() || 'G'

    return (
        <Box
            component="aside"
            sx={{
                width: 80,
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                py: 3,
                borderRight: 1,
                borderColor: 'divider',
                bgcolor: 'background.paper',
                position: 'fixed',
                left: 0,
                top: 0,
                zIndex: 1200,
            }}
        >
            {/* Logo */}
            <Box
                sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    bgcolor: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    mb: 5,
                    cursor: 'pointer',
                }}
                onClick={() => navigate('/dashboard')}
            >
                <span className="material-symbols-outlined">auto_awesome</span>
            </Box>

            {/* Navigation Items */}
            <Box
                component="nav"
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1,
                    flex: 1,
                }}
            >
                {navItems.map((item) => {
                    const active = isActive(item.path)
                    const hovered = hoveredItem === item.path

                    return (
                        <Tooltip key={item.path} title={item.label} placement="right">
                            <Box
                                sx={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    gap: 0.5,
                                    cursor: 'pointer',
                                }}
                                onMouseEnter={() => setHoveredItem(item.path)}
                                onMouseLeave={() => setHoveredItem(null)}
                                onClick={() => navigate(item.path)}
                            >
                                <IconButton
                                    sx={{
                                        width: 40,
                                        height: 40,
                                        borderRadius: 3,
                                        bgcolor: active ? 'primary.main' : hovered ? 'primary.light' : 'transparent',
                                        color: active ? 'white' : hovered ? 'primary.main' : 'text.secondary',
                                        '&:hover': {
                                            bgcolor: active ? 'primary.main' : 'rgba(183, 134, 11, 0.1)',
                                        },
                                        transition: 'all 0.2s ease',
                                    }}
                                >
                                    <span className="material-symbols-outlined">{item.icon}</span>
                                </IconButton>
                            </Box>
                        </Tooltip>
                    )
                })}
            </Box>

            {/* User Avatar (bottom) */}
            <Box sx={{ mt: 'auto' }}>
                <Tooltip title={user ? 'Sign out' : 'Sign in'} placement="right">
                    <IconButton
                        onClick={user ? handleLogout : () => navigate('/login')}
                        sx={{
                            width: 40,
                            height: 40,
                            borderRadius: 3,
                            color: 'text.secondary',
                            '&:hover': {
                                bgcolor: 'rgba(183, 134, 11, 0.1)',
                                color: 'primary.main',
                            },
                        }}
                    >
                        <span className="material-symbols-outlined">{user ? 'logout' : 'login'}</span>
                    </IconButton>
                </Tooltip>
            </Box>
            <Tooltip title={user?.email || 'Guest'} placement="right">
                <Avatar
                    sx={{
                        width: 40,
                        height: 40,
                        mt: 2,
                        border: 2,
                        borderColor: user ? 'primary.main' : 'divider',
                        bgcolor: user ? 'primary.light' : 'grey.300',
                        cursor: 'pointer',
                        fontSize: '1rem',
                        fontWeight: 600,
                    }}
                    onClick={() => navigate(user ? '/settings' : '/login')}
                >
                    {userInitial}
                </Avatar>
            </Tooltip>
        </Box>
    )
}
