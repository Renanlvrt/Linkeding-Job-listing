import {
    Card,
    CardContent,
    Box,
    Typography,
    Chip,
    IconButton,
    Tooltip,
} from '@mui/material'
import { Job } from '../../mocks/data'
import { SafeText } from '../../lib/security'
import { useUpdateJobStatus, useDeleteJob } from '../../hooks/useJobs'

interface RoleCardProps {
    job: Job
    onClick?: () => void
}

export default function RoleCard({ job, onClick }: RoleCardProps) {
    // Determine match badge color based on score
    const getMatchColor = (score: number) => {
        if (score >= 90) return { bg: 'rgba(103, 80, 164, 0.1)', text: '#6750A4', border: 'rgba(103, 80, 164, 0.2)' }
        if (score >= 70) return { bg: 'rgba(183, 134, 11, 0.1)', text: '#B7860B', border: 'rgba(183, 134, 11, 0.2)' }
        return { bg: 'rgba(148, 163, 184, 0.1)', text: '#64748B', border: 'rgba(148, 163, 184, 0.3)' }
    }

    const matchColor = getMatchColor(job.matchScore)
    const updateStatus = useUpdateJobStatus()
    const deleteJob = useDeleteJob()

    const isSaved = job.status === 'SAVED'

    const handleSaveToggle = (e: React.MouseEvent) => {
        e.stopPropagation()
        const newStatus = isSaved ? 'NEW' : 'SAVED'
        updateStatus.mutate({ id: job.id, status: newStatus })
    }

    const handleDelete = (e: React.MouseEvent) => {
        e.stopPropagation()
        if (window.confirm('Are you sure you want to delete this job?')) {
            deleteJob.mutate(job.id)
        }
    }

    // Icon based on job type
    const getIcon = (title: string) => {
        if (title.toLowerCase().includes('engineer') || title.toLowerCase().includes('developer')) return 'code'
        if (title.toLowerCase().includes('product')) return 'package_2'
        if (title.toLowerCase().includes('data')) return 'database'
        if (title.toLowerCase().includes('design')) return 'palette'
        return 'corporate_fare'
    }

    return (
        <Card
            sx={{
                bgcolor: 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                    transform: 'translateY(-2px)',
                },
            }}
            onClick={onClick}
        >
            <CardContent sx={{ p: 2.5 }}>
                {/* Header: Icon + Match Badge */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box
                        sx={{
                            width: 48,
                            height: 48,
                            borderRadius: 2,
                            bgcolor: 'grey.100',
                            border: 1,
                            borderColor: 'divider',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'text.secondary',
                        }}
                    >
                        <span className="material-symbols-outlined">{getIcon(job.title)}</span>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Tooltip title={isSaved ? "Unsave job" : "Save job"}>
                            <IconButton
                                size="small"
                                onClick={handleSaveToggle}
                                sx={{
                                    color: isSaved ? '#facc15' : 'text.disabled',
                                    '&:hover': { color: '#facc15' }
                                }}
                            >
                                <span className={isSaved ? "material-symbols-outlined filled" : "material-symbols-outlined"} style={{ fontVariationSettings: isSaved ? "'FILL' 1" : "none" }}>
                                    star
                                </span>
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete job">
                            <IconButton
                                size="small"
                                onClick={handleDelete}
                                sx={{
                                    color: 'text.disabled',
                                    '&:hover': { color: '#ef4444' }
                                }}
                            >
                                <span className="material-symbols-outlined">delete</span>
                            </IconButton>
                        </Tooltip>
                        <Chip
                            label={`${job.matchScore}% Match`}
                            size="small"
                            sx={{
                                bgcolor: matchColor.bg,
                                color: matchColor.text,
                                border: `1px solid ${matchColor.border}`,
                                fontWeight: 700,
                                fontSize: '0.625rem',
                                textTransform: 'uppercase',
                            }}
                        />
                    </Box>
                </Box>

                {/* Title & Company */}
                <Typography
                    variant="h4"
                    sx={{
                        color: 'text.primary',
                        mb: 0.5,
                        transition: 'color 0.2s ease',
                        '&:hover': {
                            color: 'primary.main',
                        },
                    }}
                >
                    <SafeText>{job.title}</SafeText>
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    <SafeText>{job.company}</SafeText>
                </Typography>

                {/* Location & Applicants */}
                <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>location_on</span>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem', textTransform: 'none', letterSpacing: 0 }}>
                            <SafeText>{job.location}</SafeText>
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>group</span>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem', textTransform: 'none', letterSpacing: 0 }}>
                            {job.applicants_count || job.applicants} Applicants
                        </Typography>
                    </Box>
                </Box>

                {/* Description Preview */}
                {job.description && (
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                            mt: 2,
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            fontSize: '0.8rem',
                            lineHeight: 1.5,
                        }}
                    >
                        <SafeText>
                            {job.description.length > 150
                                ? job.description.substring(0, 150) + '...'
                                : job.description}
                        </SafeText>
                    </Typography>
                )}

                {/* Footer: Posted Time + Action */}
                <Box
                    sx={{
                        mt: 3,
                        pt: 2,
                        borderTop: 1,
                        borderColor: 'grey.100',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                    }}
                >
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Posted {job.postedAgo} ago
                    </Typography>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            color: 'primary.main',
                            fontWeight: 700,
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            '&:hover': {
                                textDecoration: 'underline',
                            },
                        }}
                    >
                        Details
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_forward</span>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    )
}
