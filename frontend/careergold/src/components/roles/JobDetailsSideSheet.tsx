import { useState } from 'react'
import {
    Box,
    Typography,
    IconButton,
    Chip,
    Button,
    Drawer,
    Stack,
} from '@mui/material'
import { Job } from '../../mocks/data'

interface JobDetailsSideSheetProps {
    job: Job | null
    open: boolean
    onClose: () => void
}

export default function JobDetailsSideSheet({ job, open, onClose }: JobDetailsSideSheetProps) {
    if (!job) return null

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            PaperProps={{
                sx: {
                    width: '100%',
                    maxWidth: 480,
                    borderRadius: '12px 0 0 12px',
                },
            }}
            // Overlay backdrop
            ModalProps={{
                BackdropProps: {
                    sx: {
                        bgcolor: 'rgba(0, 0, 0, 0.2)',
                        backdropFilter: 'blur(2px)',
                    },
                },
            }}
        >
            {/* Header Section */}
            <Box
                sx={{
                    position: 'sticky',
                    top: 0,
                    zIndex: 30,
                    px: 3,
                    py: 3,
                    borderBottom: 1,
                    borderColor: 'divider',
                    bgcolor: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(12px)',
                }}
            >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                        <Chip
                            label="Highly Matched"
                            size="small"
                            sx={{
                                bgcolor: 'rgba(183, 134, 11, 0.1)',
                                color: 'primary.main',
                                fontWeight: 700,
                                fontSize: '0.625rem',
                                textTransform: 'uppercase',
                                mb: 1,
                            }}
                        />
                        <Typography variant="h3" sx={{ color: 'text.primary', fontWeight: 700, fontSize: '1.5rem' }}>
                            {job.title}
                        </Typography>
                        <Typography variant="body1" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                            {job.company}
                        </Typography>
                    </Box>
                    <IconButton onClick={onClose} sx={{ color: 'text.secondary' }}>
                        <span className="material-symbols-outlined">close</span>
                    </IconButton>
                </Box>

                {/* Meta Info */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, color: 'text.secondary', fontSize: '0.875rem' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>location_on</span>
                        <span>{job.location}</span>
                    </Box>
                    {job.salary && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>payments</span>
                            <span>{job.salary}</span>
                        </Box>
                    )}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>schedule</span>
                        <span>Posted {job.postedAgo} ago</span>
                    </Box>
                </Box>
            </Box>

            {/* Scrollable Content */}
            <Box sx={{ flex: 1, overflowY: 'auto', px: 3, py: 3 }}>
                {/* Breadcrumbs */}
                <Box sx={{ display: 'flex', gap: 1, mb: 3, color: 'text.secondary', fontSize: '0.75rem' }}>
                    <span style={{ textTransform: 'uppercase', letterSpacing: '0.1em' }}>Engineering</span>
                    <span>/</span>
                    <span style={{ color: '#1C170D', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Frontend</span>
                </Box>

                {/* Job Description */}
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h4" sx={{ mb: 1.5 }}>Job Description</Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                        {job.description || 'We are seeking an experienced developer to join our core product team. You will be responsible for building high-quality, scalable applications.'}
                    </Typography>
                </Box>

                {/* Responsibilities */}
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h4" sx={{ mb: 1.5 }}>Key Responsibilities</Typography>
                    <Box component="ul" sx={{ pl: 2.5, color: 'text.secondary' }}>
                        {(job.responsibilities || [
                            'Develop and maintain responsive web applications using React and TypeScript.',
                            'Collaborate with UI/UX designers to implement design systems.',
                            'Optimize application performance and ensure cross-browser compatibility.',
                            'Participate in code reviews and mentor junior developers.',
                        ]).map((resp, idx) => (
                            <Typography component="li" key={idx} variant="body2" sx={{ mb: 1 }}>
                                {resp}
                            </Typography>
                        ))}
                    </Box>
                </Box>

                {/* Skills Match */}
                <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                        <Typography variant="h4">Skills Match</Typography>
                        <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 600 }}>
                            {job.matchScore}% Match
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {(job.skills || []).map((skill, idx) => (
                            <Chip
                                key={idx}
                                label={skill.name}
                                size="small"
                                icon={
                                    <span
                                        className="material-symbols-outlined"
                                        style={{
                                            fontSize: 14,
                                            color: skill.matched ? '#16A34A' : '#9ca3af',
                                            fontWeight: 700,
                                        }}
                                    >
                                        {skill.matched ? 'check' : 'add'}
                                    </span>
                                }
                                sx={{
                                    bgcolor: 'grey.100',
                                    color: 'text.primary',
                                    fontWeight: 500,
                                    '& .MuiChip-icon': {
                                        ml: 0.5,
                                    },
                                }}
                            />
                        ))}
                    </Box>
                </Box>

                {/* Company Info */}
                {job.companyInfo && (
                    <Box
                        sx={{
                            p: 2,
                            borderRadius: 2,
                            bgcolor: 'grey.50',
                            border: 1,
                            borderColor: 'divider',
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Box
                                sx={{
                                    width: 48,
                                    height: 48,
                                    borderRadius: 2,
                                    bgcolor: 'background.paper',
                                    border: 1,
                                    borderColor: 'divider',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'primary.main',
                                }}
                            >
                                <span className="material-symbols-outlined">corporate_fare</span>
                            </Box>
                            <Box>
                                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                                    About {job.company}
                                </Typography>
                                <Typography variant="caption" sx={{ color: 'text.secondary', textTransform: 'none', letterSpacing: 0 }}>
                                    {job.companyInfo.size} • {job.companyInfo.industry}
                                </Typography>
                            </Box>
                        </Box>
                    </Box>
                )}
            </Box>

            {/* Sticky Action Footer */}
            <Box
                sx={{
                    position: 'sticky',
                    bottom: 0,
                    zIndex: 30,
                    px: 3,
                    py: 2.5,
                    borderTop: 1,
                    borderColor: 'divider',
                    bgcolor: 'background.paper',
                    display: 'flex',
                    gap: 2,
                }}
            >
                <Button
                    variant="outlined"
                    startIcon={<span className="material-symbols-outlined">bookmark</span>}
                    sx={{
                        flex: 1,
                        height: 48,
                        borderWidth: 2,
                        '&:hover': {
                            borderWidth: 2,
                        },
                    }}
                >
                    Save
                </Button>
                <Button
                    variant="contained"
                    sx={{
                        flex: 2,
                        height: 48,
                        boxShadow: '0 4px 16px rgba(183, 134, 11, 0.2)',
                    }}
                >
                    Apply Now
                </Button>
            </Box>
        </Drawer>
    )
}
