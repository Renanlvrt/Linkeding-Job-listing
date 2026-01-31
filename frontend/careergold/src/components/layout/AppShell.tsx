import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import NavigationRail from './NavigationRail'
import TopAppBar from './TopAppBar'

export default function AppShell() {
    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Navigation Rail (fixed left) */}
            <NavigationRail />

            {/* Main Content Area */}
            <Box
                component="main"
                sx={{
                    flex: 1,
                    ml: '80px', // Offset for fixed nav rail
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: '100vh',
                    bgcolor: 'background.default',
                }}
            >
                {/* Top App Bar */}
                <TopAppBar />

                {/* Page Content */}
                <Box
                    sx={{
                        flex: 1,
                        position: 'relative',
                        overflow: 'auto',
                    }}
                >
                    <Outlet />
                </Box>
            </Box>
        </Box>
    )
}
