import { useState } from 'react'
import {
    Box,
    Typography,
    Button,
    Fab,
    Grid,
    Card,
    CardContent,
} from '@mui/material'
import RoleCard from '../components/roles/RoleCard'
import JobDetailsSideSheet from '../components/roles/JobDetailsSideSheet'
import { mockJobs, Job } from '../mocks/data'

export default function DashboardPage() {
    const [selectedJob, setSelectedJob] = useState<Job | null>(null)
    const [sideSheetOpen, setSideSheetOpen] = useState(false)

    const handleJobClick = (job: Job) => {
        setSelectedJob(job)
        setSideSheetOpen(true)
    }

    const handleCloseSideSheet = () => {
        setSideSheetOpen(false)
    }

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
                            {mockJobs.length} technical roles identified based on your profile scan
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
                <Grid container spacing={3}>
                    {mockJobs.map((job) => (
                        <Grid item xs={12} md={6} lg={4} key={job.id}>
                            <RoleCard job={job} onClick={() => handleJobClick(job)} />
                        </Grid>
                    ))}

                    {/* Placeholder Card (pending scrape) */}
                    <Grid item xs={12} md={6} lg={4}>
                        <Card
                            sx={{
                                bgcolor: 'rgba(248, 247, 245, 0.5)',
                                border: '2px dashed',
                                borderColor: 'divider',
                                minHeight: 220,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <CardContent sx={{ textAlign: 'center' }}>
                                <span
                                    className="material-symbols-outlined"
                                    style={{ fontSize: 40, color: '#cbd5e1', marginBottom: 8 }}
                                >
                                    work_outline
                                </span>
                                <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 700 }}>
                                    Pending Scrape Results...
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
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
                    <span>BUILD: v0.4.2-alpha</span>
                    <span>ENV: STAGING_WIREFRAME</span>
                    <span>MD3_GRID_8DP</span>
                </Box>
                <span>CAREERGOLD DASHBOARD • BLUEPRINT MODE</span>
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
