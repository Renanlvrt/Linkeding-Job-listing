import {
    Box,
    Typography,
    Card,
    CardContent,
    Switch,
    FormControlLabel,
    Divider,
    Button,
} from '@mui/material'
import StatusChip from '../components/common/StatusChip'
import { mockSources } from '../mocks/data'

export default function SettingsPage() {
    return (
        <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
            {/* Page Heading */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h1" sx={{ fontSize: '2rem', mb: 1 }}>
                    Settings
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Configure sources, preferences, and safe mode options
                </Typography>
            </Box>

            {/* Source Connections */}
            <Card sx={{ mb: 3 }}>
                <CardContent sx={{ p: 3 }}>
                    <Typography variant="h4" sx={{ mb: 3 }}>Source Connections</Typography>
                    {mockSources.map((source, idx) => (
                        <Box key={source.name}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <Box
                                        sx={{
                                            width: 40,
                                            height: 40,
                                            borderRadius: 2,
                                            bgcolor: 'grey.100',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        <span className="material-symbols-outlined" style={{ color: '#64748B' }}>link</span>
                                    </Box>
                                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                        {source.name}
                                    </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <StatusChip status={source.status} />
                                    <Button
                                        size="small"
                                        variant={source.status === 'Connected' ? 'outlined' : 'contained'}
                                    >
                                        {source.status === 'Connected' ? 'Disconnect' : 'Connect'}
                                    </Button>
                                </Box>
                            </Box>
                            {idx < mockSources.length - 1 && <Divider />}
                        </Box>
                    ))}
                </CardContent>
            </Card>

            {/* Preferences */}
            <Card sx={{ mb: 3 }}>
                <CardContent sx={{ p: 3 }}>
                    <Typography variant="h4" sx={{ mb: 3 }}>Preferences</Typography>

                    <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Auto-generate CV for high match roles (≥80%)"
                        sx={{ mb: 2, display: 'flex' }}
                    />

                    <FormControlLabel
                        control={<Switch />}
                        label="Show salary estimates when available"
                        sx={{ mb: 2, display: 'flex' }}
                    />

                    <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Email notifications for new matches"
                        sx={{ display: 'flex' }}
                    />
                </CardContent>
            </Card>

            {/* Safe Mode */}
            <Card>
                <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                            <Typography variant="h4" sx={{ mb: 1 }}>Safe Mode</Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                When enabled, all applications require manual confirmation before submission.
                                Auto-apply is disabled by default for your protection.
                            </Typography>
                        </Box>
                        <Switch defaultChecked color="warning" />
                    </Box>
                </CardContent>
            </Card>
        </Box>
    )
}
