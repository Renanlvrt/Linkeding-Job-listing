/**
 * useAuthCallback Hook
 * =====================
 * Handles OAuth/magic link callback flow securely.
 * 
 * Responsibilities:
 * 1. Parse URL for session/error
 * 2. Finalize auth via supabase.auth.getSession()
 * 3. Validate redirect parameter
 * 4. Return state machine for UI
 * 
 * Security:
 * - Never exposes tokens in errors
 * - Logs failures (generic message only)
 * - Handles edge cases: malformed URL, expired, missing params
 */

import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { sanitizeNextPath } from '../utils/redirectValidation'

export type AuthCallbackStatus = 'loading' | 'success' | 'error'

export interface AuthCallbackState {
    status: AuthCallbackStatus
    redirectPath: string
    errorMessage?: string
}

/**
 * Hook to handle Supabase auth callback flow.
 * 
 * @returns State object with status, redirectPath, and optional error
 * 
 * @example
 * const { status, redirectPath } = useAuthCallback()
 * 
 * if (status === 'loading') return <Spinner />
 * if (status === 'error') return <Error />
 * if (status === 'success') navigate(redirectPath)
 */
export function useAuthCallback(): AuthCallbackState {
    const [state, setState] = useState<AuthCallbackState>({
        status: 'loading',
        redirectPath: '/dashboard',
    })

    useEffect(() => {
        const handleCallback = async () => {
            try {
                // Parse URL params for redirect target
                const urlParams = new URLSearchParams(window.location.search)
                const next = sanitizeNextPath(urlParams.get('next'))

                // Get session from Supabase (handles hash parsing automatically)
                const { data, error } = await supabase.auth.getSession()

                if (error || !data.session) {
                    // Log technical error for developers (console only)
                    console.error('[Auth] Callback failed:', error?.message || 'No session')

                    // User-friendly error (no technical details)
                    setState({
                        status: 'error',
                        redirectPath: '/login',
                        errorMessage: 'Authentication failed. Please try logging in again.',
                    })
                    return
                }

                // Success: redirect to original target
                setState({
                    status: 'success',
                    redirectPath: next,
                })
            } catch (err) {
                // Unexpected error (malformed URL, network failure, etc.)
                console.error('[Auth] Unexpected callback error:', err)

                setState({
                    status: 'error',
                    redirectPath: '/login',
                    errorMessage: 'An unexpected error occurred. Please try again.',
                })
            }
        }

        handleCallback()
    }, [])

    return state
}
