// Canonical dashboard client lives at features/dashboard/api/dashboardClient.ts
// and assembles the dashboard from the real /scorecard + /timeseries endpoints.
// Re-exported here for backward compatibility with any older import path.
export { dashboardClient } from '@/features/dashboard/api/dashboardClient';
