import { createTheme } from '@mui/material/styles';

// CareerGold M3 Theme based on Stitch wireframes
// Primary: Metallic Gold #B7860B
// Surface: White/Light backgrounds
// Font: Plus Jakarta Sans

const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#B7860B',
            light: '#D4A842',
            dark: '#8A6508',
            contrastText: '#FFFFFF',
        },
        secondary: {
            main: '#6750A4', // M3 Purple for wireframe accents
            light: '#9A82DB',
            dark: '#4F378B',
            contrastText: '#FFFFFF',
        },
        background: {
            default: '#F8F7F5',
            paper: '#FFFFFF',
        },
        text: {
            primary: '#1C170D',
            secondary: '#9B844B',
        },
        divider: '#E8E1CF',
        error: {
            main: '#BA1A1A',
        },
        success: {
            main: '#16A34A',
        },
    },
    typography: {
        fontFamily: '"Plus Jakarta Sans", sans-serif',
        h1: {
            fontWeight: 800,
            fontSize: '2.5rem',
            letterSpacing: '-0.033em',
        },
        h2: {
            fontWeight: 700,
            fontSize: '1.5rem',
            letterSpacing: '-0.02em',
        },
        h3: {
            fontWeight: 700,
            fontSize: '1.25rem',
        },
        h4: {
            fontWeight: 700,
            fontSize: '1.125rem',
        },
        body1: {
            fontSize: '1rem',
            lineHeight: 1.6,
        },
        body2: {
            fontSize: '0.875rem',
            lineHeight: 1.5,
        },
        button: {
            fontWeight: 700,
            textTransform: 'none',
        },
        caption: {
            fontSize: '0.625rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
        },
    },
    shape: {
        borderRadius: 8,
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    padding: '12px 24px',
                    boxShadow: 'none',
                    '&:hover': {
                        boxShadow: 'none',
                    },
                },
                containedPrimary: {
                    '&:hover': {
                        backgroundColor: '#A07809',
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    border: '1px solid #E8E1CF',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    '& .MuiOutlinedInput-root': {
                        borderRadius: 8,
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#B7860B',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#B7860B',
                        },
                    },
                },
            },
        },
        MuiFab: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    boxShadow: '0 4px 16px rgba(183, 134, 11, 0.2)',
                },
            },
        },
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    borderRight: '1px solid #E8E1CF',
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    fontWeight: 700,
                    fontSize: '0.625rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                },
            },
        },
    },
});

export default theme;
