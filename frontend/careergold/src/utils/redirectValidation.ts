/**
 * Redirect Validation Utility
 * ============================
 * Centralized protection against open redirect attacks.
 * 
 * Usage:
 * - AuthCallback: Validate `next` param before redirecting
 * - ProtectedRoute: Validate redirect target
 * - redirectToLogin: Build safe login URLs with next param
 * 
 * Security:
 * - Blocks absolute URLs (https://evil.com)
 * - Blocks protocol-relative URLs (//evil.com)
 * - Allows only relative paths starting with /
 * - Optional: Allowlist known routes
 */

const ALLOWED_ROUTES = [
    '/dashboard',
    '/leads',
    '/roles',
    '/applications',
    '/cv',
    '/settings',
]

/**
 * Sanitize and validate a redirect path to prevent open redirect vulnerabilities.
 * 
 * @param next - The redirect path from URL params (e.g., ?next=/dashboard)
 * @returns A safe redirect path (defaults to /dashboard if invalid)
 * 
 * @example
 * sanitizeNextPath('/leads') // '/leads'
 * sanitizeNextPath('https://evil.com') // '/dashboard' (blocked)
 * sanitizeNextPath('//evil.com') // '/dashboard' (blocked)
 * sanitizeNextPath(null) // '/dashboard' (default)
 */
export function sanitizeNextPath(next: string | null): string {
    // Default fallback
    if (!next) return '/dashboard'

    // Block absolute URLs and protocol-relative URLs
    if (next.includes('://') || next.startsWith('//')) {
        console.warn('[Security] Blocked absolute redirect:', next)
        return '/dashboard'
    }

    // Must start with /
    if (!next.startsWith('/')) {
        console.warn('[Security] Blocked non-relative redirect:', next)
        return '/dashboard'
    }

    // Allowlist check (optional: can be disabled for more flexibility)
    const isAllowed = ALLOWED_ROUTES.some(route => next.startsWith(route))
    if (!isAllowed) {
        console.warn('[Security] Blocked non-allowlisted redirect:', next)
        return '/dashboard'
    }

    return next
}

/**
 * Build a login URL with a safe next parameter.
 * 
 * @param currentPath - Current page path to return to after login
 * @returns Login URL with sanitized next param
 * 
 * @example
 * buildLoginUrl('/leads') // '/login?next=/leads'
 * buildLoginUrl('https://evil.com') // '/login?next=/dashboard'
 */
export function buildLoginUrl(currentPath: string): string {
    const safePath = sanitizeNextPath(currentPath)
    return `/login?next=${encodeURIComponent(safePath)}`
}
