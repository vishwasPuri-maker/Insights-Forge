import React, { useCallback } from 'react';
import { usePermissions } from '../hooks/usePermissions';
import type { GovernancePermission } from '@/types/governance';

interface PermissionMatrixProps {
  tenantId: string;
  role: string;
}

const PermissionRow = React.memo(({ 
  resource, 
  permissions,
  onToggle 
}: { 
  resource: string; 
  permissions: GovernancePermission[];
  onToggle: (id: string) => void;
}) => {
  const getPerm = (action: string) => permissions.find(p => p.action === action);

  return (
    <tr role="row" className="border-b border-border/50 hover:bg-muted/30">
      <td role="cell" className="p-3 font-medium">{resource}</td>
      {['read', 'write', 'delete', 'execute'].map(action => {
        const perm = getPerm(action);
        const permId = perm ? perm.id : `${resource}-${action}`;
        const hasPerm = Boolean(perm);
        return (
          <td role="cell" key={action} className="p-3 text-center">
            <input 
              type="checkbox" 
              checked={hasPerm}
              onChange={() => onToggle(permId)}
              aria-label={`${action} permission for ${resource}`}
              className="w-4 h-4 rounded border-input bg-background cursor-pointer"
            />
          </td>
        );
      })}
    </tr>
  );
});

PermissionRow.displayName = 'PermissionRow';

export const PermissionMatrix: React.FC<PermissionMatrixProps> = ({ tenantId, role }) => {
  const { data: permissions, isLoading, isError } = usePermissions(tenantId, role);

  const handleToggle = useCallback((permId: string) => {
    // Pure UI. No mutation APIs are permitted in components under Option C.
    console.log('Toggled permission:', permId);
  }, []);

  if (isLoading) return <div className="p-4 animate-pulse">Loading matrix...</div>;
  if (isError) return <div className="p-4 text-destructive">Failed to load permission matrix.</div>;

  const permsByResource = (permissions || []).reduce((acc, p) => {
    if (!acc[p.resource]) acc[p.resource] = [];
    acc[p.resource].push(p);
    return acc;
  }, {} as Record<string, GovernancePermission[]>);

  const resources = Object.keys(permsByResource);

  return (
    <div className="w-full overflow-auto rounded-md border border-border bg-card">
      <table role="grid" aria-rowcount={resources.length + 1} aria-label="Role Permission Matrix" className="w-full text-sm text-left">
        <caption className="sr-only">Permission assignment matrix mapping resources to actions</caption>
        <thead className="bg-muted/50 text-muted-foreground uppercase text-xs">
          <tr role="row">
            <th scope="col" role="columnheader" className="p-3">Resource</th>
            <th scope="col" role="columnheader" className="p-3 text-center">Read</th>
            <th scope="col" role="columnheader" className="p-3 text-center">Write</th>
            <th scope="col" role="columnheader" className="p-3 text-center">Delete</th>
            <th scope="col" role="columnheader" className="p-3 text-center">Execute</th>
          </tr>
        </thead>
        <tbody>
          {resources.map((resource) => (
            <PermissionRow 
              key={resource} 
              resource={resource} 
              permissions={permsByResource[resource]} 
              onToggle={handleToggle}
            />
          ))}
          {resources.length === 0 && (
            <tr role="row">
              <td role="cell" colSpan={5} className="p-4 text-center text-muted-foreground">
                No permissions defined for this role.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
