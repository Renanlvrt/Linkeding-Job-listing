import { useState, useEffect } from 'react'
import {
    Box,
    Typography,
    Card,
    CardContent,
    Button,
    TextField,
    LinearProgress,
    Chip,
    Grid,
    Divider,
    Alert,
} from '@mui/material'
import StatusChip from '../components/common/StatusChip'
import { mockSources } from '../mocks/data'

// API Base URL - change this when deploying
const API_BASE = 'http://localhost:8000'

interface ScrapedJob {
    title: string
    company: string
    link: string
    snippet?: string
    source?: string
    external_id?: string | null
}

interface ScrapeResult {
    status: string
    keywords: string
    location: string
    jobs_found: number
    jobs: ScrapedJob[]
}

interface QuotaInfo {
    requests_remaining: number
    monthly_limit: number
    api_configured: boolean
}

export default function LeadScraperPage() {
    const [isRunning, setIsRunning] = useState(false)
    const [progress, setProgress] = useState(0)
    const [keywords, setKeywords] = useState('Software Engineer')
    const [location, setLocation] = useState('Remote')
    const [maxResults, setMaxResults] = useState(10)
    const [dateFilter, setDateFilter] = useState('week')
    const [results, setResults] = useState<ScrapedJob[]>([])
    const [scrapeHistory, setScrapeHistory] = useState<{ date: string; count: number; keywords: string; status: string }[]>([])
    const [error, setError] = useState<string | null>(null)
    const [quota, setQuota] = useState<QuotaInfo | null>(null)

    // Fetch quota on mount
    useEffect(() => {
        const fetchQuota = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/scraper/quota`)
                if (res.ok) {
                    const data = await res.json()
                    setQuota(data)
                }
            } catch {
                // Quota endpoint not critical
            }
        }
        fetchQuota()
    }, [])

    const handleStartScrape = async () => {
        setIsRunning(true)
        setProgress(10)
        setError(null)

        try {
            // Call the real backend API
            const response = await fetch(`${API_BASE}/api/scraper/quick`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords,
                    location,
                    max_results: maxResults,
                    date_filter: dateFilter,
                }),
            })

            setProgress(50)

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`)
            }

            const data: ScrapeResult = await response.json()
            setProgress(100)

            // Update results
            setResults(data.jobs)

            // Add to history
            setScrapeHistory(prev => [
                {
                    date: 'Just now',
                    count: data.jobs_found,
                    keywords: data.keywords,
                    status: 'Completed',
                },
                ...prev.slice(0, 4), // Keep last 5
            ])

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to scrape')
            setProgress(0)
        } finally {
            setIsRunning(false)
        }
    }

    return (
        <Box sx={{ p: 4 }}>
            {/* Page Heading */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
                <Box>
                    <Typography variant="h1" sx={{ fontSize: '2rem', mb: 1 }}>
                        Lead Scraper
                    </Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                        Discover and import job leads from connected sources
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    startIcon={<span className="material-symbols-outlined">play_arrow</span>}
                    onClick={handleStartScrape}
                    disabled={isRunning}
                    sx={{
                        bgcolor: '#6750A4',
                        '&:hover': { bgcolor: '#5840A0' },
                    }}
                >
                    {isRunning ? 'Scraping...' : 'Start Scrape'}
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Scrape Configuration */}
                <Grid item xs={12} lg={8}>
                    <Card sx={{ mb: 3 }}>
                        <CardContent sx={{ p: 3 }}>
                            <Typography variant="h4" sx={{ mb: 3 }}>Scrape Configuration</Typography>

                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                                <TextField
                                    label="Search Keywords"
                                    placeholder="e.g. Machine Learning Engineer, Robotics"
                                    fullWidth
                                    value={keywords}
                                    onChange={(e) => setKeywords(e.target.value)}
                                />
                                <TextField
                                    label="Location"
                                    placeholder="e.g. Remote, London, UK"
                                    fullWidth
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                />
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <TextField
                                        label="Max Results"
                                        type="number"
                                        value={maxResults}
                                        onChange={(e) => setMaxResults(Number(e.target.value))}
                                        sx={{ width: 150 }}
                                    />
                                    <TextField
                                        label="Posted Within"
                                        select
                                        value={dateFilter}
                                        onChange={(e) => setDateFilter(e.target.value)}
                                        sx={{ width: 180 }}
                                        SelectProps={{ native: true }}
                                    >
                                        <option value="day">Last 24 hours</option>
                                        <option value="week">Last week</option>
                                        <option value="month">Last month</option>
                                    </TextField>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>

                    {/* Scrape Progress */}
                    {isRunning && (
                        <Card sx={{ mb: 3 }}>
                            <CardContent sx={{ p: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h4">Scrape in Progress</Typography>
                                    <Chip label="Running" color="primary" size="small" />
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={progress}
                                    sx={{
                                        height: 8,
                                        borderRadius: 4,
                                        mb: 2,
                                        bgcolor: 'grey.200',
                                        '& .MuiLinearProgress-bar': {
                                            bgcolor: '#6750A4',
                                        },
                                    }}
                                />
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', color: 'text.secondary' }}>
                                    <Typography variant="body2">Searching for "{keywords}"...</Typography>
                                    <Typography variant="body2">{progress}% complete</Typography>
                                </Box>
                            </CardContent>
                        </Card>
                    )}

                    {/* Scraped Jobs Results */}
                    {results.length > 0 && (
                        <Card sx={{ mb: 3 }}>
                            <CardContent sx={{ p: 3 }}>
                                <Typography variant="h4" sx={{ mb: 3 }}>
                                    Found {results.length} Jobs
                                </Typography>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                    {results.map((job, idx) => (
                                        <Box
                                            key={idx}
                                            sx={{
                                                p: 2,
                                                borderRadius: 2,
                                                border: 1,
                                                borderColor: 'divider',
                                                '&:hover': { bgcolor: 'grey.50' },
                                            }}
                                        >
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <Box>
                                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                        {job.title}
                                                    </Typography>
                                                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                                        {job.company}
                                                    </Typography>
                                                </Box>
                                                <Button
                                                    size="small"
                                                    href={job.link}
                                                    target="_blank"
                                                    startIcon={<span className="material-symbols-outlined" style={{ fontSize: 16 }}>open_in_new</span>}
                                                >
                                                    View
                                                </Button>
                                            </Box>
                                            {job.snippet && (
                                                <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>
                                                    {job.snippet.slice(0, 150)}...
                                                </Typography>
                                            )}
                                        </Box>
                                    ))}
                                </Box>
                            </CardContent>
                        </Card>
                    )}

                    {/* Recent Scrape Results */}
                    <Card>
                        <CardContent sx={{ p: 3 }}>
                            <Typography variant="h4" sx={{ mb: 3 }}>Recent Scrape History</Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {scrapeHistory.length === 0 ? (
                                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                        No scrapes yet. Click "Start Scrape" to find jobs!
                                    </Typography>
                                ) : (
                                    scrapeHistory.map((run, idx) => (
                                        <Box
                                            key={idx}
                                            sx={{
                                                p: 2,
                                                borderRadius: 2,
                                                border: 1,
                                                borderColor: 'divider',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center',
                                            }}
                                        >
                                            <Box>
                                                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                    {run.keywords}
                                                </Typography>
                                                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                                    {run.date} • {run.count} leads found
                                                </Typography>
                                            </Box>
                                            <StatusChip status="Completed" />
                                        </Box>
                                    ))
                                )}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Source Status Sidebar */}
                <Grid item xs={12} lg={4}>
                    <Card>
                        <CardContent sx={{ p: 3 }}>
                            <Typography variant="h4" sx={{ mb: 3 }}>Source Status</Typography>
                            {mockSources.map((source, idx) => (
                                <Box key={source.name}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                            <Box
                                                sx={{
                                                    width: 36,
                                                    height: 36,
                                                    borderRadius: 2,
                                                    bgcolor: 'grey.100',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                }}
                                            >
                                                <span className="material-symbols-outlined" style={{ fontSize: 18, color: '#64748B' }}>
                                                    link
                                                </span>
                                            </Box>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                                {source.name}
                                            </Typography>
                                        </Box>
                                        <StatusChip status={source.status} />
                                    </Box>
                                    {idx < mockSources.length - 1 && <Divider />}
                                </Box>
                            ))}
                        </CardContent>
                    </Card>

                    {/* RapidAPI Quota Card */}
                    {quota && (
                        <Card sx={{ mt: 3 }}>
                            <CardContent sx={{ p: 3 }}>
                                <Typography variant="h4" sx={{ mb: 2 }}>RapidAPI Quota</Typography>
                                <Box sx={{ mb: 2 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>Monthly Usage</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                            {quota.monthly_limit - quota.requests_remaining} / {quota.monthly_limit}
                                        </Typography>
                                    </Box>
                                    <LinearProgress
                                        variant="determinate"
                                        value={((quota.monthly_limit - quota.requests_remaining) / quota.monthly_limit) * 100}
                                        sx={{
                                            height: 6,
                                            borderRadius: 3,
                                            bgcolor: 'grey.200',
                                            '& .MuiLinearProgress-bar': {
                                                bgcolor: quota.requests_remaining < 20 ? 'error.main' : 'primary.main',
                                            },
                                        }}
                                    />
                                </Box>
                                <Typography variant="caption" sx={{ color: quota.requests_remaining < 20 ? 'error.main' : 'text.secondary' }}>
                                    {quota.requests_remaining} requests remaining this month
                                </Typography>
                                {!quota.api_configured && (
                                    <Alert severity="warning" sx={{ mt: 2 }}>
                                        RapidAPI key not configured
                                    </Alert>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {/* Info Card */}
                    <Card sx={{ mt: 3 }}>
                        <CardContent sx={{ p: 3 }}>
                            <Typography variant="h4" sx={{ mb: 2 }}>How It Works</Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                                <strong>Quick Search</strong> uses DuckDuckGo (free, unlimited).
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                                <strong>RapidAPI</strong> gets detailed LinkedIn data (100/month free).
                            </Typography>
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                Tip: Use specific keywords like "ML Engineer Remote" for better results.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    )
}
