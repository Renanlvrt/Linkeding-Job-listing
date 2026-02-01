/**
 * Applications Hook
 * ==================
 * React Query hooks for managing job applications.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase, Application } from '../lib/supabase'

// Fetch all applications for current user
export function useApplications() {
    return useQuery({
        queryKey: ['applications'],
        queryFn: async () => {
            const { data, error } = await supabase
                .from('applications')
                .select(`
                    *,
                    job:jobs(*)
                `)
                .order('created_at', { ascending: false })

            if (error) {
                console.error('Error fetching applications:', error)
                throw error
            }

            return data
        },
    })
}

// Create a new application
export function useCreateApplication() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (application: {
            job_id: string
            cv_version?: string
            notes?: string
        }) => {
            // Get current user
            const { data: { user } } = await supabase.auth.getUser()
            if (!user) throw new Error('Not authenticated')

            const { data, error } = await supabase
                .from('applications')
                .insert({
                    user_id: user.id,
                    job_id: application.job_id,
                    cv_version: application.cv_version || null,
                    notes: application.notes || null,
                    status: 'QUEUED',
                })
                .select()
                .single()

            if (error) throw error
            return data as Application
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['applications'] })
            queryClient.invalidateQueries({ queryKey: ['jobs'] })
        },
    })
}

// Update application status
export function useUpdateApplicationStatus() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ id, status }: { id: string; status: Application['status'] }) => {
            const { data, error } = await supabase
                .from('applications')
                .update({
                    status,
                    applied_at: status === 'SUBMITTED' ? new Date().toISOString() : undefined,
                })
                .eq('id', id)
                .select()
                .single()

            if (error) throw error
            return data as Application
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['applications'] })
        },
    })
}
