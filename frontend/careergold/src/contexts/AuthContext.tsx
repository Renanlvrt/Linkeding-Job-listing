/**
 * Authentication Context
 * =======================
 * Manages Supabase auth state across the application.
 * 
 * Session Storage Strategy:
 * - Relies on supabase-js client for automatic token management
 * - Tokens stored in localStorage (XSS risk mitigated by sanitization)
 * - This context does NOT store tokens directly, only reads from client
 * - Auto-refresh handled by Supabase client
 * 
 * SECURITY WARNING:
 * - One XSS vulnerability = full token compromise
 * - Never use dangerouslySetInnerHTML
 * - Always sanitize user/scraped content
 */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { buildLoginUrl } from '../utils/redirectValidation'

interface AuthContextType {
    user: User | null
    session: Session | null
    loading: boolean
    signOut: () => Promise<void>
    redirectToLogin: (currentPath: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setUser(session?.user ?? null)
            setLoading(false)
        })

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (_event, session) => {
                setSession(session)
                setUser(session?.user ?? null)
                setLoading(false)
            }
        )

        return () => subscription.unsubscribe()
    }, [])

    /**
     * Sign out user and clear session.
     * Calls Supabase to invalidate refresh tokens.
     */
    const signOut = async () => {
        await supabase.auth.signOut()
        // State will be cleared automatically by onAuthStateChange
    }

    /**
     * Redirect to login with `?next=` parameter for post-login redirect.
     * Used for session expiry and 401 error handling.
     * 
     * @param currentPath - Path to return to after login
     */
    const redirectToLogin = (currentPath: string) => {
        const loginUrl = buildLoginUrl(currentPath)
        window.location.href = loginUrl
    }

    return (
        <AuthContext.Provider value={{ user, session, loading, signOut, redirectToLogin }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
