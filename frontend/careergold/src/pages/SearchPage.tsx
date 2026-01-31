import {
    Box,
    Typography,
    TextField,
    Button,
    InputAdornment,
} from '@mui/material'

export default function SearchPage() {
    return (
        <Box
            sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                py: 6,
                px: 3,
            }}
        >
            {/* Page Heading */}
            <Box sx={{ textAlign: 'center', mb: 5, maxWidth: 600 }}>
                <Typography
                    variant="h1"
                    sx={{
                        fontSize: { xs: '2rem', md: '2.5rem' },
                        mb: 1,
                    }}
                >
                    Define Your Search
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Set your preferences to find the best job matches.
                </Typography>
            </Box>

            {/* Search Form Card */}
            <Box
                sx={{
                    width: '100%',
                    maxWidth: 600,
                    bgcolor: 'background.paper',
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 3,
                    p: 4,
                    boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                }}
            >
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    {/* Job Title Field */}
                    <Box>
                        <Typography
                            variant="caption"
                            sx={{
                                display: 'block',
                                mb: 1,
                                fontWeight: 600,
                                color: 'text.primary',
                            }}
                        >
                            JOB TITLE
                        </Typography>
                        <TextField
                            fullWidth
                            placeholder="e.g. Senior Software Engineer"
                            variant="outlined"
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    height: 56,
                                },
                            }}
                        />
                    </Box>

                    {/* Location Field */}
                    <Box>
                        <Typography
                            variant="caption"
                            sx={{
                                display: 'block',
                                mb: 1,
                                fontWeight: 600,
                                color: 'text.primary',
                            }}
                        >
                            DESIRED LOCATION
                        </Typography>
                        <TextField
                            fullWidth
                            placeholder="e.g. Remote or New York, NY"
                            variant="outlined"
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <span className="material-symbols-outlined" style={{ color: '#9B844B' }}>
                                            map
                                        </span>
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    height: 56,
                                },
                            }}
                        />
                    </Box>

                    {/* Skills Field */}
                    <Box>
                        <Typography
                            variant="caption"
                            sx={{
                                display: 'block',
                                mb: 1,
                                fontWeight: 600,
                                color: 'text.primary',
                            }}
                        >
                            SKILL KEYWORDS
                        </Typography>
                        <TextField
                            fullWidth
                            multiline
                            rows={4}
                            placeholder="e.g. React, Python, Project Management"
                            variant="outlined"
                        />
                        <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary', fontSize: '0.75rem' }}>
                            Separate skills with commas to improve accuracy.
                        </Typography>
                    </Box>

                    {/* Submit Button */}
                    <Box sx={{ pt: 2 }}>
                        <Button
                            variant="contained"
                            fullWidth
                            sx={{
                                height: 56,
                                fontWeight: 700,
                                fontSize: '1rem',
                            }}
                        >
                            Save & Find Jobs
                        </Button>
                    </Box>
                </Box>
            </Box>

            {/* Security Note */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mt: 4,
                    color: 'text.secondary',
                    fontSize: '0.875rem',
                }}
            >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>lock</span>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Your data is secured and encrypted.
                </Typography>
            </Box>
        </Box>
    )
}
