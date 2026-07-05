import React from 'react';

export const GovernanceLoadingState: React.FC = () => (
  <div className="flex h-full w-full items-center justify-center p-8">
    <div className="flex flex-col items-center gap-4 text-muted-foreground animate-pulse">
      <div className="h-8 w-8 rounded-full border-4 border-primary border-t-transparent animate-spin" />
      <p>Initializing Governance Operating System...</p>
    </div>
  </div>
);

export const GovernanceErrorState: React.FC<{ error: Error }> = ({ error }) => (
  <div className="flex h-full w-full items-center justify-center p-8 text-destructive">
    <div className="max-w-md text-center">
      <h2 className="mb-2 text-lg font-bold">Governance Access Denied</h2>
      <p className="text-sm">{error.message}</p>
    </div>
  </div>
);

export const GovernanceEmptyState: React.FC = () => (
  <div className="flex h-full w-full items-center justify-center p-8 text-muted-foreground">
    <p>No governance data available for this sector.</p>
  </div>
);
