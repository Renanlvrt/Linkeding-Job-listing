import {
    Box,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    IconButton,
} from '@mui/material'
import StatusChip from '../components/common/StatusChip'
import { mockApplications } from '../mocks/data'

export default function ApplicationsPage() {
    return (
        <Box sx={{ p: 4 }}>
            {/* Page Heading */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h1" sx={{ fontSize: '2rem', mb: 1 }}>
                    Applications
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Track your application queue and submission statuses
                </Typography>
            </Box>

            {/* Applications Table */}
            <TableContainer component={Paper} sx={{ border: 1, borderColor: 'divider', boxShadow: 'none' }}>
                <Table>
                    <TableHead>
                        <TableRow sx={{ bgcolor: 'grey.50' }}>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                Job Title
                            </TableCell>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                Company
                            </TableCell>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                CV Version
                            </TableCell>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                Status
                            </TableCell>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                Submitted
                            </TableCell>
                            <TableCell sx={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                Actions
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {mockApplications.map((app) => (
                            <TableRow key={app.id} hover>
                                <TableCell>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {app.jobTitle}
                                    </Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                        {app.company}
                                    </Typography>
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={app.cvVersion}
                                        size="small"
                                        variant="outlined"
                                        sx={{ fontWeight: 600 }}
                                    />
                                </TableCell>
                                <TableCell>
                                    <StatusChip status={app.status} />
                                </TableCell>
                                <TableCell>
                                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                        {app.submittedAt || '—'}
                                    </Typography>
                                </TableCell>
                                <TableCell>
                                    <IconButton size="small" sx={{ color: 'text.secondary' }}>
                                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>visibility</span>
                                    </IconButton>
                                    <IconButton size="small" sx={{ color: 'primary.main' }}>
                                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>refresh</span>
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    )
}
