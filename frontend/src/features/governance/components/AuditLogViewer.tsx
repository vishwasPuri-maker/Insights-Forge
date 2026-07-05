import React, { useRef, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useAudit } from '../hooks/useAudit';
import type { GovernanceAuditEntry } from '@/types/governance';
import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import { createColumnHelper } from '@tanstack/react-table';

interface AuditLogViewerProps {
  initialAudits: GovernanceAuditEntry[];
  tenantId: string;
  role: string;
}

interface AuditRow {
  id: string;
  timestamp: string;
  userId: string;
  action: React.ReactNode;
  resource: string;
  ipAddress: React.ReactNode;
}

const columnHelper = createColumnHelper<AuditRow>();
const columns = [
  columnHelper.accessor('timestamp', { header: 'Timestamp' }),
  columnHelper.accessor('userId', { header: 'User ID' }),
  columnHelper.accessor('action', { header: 'Action' }),
  columnHelper.accessor('resource', { header: 'Resource' }),
  columnHelper.accessor('ipAddress', { header: 'IP Address' }),
];

export const AuditLogViewer: React.FC<AuditLogViewerProps> = ({ initialAudits, tenantId, role }) => {
  const [filter, setFilter] = useState('');
  const { data: remoteAudits, isLoading } = useAudit(tenantId, role, filter);
  
  const displayAudits = (filter ? remoteAudits : (remoteAudits || initialAudits)) || [];
  const parentRef = useRef<HTMLDivElement>(null);

  const isLargeDataset = displayAudits.length >= 100;

  const rowVirtualizer = useVirtualizer({
    count: displayAudits.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
    overscan: 5,
  });

  if (!isLargeDataset) {
    const rowData: AuditRow[] = displayAudits.map(audit => ({
      id: audit.id,
      timestamp: new Date(audit.timestamp).toLocaleString(),
      userId: audit.userId,
      action: <span className="font-mono text-xs px-2 py-1 bg-muted rounded">{audit.action}</span>,
      resource: audit.resource,
      ipAddress: <span className="text-muted-foreground">{audit.ipAddress}</span>
    }));

    return (
      <div className="w-full flex flex-col gap-4">
        <input 
          type="text" 
          placeholder="Filter audit logs..." 
          className="px-3 py-2 border rounded-md max-w-sm bg-background text-sm"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
        {isLoading && filter ? (
          <div className="text-sm text-muted-foreground animate-pulse">Searching...</div>
        ) : (
          <ExecutiveTable 
            columns={columns}
            data={rowData}
          />
        )}
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col gap-4 h-[500px]">
      <input 
        type="text" 
        placeholder="Filter audit logs..." 
        className="px-3 py-2 border rounded-md max-w-sm bg-background text-sm"
        value={filter}
        onChange={e => setFilter(e.target.value)}
      />
      {isLoading && filter ? (
        <div className="text-sm text-muted-foreground animate-pulse">Searching...</div>
      ) : (
        <div 
          ref={parentRef} 
          className="flex-1 overflow-auto border rounded-md border-border bg-card"
        >
          <table role="table" aria-rowcount={displayAudits.length + 1} aria-label="Audit Logs" className="w-full text-sm text-left relative">
            <caption className="sr-only">Immutable audit history</caption>
            <thead className="bg-muted/50 text-muted-foreground uppercase text-xs sticky top-0 z-10">
              <tr role="row">
                <th scope="col" className="p-3">Timestamp</th>
                <th scope="col" className="p-3">User ID</th>
                <th scope="col" className="p-3">Action</th>
                <th scope="col" className="p-3">Resource</th>
                <th scope="col" className="p-3">IP Address</th>
              </tr>
            </thead>
            <tbody style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
              {rowVirtualizer.getVirtualItems().map(virtualRow => {
                const audit = displayAudits[virtualRow.index];
                return (
                  <tr 
                    role="row"
                    aria-rowindex={virtualRow.index + 2}
                    key={virtualRow.index}
                    className="border-b border-border/50 hover:bg-muted/30 absolute top-0 left-0 w-full"
                    style={{ height: `${virtualRow.size}px`, transform: `translateY(${virtualRow.start}px)` }}
                  >
                    <td role="cell" className="p-3 whitespace-nowrap">{new Date(audit.timestamp).toLocaleString()}</td>
                    <td role="cell" className="p-3">{audit.userId}</td>
                    <td role="cell" className="p-3"><span className="font-mono text-xs px-2 py-1 bg-muted rounded">{audit.action}</span></td>
                    <td role="cell" className="p-3">{audit.resource}</td>
                    <td role="cell" className="p-3 text-muted-foreground">{audit.ipAddress}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
