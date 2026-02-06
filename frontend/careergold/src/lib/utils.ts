import { Job as DbJob } from './supabase'
import { Job as UiJob } from '../mocks/data'

export function mapDbJobToUi(j: DbJob): UiJob {
    return {
        id: j.id,
        title: j.title,
        company: j.company,
        location: j.location || 'Remote',
        matchScore: j.match_score,
        applicants: j.applicants !== null ? j.applicants : 0,
        postedAgo: getTimeAgo(j.scraped_at),
        status: j.status as UiJob['status'],
        description: j.description || undefined,
        link: j.link || undefined,
        skills: Array.isArray(j.skills_matched)
            ? j.skills_matched.map((s: string) => ({ name: s, matched: true }))
            : [],
        raw_data: j
    }
}

export function getTimeAgo(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (isNaN(date.getTime())) return 'Recently'
    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
    return `${Math.floor(seconds / 604800)}w ago`
}
