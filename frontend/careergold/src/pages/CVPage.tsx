import {
    Box,
    Typography,
    Card,
    CardContent,
    Button,
    Chip,
    Grid,
    Divider,
} from '@mui/material'

export default function CVPage() {
    const skills = [
        { category: 'AI/ML', items: ['Python', 'Deep Learning', 'PyTorch', 'TensorFlow', 'OpenCV', 'MediaPipe', 'Reinforcement Learning'] },
        { category: 'Algorithms', items: ['Graph Theory', 'Dijkstra', 'A*', 'BFS/DFS', 'Network Flows'] },
        { category: 'Systems', items: ['ROS2', 'Gazebo', 'TCP/UDP', 'Distributed Systems', 'Git', 'Linux'] },
    ]

    const cvVersions = [
        { version: 'v3.1', name: 'General Research', status: 'Active', lastModified: '2h ago' },
        { version: 'v2.0', name: 'Product Focus', status: 'Draft', lastModified: '3d ago' },
        { version: 'v1.5', name: 'ML Engineer', status: 'Archived', lastModified: '1w ago' },
    ]

    return (
        <Box sx={{ p: 4 }}>
            {/* Page Heading */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h1" sx={{ fontSize: '2rem', mb: 1 }}>
                    CV Profile
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Manage your base CV and tailored versions
                </Typography>
            </Box>

            <Grid container spacing={3}>
                {/* Base CV Card */}
                <Grid item xs={12} lg={8}>
                    <Card sx={{ mb: 3 }}>
                        <CardContent sx={{ p: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                                <Box>
                                    <Typography variant="h3" sx={{ mb: 0.5 }}>Renan Lavirotte</Typography>
                                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                        renan.lavirotte@gmail.com • +44 7729446958
                                    </Typography>
                                </Box>
                                <Button
                                    variant="outlined"
                                    startIcon={<span className="material-symbols-outlined">edit</span>}
                                    size="small"
                                >
                                    Edit
                                </Button>
                            </Box>

                            <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
                                Experienced across machine learning, deep learning, computer vision, reinforcement learning, and theoretical Computer science. Built Python systems using OpenCV/MediaPipe and PyTorch/TensorFlow.
                            </Typography>

                            <Divider sx={{ my: 2 }} />

                            {/* Skills */}
                            <Typography variant="h4" sx={{ mb: 2 }}>Skills</Typography>
                            {skills.map((group) => (
                                <Box key={group.category} sx={{ mb: 2 }}>
                                    <Typography variant="caption" sx={{ color: 'text.secondary', mb: 1, display: 'block' }}>
                                        {group.category}
                                    </Typography>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                        {group.items.map((skill) => (
                                            <Chip key={skill} label={skill} size="small" sx={{ bgcolor: 'grey.100' }} />
                                        ))}
                                    </Box>
                                </Box>
                            ))}
                        </CardContent>
                    </Card>
                </Grid>

                {/* CV Versions Sidebar */}
                <Grid item xs={12} lg={4}>
                    <Card>
                        <CardContent sx={{ p: 3 }}>
                            <Typography variant="h4" sx={{ mb: 2 }}>CV Versions</Typography>
                            {cvVersions.map((cv) => (
                                <Box
                                    key={cv.version}
                                    sx={{
                                        p: 2,
                                        mb: 1,
                                        borderRadius: 2,
                                        border: 1,
                                        borderColor: cv.status === 'Active' ? 'primary.main' : 'divider',
                                        bgcolor: cv.status === 'Active' ? 'rgba(183, 134, 11, 0.05)' : 'transparent',
                                        cursor: 'pointer',
                                        '&:hover': { bgcolor: 'grey.50' },
                                    }}
                                >
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Box>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                {cv.name}
                                            </Typography>
                                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                                {cv.version} • {cv.lastModified}
                                            </Typography>
                                        </Box>
                                        <Chip
                                            label={cv.status}
                                            size="small"
                                            color={cv.status === 'Active' ? 'primary' : 'default'}
                                            variant={cv.status === 'Active' ? 'filled' : 'outlined'}
                                        />
                                    </Box>
                                </Box>
                            ))}
                            <Button
                                fullWidth
                                variant="outlined"
                                startIcon={<span className="material-symbols-outlined">add</span>}
                                sx={{ mt: 2 }}
                            >
                                Create New Version
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    )
}
