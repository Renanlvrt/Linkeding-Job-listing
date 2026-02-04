import React from 'react'
import ReactDOM from 'react-dom/client'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import theme from './theme/theme'
import { AuthProvider } from './contexts/AuthContext'
import { supabase } from './lib/supabase'
import './index.css'

// Development mode: Check Supabase configuration
if (import.meta.env.DEV) {
    supabase.auth.getSession().then(({ error }) => {
        if (error?.message.includes('redirect') || error?.message.includes('URL')) {
            console.error('❌ SUPABASE CONFIG ERROR: Redirect URL mismatch')
            console.error('→ Check Supabase Dashboard → Authentication → URL Configuration')
            console.error(`→ Add: ${window.location.origin}/auth/callback`)
            console.error('→ See SUPABASE_CONFIG.md for full setup guide')
        }
    })
}

// Create a client for React Query
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            refetchOnWindowFocus: false,
        },
    },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <BrowserRouter>
                    <AuthProvider>
                        <App />
                    </AuthProvider>
                </BrowserRouter>
            </ThemeProvider>
        </QueryClientProvider>
    </React.StrictMode>,
)
