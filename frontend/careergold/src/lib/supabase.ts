/**
 * Supabase Client Configuration
 * ==============================
 * Singleton client for connecting to Supabase from the frontend.
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Supabase environment variables not set. Using mock data.')
}

export const supabase = createClient(
    supabaseUrl || 'https://placeholder.supabase.co',
    supabaseAnonKey || 'placeholder-key'
)

// Database types (matches db_schema.sql)
export interface Job {
    id: string
    external_id: string | null
    title: string
    company: string
    location: string | null
    description: string | null
    link: string | null
    applicants: number | null
    posted_at: string | null
    source: string
    match_score: number
    skills_matched: string[]
    status: 'NEW' | 'SAVED' | 'APPLIED' | 'REJECTED' | 'EXPIRED'
    scraped_at: string
    created_at: string
    updated_at: string
}

export interface Application {
    id: string
    user_id: string
    job_id: string
    cv_version: string | null
    status: 'QUEUED' | 'SUBMITTING' | 'SUBMITTED' | 'REJECTED' | 'INTERVIEW' | 'OFFER' | 'MANUAL'
    applied_at: string | null
    notes: string | null
    created_at: string
    updated_at: string
}

export interface User {
    id: string
    email: string
    full_name: string | null
    skills: string[]
    location_pref: string | null
    job_title_pref: string | null
    created_at: string
    updated_at: string
}
