/**
 * Jobs Hook
 * ==========
 * React Query hooks for fetching and mutating jobs from Supabase.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase, Job } from '../lib/supabase'

// Fetch all jobs with optional filters
export function useJobs(options?: {
    status?: Job['status']
    minMatchScore?: number
    limit?: number
}) {
    return useQuery({
        queryKey: ['jobs', options],
        queryFn: async () => {
            let query = supabase
                .from('jobs')
                .select('*')
                .order('match_score', { ascending: false })

            if (options?.status) {
                query = query.eq('status', options.status)
            }
            if (options?.minMatchScore) {
                query = query.gte('match_score', options.minMatchScore)
            }
            if (options?.limit) {
                query = query.limit(options.limit)
            }

            const { data, error } = await query

            if (error) {
                console.error('Error fetching jobs:', error)
                throw error
            }

            return data as Job[]
        },
    })
}

// Fetch a single job by ID
export function useJob(id: string) {
    return useQuery({
        queryKey: ['job', id],
        queryFn: async () => {
            const { data, error } = await supabase
                .from('jobs')
                .select('*')
                .eq('id', id)
                .single()

            if (error) {
                console.error('Error fetching job:', error)
                throw error
            }

            return data as Job
        },
        enabled: !!id,
    })
}

// Update job status (e.g., SAVED, APPLIED)
export function useUpdateJobStatus() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ id, status }: { id: string; status: Job['status'] }) => {
            const { data, error } = await supabase
                .from('jobs')
                .update({ status })
                .eq('id', id)
                .select()
                .single()

            if (error) throw error
            return data as Job
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['jobs'] })
        },
    })
}

// Save scraped jobs to Supabase (batch insert)
export function useSaveScrapedJobs() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (jobs: Partial<Job>[]) => {
            // Map scraped jobs to database format
            const dbJobs = jobs.map(job => ({
                external_id: job.external_id || null,
                title: job.title,
                company: job.company,
                location: job.location || null,
                link: job.link || null,
                applicants: job.applicants || null,
                source: job.source || 'linkedin',
                match_score: job.match_score || 0,
                status: 'NEW' as const,
            }))

            const { data, error } = await supabase
                .from('jobs')
                .upsert(dbJobs, {
                    onConflict: 'external_id',
                    ignoreDuplicates: true,
                })
                .select()

            if (error) throw error
            return data as Job[]
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['jobs'] })
        },
    })
}
