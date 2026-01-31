import { useState } from 'react'
import { Box, Typography, Chip, IconButton } from '@mui/material'
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid'
import JobDetailsSideSheet from '../components/roles/JobDetailsSideSheet'
import { mockJobs, Job } from '../mocks/data'

export default function RolesPage() {
    const [selectedJob, setSelectedJob] = useState<Job | null>(null)
    const [sideSheetOpen, setSideSheetOpen] = useState(false)

    const handleJobClick = (job: Job) => {
        setSelectedJob(job)
        setSideSheetOpen(true)
    }

    const getMatchColor = (score: number): 'secondary' | 'primary' | 'default' => {
        if (score >= 90) return 'secondary'
        if (score >= 70) return 'primary'
        return 'default'
    }

    const columns: GridColDef[] = [
        {
            field: 'title',
            headerName: 'JOB TITLE',
            flex: 1.5,
            minWidth: 200,
            renderCell: (params: GridRenderCellParams) => (
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {params.value}
                </Typography>
            ),
        },
        {
            field: 'company',
            headerName: 'COMPANY',
            flex: 1,
            minWidth: 150,
            renderCell: (params: GridRenderCellParams) => (
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {params.value}
                </Typography>
            ),
        },
        {
            field: 'location',
            headerName: 'LOCATION',
            flex: 1,
            minWidth: 150,
            renderCell: (params: GridRenderCellParams) => (
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {params.value}
                </Typography>
            ),
        },
        {
            field: 'matchScore',
            headerName: 'MATCH',
            width: 100,
            align: 'center',
            headerAlign: 'center',
            renderCell: (params: GridRenderCellParams) => (
                <Chip
                    label={`${params.value}%`}
                    size="small"
                    color={getMatchColor(params.value as number)}
                    sx={{ fontWeight: 700, minWidth: 50 }}
                />
            ),
        },
        {
            field: 'status',
            headerName: 'STATUS',
            width: 120,
            align: 'center',
            headerAlign: 'center',
            renderCell: (params: GridRenderCellParams) => (
                <Chip
                    label={params.value}
                    size="small"
                    variant={params.value === 'NEW' ? 'outlined' : 'filled'}
                    color={params.value === 'SAVED' ? 'warning' : params.value === 'APPLIED' ? 'success' : 'default'}
                />
            ),
        },
        {
            field: 'actions',
            headerName: 'ACTIONS',
            width: 100,
            sortable: false,
            filterable: false,
            renderCell: () => (
                <>
                    <IconButton size="small" sx={{ color: 'text.secondary' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>bookmark</span>
                    </IconButton>
                    <IconButton size="small" sx={{ color: 'primary.main' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>open_in_new</span>
                    </IconButton>
                </>
            ),
        },
    ]

    return (
        <Box sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Page Heading */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h1" sx={{ fontSize: '2rem', mb: 1 }}>
                    All Roles
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                    Browse and filter all discovered job opportunities
                </Typography>
            </Box>

            {/* Roles DataGrid */}
            <Box sx={{ flex: 1, minHeight: 400 }}>
                <DataGrid
                    rows={mockJobs}
                    columns={columns}
                    pageSizeOptions={[10, 25, 50]}
                    initialState={{
                        pagination: { paginationModel: { pageSize: 10 } },
                    }}
                    disableRowSelectionOnClick
                    onRowClick={(params) => handleJobClick(params.row as Job)}
                    sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 2,
                        bgcolor: 'background.paper',
                        '& .MuiDataGrid-columnHeaders': {
                            bgcolor: 'grey.50',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            fontSize: '0.75rem',
                            letterSpacing: '0.05em',
                        },
                        '& .MuiDataGrid-row:hover': {
                            cursor: 'pointer',
                            bgcolor: 'rgba(183, 134, 11, 0.04)',
                        },
                        '& .MuiDataGrid-cell:focus': {
                            outline: 'none',
                        },
                        '& .MuiDataGrid-columnHeader:focus': {
                            outline: 'none',
                        },
                    }}
                />
            </Box>

            {/* Job Details Side Sheet */}
            <JobDetailsSideSheet
                job={selectedJob}
                open={sideSheetOpen}
                onClose={() => setSideSheetOpen(false)}
            />
        </Box>
    )
}
