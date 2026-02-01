/**
 * Frontend Security Utilities
 * =============================
 * XSS protection, safe rendering, and token management.
 */

// ============================================================
// HTML SANITIZATION (XSS Prevention)
// ============================================================

/**
 * Sanitize HTML to prevent XSS attacks.
 * Use this for ANY user-generated or external content before rendering.
 * 
 * For full protection, install DOMPurify:
 *   npm install dompurify @types/dompurify
 * 
 * Then import and use:
 *   import DOMPurify from 'dompurify'
 *   const clean = DOMPurify.sanitize(dirty)
 */

// Basic sanitizer (use DOMPurify for production)
export function sanitizeText(text: string): string {
    if (!text) return ''

    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;')
}

/**
 * Validate URLs to prevent javascript: attacks
 */
export function sanitizeUrl(url: string): string {
    if (!url) return ''

    const trimmed = url.trim()

    // Only allow http/https
    if (!/^https?:\/\//i.test(trimmed)) {
        return ''
    }

    // Block dangerous patterns
    const dangerousPatterns = [
        /javascript:/i,
        /data:/i,
        /vbscript:/i,
        /file:/i,
    ]

    for (const pattern of dangerousPatterns) {
        if (pattern.test(trimmed)) {
            return ''
        }
    }

    return trimmed
}

// ============================================================
// SAFE RENDERING COMPONENTS
// ============================================================

import { ReactNode } from 'react'

interface SafeTextProps {
    children: string
    className?: string
}

/**
 * Component that safely renders text content.
 * React already escapes text, but this makes intent explicit.
 */
export function SafeText({ children, className }: SafeTextProps): ReactNode {
    return <span className={ className }> { sanitizeText(children) } </span>
}

/**
 * Safely render job descriptions.
 * Use this for any scraped content.
 */
export function sanitizeJobData(job: Record<string, unknown>): Record<string, unknown> {
    return {
        ...job,
        title: sanitizeText(String(job.title || '')),
        company: sanitizeText(String(job.company || '')),
        location: sanitizeText(String(job.location || '')),
        snippet: sanitizeText(String(job.snippet || '')),
        description: sanitizeText(String(job.description || '')),
        link: sanitizeUrl(String(job.link || '')),
    }
}

// ============================================================
// TOKEN STORAGE (Supabase handles this, but document best practices)
// ============================================================

/**
 * Token Storage Best Practices:
 * 
 * 1. Supabase stores tokens in localStorage by default.
 *    This is vulnerable to XSS but necessary for SPAs.
 * 
 * 2. MITIGATIONS we implement:
 *    - Strict CSP to block inline scripts
 *    - Input sanitization everywhere
 *    - Short token expiry (1 hour)
 *    - Refresh token rotation
 * 
 * 3. For higher security, configure Supabase to use
 *    httpOnly cookies (requires custom auth flow).
 */

// Check if Supabase auth is configured properly
export function validateAuthConfig(): { valid: boolean; issues: string[] } {
    const issues: string[] = []

    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
    const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

    if (!supabaseUrl) {
        issues.push('VITE_SUPABASE_URL is not configured')
    }

    if (!supabaseKey) {
        issues.push('VITE_SUPABASE_ANON_KEY is not configured')
    }

    // Check we're not accidentally exposing service key
    if (supabaseKey?.includes('service_role')) {
        issues.push('CRITICAL: Service key exposed in frontend!')
    }

    return {
        valid: issues.length === 0,
        issues
    }
}

// ============================================================
// CSP NONCE HELPER (for inline scripts if needed)
// ============================================================

/**
 * Generate a CSP nonce for inline scripts.
 * In production, this should come from the server.
 */
export function generateNonce(): string {
    const array = new Uint8Array(16)
    crypto.getRandomValues(array)
    return btoa(String.fromCharCode(...array))
}
