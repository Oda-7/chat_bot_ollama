import { Box } from '@mui/material';

const ModernSpinner: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: 48,
    }}
  >
    <svg width="48" height="48" viewBox="0 0 48 48">
      <circle
        cx="24"
        cy="24"
        r="20"
        fill="none"
        stroke="#1976d2"
        strokeWidth="4"
        strokeDasharray="100"
        strokeDashoffset="60"
        strokeLinecap="round"
        style={{
          animation: 'spinner 1.2s linear infinite',
        }}
      />
      <style>
        {`
          @keyframes spinner {
            0% { stroke-dashoffset: 100; }
            100% { stroke-dashoffset: 0; }
          }
        `}
      </style>
    </svg>
  </Box>
);

export default ModernSpinner;
