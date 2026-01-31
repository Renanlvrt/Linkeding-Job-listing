import { Chip, ChipProps } from '@mui/material'

type StatusType =
    | 'NEW'
    | 'SAVED'
    | 'APPLIED'
    | 'REJECTED'
    | 'Queued'
    | 'Submitting'
    | 'Submitted'
    | 'Manual follow-up'
    | 'Not connected'
    | 'Connected'
    | 'Rate-limited'
    | 'Error'
    | 'Idle'
    | 'Running'
    | 'Paused'
    | 'Completed'
    | 'Drafting'
    | 'Ready'
    | 'Needs review'

interface StatusChipProps {
    status: StatusType
    size?: ChipProps['size']
}

// Color mapping for different status types
const statusConfig: Record<StatusType, { color: ChipProps['color']; variant: 'filled' | 'outlined' }> = {
    // Job statuses
    NEW: { color: 'primary', variant: 'outlined' },
    SAVED: { color: 'warning', variant: 'filled' },
    APPLIED: { color: 'success', variant: 'filled' },
    REJECTED: { color: 'error', variant: 'filled' },

    // Application statuses
    Queued: { color: 'default', variant: 'outlined' },
    Submitting: { color: 'warning', variant: 'filled' },
    Submitted: { color: 'success', variant: 'filled' },
    'Manual follow-up': { color: 'warning', variant: 'outlined' },

    // Source connection statuses
    'Not connected': { color: 'default', variant: 'outlined' },
    Connected: { color: 'success', variant: 'filled' },
    'Rate-limited': { color: 'warning', variant: 'filled' },
    Error: { color: 'error', variant: 'filled' },

    // Search run statuses
    Idle: { color: 'default', variant: 'outlined' },
    Running: { color: 'primary', variant: 'filled' },
    Paused: { color: 'warning', variant: 'outlined' },
    Completed: { color: 'success', variant: 'filled' },

    // CV generation statuses
    Drafting: { color: 'warning', variant: 'outlined' },
    Ready: { color: 'success', variant: 'filled' },
    'Needs review': { color: 'warning', variant: 'filled' },
}

export default function StatusChip({ status, size = 'small' }: StatusChipProps) {
    const config = statusConfig[status] || { color: 'default', variant: 'outlined' }

    return (
        <Chip
            label={status}
            size={size}
            color={config.color}
            variant={config.variant}
            sx={{
                fontWeight: 700,
                fontSize: '0.625rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
            }}
        />
    )
}
