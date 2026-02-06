import { Box, Typography, Button, Fab, Grid, Card, CircularProgress } from '@mui/material'
import RoleCard from '../components/roles/RoleCard'
import JobDetailsSideSheet from '../components/roles/JobDetailsSideSheet'
import { Job } from '../mocks/data'
import { useJobs } from '../hooks/useJobs'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { mapDbJobToUi } from '../lib/utils'

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
    const displayJobs: Job[] = (jobs || []).map(mapDbJobToUi)

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
                            {isLoading ? 'Loading...' : `${displayJobs.length} roles found`}
                            {!isLoading && displayJobs.length >= 20 && (
                                <Button
                                    size="small"
                                    onClick={() => navigate('/roles')}
                                    sx={{ ml: 2, textTransform: 'none', fontWeight: 600 }}
                                >
                                    View All ({jobs?.length || 20}+)
                                </Button>
                            )}
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                            variant="outlined"
                            onClick={() => navigate('/roles')}
                            startIcon={<span className="material-symbols-outlined">list</span>}
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
                            All Roles
                        </Button>
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
                            Filter
                        </Button>
                    </Box>
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

                {!isLoading && displayJobs.length >= 20 && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                        <Button
                            variant="text"
                            color="primary"
                            onClick={() => navigate('/roles')}
                            sx={{ fontWeight: 700, fontSize: '0.875rem' }}
                        >
                            See all saved roles ({jobs?.length || 20}+)
                            <span className="material-symbols-outlined" style={{ marginLeft: 8 }}>arrow_forward</span>
                        </Button>
                    </Box>
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


