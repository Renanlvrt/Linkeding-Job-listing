import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/DashboardPage'
import LeadScraperPage from './pages/LeadScraperPage'
import SearchPage from './pages/SearchPage'
import RolesPage from './pages/RolesPage'
import ApplicationsPage from './pages/ApplicationsPage'
import CVPage from './pages/CVPage'
import SettingsPage from './pages/SettingsPage'
import LoginPage from './pages/LoginPage'
import AuthCallback from './pages/AuthCallback'

function App() {
    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route element={<AppShell />}>
                    <Route path="/" element={<Navigate to="/login" replace />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/scraper" element={<LeadScraperPage />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/roles" element={<RolesPage />} />
                    <Route path="/roles/:id" element={<RolesPage />} />
                    <Route path="/applications" element={<ApplicationsPage />} />
                    <Route path="/cv" element={<CVPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Route>
            </Routes>
        </Box>
    )
}

export default App
