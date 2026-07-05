import React, { useState } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAdminUsers, useThresholds } from '../hooks/useAdminUsers';
import type { SectorValue, UserRoleValue } from '@/types/user';

const UsersPanel: React.FC = () => {
  const { data: users, isLoading, isError, create, remove } = useAdminUsers();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRoleValue>('user');
  const [sector, setSector] = useState<SectorValue>('retail');

  const handleCreate = () => {
    if (!email.trim() || password.length < 8) return;
    create.mutate(
      { email: email.trim(), password, role, sector },
      { onSuccess: () => { setEmail(''); setPassword(''); } },
    );
  };

  return (
    <Card>
      <CardContent className="pt-6 flex flex-col gap-4">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_1fr_auto_auto_auto] gap-2 items-end">
          <Input placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input
            type="password"
            placeholder="password (min 8)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRoleValue)}
            className="h-10 px-3 bg-background border border-input rounded text-sm"
          >
            <option value="user">user</option>
            <option value="manager">manager</option>
            <option value="admin">admin</option>
          </select>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value as SectorValue)}
            className="h-10 px-3 bg-background border border-input rounded text-sm"
          >
            <option value="retail">retail</option>
            <option value="service">service</option>
            <option value="education">education</option>
            <option value="agriculture">agriculture</option>
          </select>
          <Button size="sm" onClick={handleCreate} disabled={create.isPending}>
            Add user
          </Button>
        </div>

        {isLoading && <p className="text-muted-foreground">Loading users…</p>}
        {isError && <p className="text-brand-error">Failed to load users.</p>}
        {users && (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted-foreground border-b border-border">
                <th className="py-2">Email</th>
                <th className="py-2">Role</th>
                <th className="py-2">Sector</th>
                <th className="py-2" />
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-border/50">
                  <td className="py-2">{u.email}</td>
                  <td className="py-2">{u.role}</td>
                  <td className="py-2">{u.sector}</td>
                  <td className="py-2 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={remove.isPending}
                      onClick={() => remove.mutate(u.id)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
};

const ThresholdsPanel: React.FC = () => {
  const { data: thresholds, isLoading, isError, update } = useThresholds();

  return (
    <Card>
      <CardContent className="pt-6">
        {isLoading && <p className="text-muted-foreground">Loading thresholds…</p>}
        {isError && <p className="text-brand-error">Failed to load thresholds.</p>}
        {thresholds && (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted-foreground border-b border-border">
                <th className="py-2">Metric</th>
                <th className="py-2">Warning</th>
                <th className="py-2">Critical</th>
                <th className="py-2" />
              </tr>
            </thead>
            <tbody>
              {thresholds.map((t) => (
                <tr key={t.id} className="border-b border-border/50">
                  <td className="py-2 font-medium">{t.label}</td>
                  <td className="py-2">{t.warning_value ?? '—'}</td>
                  <td className="py-2">{t.critical_value ?? '—'}</td>
                  <td className="py-2 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={update.isPending}
                      onClick={() =>
                        update.mutate({
                          id: t.id,
                          body: {
                            warning_value: t.warning_value,
                            critical_value: t.critical_value,
                          },
                        })
                      }
                    >
                      Save
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
};

export const GovernancePage: React.FC = () => {
  return (
    <OSLayout title="Governance & Administration" description="Users, thresholds and org settings">
      <OSSection title="User Directory" description="GET/POST/DELETE /users">
        <UsersPanel />
      </OSSection>

      <OSSection title="KPI Thresholds" description="GET/PUT /thresholds">
        <ThresholdsPanel />
      </OSSection>

      <OSSection title="Audit, Permissions & Policies" description="Not available in the current backend">
        <div className="p-6 text-muted-foreground border border-dashed border-border rounded-lg flex items-center gap-3">
          <Badge variant="outline">Unavailable</Badge>
          <span>These governance surfaces are not exposed by the current API contract.</span>
        </div>
      </OSSection>
    </OSLayout>
  );
};
