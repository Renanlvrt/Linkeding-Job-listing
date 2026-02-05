import { Box, Typography, Button, Fab, Grid, Card, CardContent, CircularProgress } from '@mui/material'
import RoleCard from '../components/roles/RoleCard'
import JobDetailsSideSheet from '../components/roles/JobDetailsSideSheet'
import { Job } from '../mocks/data'
import { useJobs } from '../hooks/useJobs'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function DashboardPage() {
    const [selectedJob, setSelectedJob] = useState<Job | null>(null)
    const [sideSheetOpen, setSideSheetOpen] = useState(false)
    const navigate = useNavigate()

    // Fetch real jobs from Supabase
    const { data: jobs, isLoading, error } = useJobs({ limit: 20 })

    const handleJobClick = (job: Job) => {
        setSelectedJob(job)
        setSideSheetOpen(true)
    }

    const handleCloseSideSheet = () => {
        setSideSheetOpen(false)
    }

    // Map Supabase jobs to the Job type expected by RoleCard
    const displayJobs: Job[] = (jobs || []).map(j => ({
        id: j.id,
        title: j.title,
        company: j.company,
        location: j.location || 'Remote',
        matchScore: j.match_score,
        applicants: j.applicants !== null ? j.applicants : (j.applicants_count || 0),
        postedAgo: j.posted_date || (j.scraped_at ? getTimeAgo(j.scraped_at) : 'Recently'),
        status: j.status as Job['status'],
        salaryRange: j.salary_range || undefined,
        description: j.description || j.snippet || undefined,
        link: j.apply_link || j.link, // Pass link for "Apply Now"
        skills: Array.isArray(j.skills_matched)
            ? j.skills_matched.map((s: string) => ({ name: s, matched: true }))
            : [],
    }))

    return (
        <Box sx={{ position: 'relative', minHeight: '100%' }}>
            {/* Page Heading */}
            <Box sx={{ px: 4, pt: 4, pb: 2 }}>
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { md: 'flex-end' }, gap: 2 }}>
                    <Box>
                        <Typography
                            variant="h1"
                            sx={{
                                color: 'text.primary',
                                fontSize: { xs: '2rem', md: '2.5rem' },
                            }}
                        >
                            Top Matches
                        </Typography>
                        <Typography variant="body1" sx={{ color: 'text.secondary', mt: 1, fontWeight: 500 }}>
                            {isLoading ? 'Loading...' : `${displayJobs.length} roles from Supabase database`}
                        </Typography>
                    </Box>
                    <Button
                        variant="outlined"
                        startIcon={<span className="material-symbols-outlined">tune</span>}
                        sx={{
                            height: 40,
                            px: 2,
                            borderColor: 'divider',
                            color: 'text.secondary',
                            bgcolor: 'background.paper',
                            '&:hover': {
                                bgcolor: 'grey.50',
                                borderColor: 'divider',
                            },
                        }}
                    >
                        Filter Results
                    </Button>
                </Box>
            </Box>

            {/* Job Grid */}
            <Box sx={{ p: 4 }}>
                {isLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                        <CircularProgress />
                    </Box>
                ) : error ? (
                    <Typography color="error">Failed to load jobs: {String(error)}</Typography>
                ) : displayJobs.length === 0 ? (
                    <Card sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 48, color: '#9ca3af' }}>search_off</span>
                        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>No jobs in database yet</Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                            Head to the Lead Scraper to discover and save jobs.
                        </Typography>
                        <Button variant="contained" onClick={() => navigate('/scraper')}>
                            Go to Scraper
                        </Button>
                    </Card>
                ) : (
                    <Grid container spacing={3}>
                        {displayJobs.map((job) => (
                            <Grid item xs={12} md={6} lg={4} key={job.id}>
                                <RoleCard job={job} onClick={() => handleJobClick(job)} />
                            </Grid>
                        ))}
                    </Grid>
                )}
            </Box>

            {/* Floating Action Button (FAB) */}
            <Box
                sx={{
                    position: 'fixed',
                    bottom: 40,
                    right: 40,
                    zIndex: 30,
                }}
            >
                <Fab
                    variant="extended"
                    color="secondary"
                    onClick={() => navigate('/scraper')}
                    sx={{
                        bgcolor: '#6750A4',
                        '&:hover': {
                            bgcolor: '#5840A0',
                        },
                        px: 3,
                        py: 1.5,
                        fontWeight: 700,
                        textTransform: 'none',
                        boxShadow: '0 4px 16px rgba(103, 80, 164, 0.3)',
                    }}
                >
                    <span className="material-symbols-outlined" style={{ marginRight: 8 }}>data_object</span>
                    RUN SCRAPE
                </Fab>
            </Box>

            {/* Blueprint Footer */}
            <Box
                component="footer"
                sx={{
                    mt: 'auto',
                    p: 4,
                    borderTop: 1,
                    borderColor: 'divider',
                    bgcolor: 'rgba(248, 247, 245, 0.5)',
                    display: 'flex',
                    flexDirection: { xs: 'column', md: 'row' },
                    justifyContent: 'space-between',
                    color: 'text.secondary',
                    fontSize: '0.625rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    gap: 2,
                }}
            >
                <Box sx={{ display: 'flex', gap: 4 }}>
                    <span>BUILD: v0.5.0-supabase</span>
                    <span>ENV: {import.meta.env.DEV ? 'DEVELOPMENT' : 'PRODUCTION'}</span>
                    <span>MD3_GRID_8DP</span>
                </Box>
                <span>CAREERGOLD DASHBOARD • SUPABASE CONNECTED</span>
            </Box>

            {/* Job Details Side Sheet */}
            <JobDetailsSideSheet
                job={selectedJob}
                open={sideSheetOpen}
                onClose={handleCloseSideSheet}
            />
        </Box>
    )
}

// Helper function
function getTimeAgo(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
    return `${Math.floor(seconds / 604800)}w ago`
}
