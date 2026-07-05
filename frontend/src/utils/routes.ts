import type { UserRole } from '@/types/auth';

export type OperatingSystemType = 'dashboard' | 'reasoning' | 'simulations' | 'recommendation' | 'governance' | 'chat';

export const buildOperatingSystemRoute = (
  tenantId: string,
  sectorId: string,
  operatingSystem: OperatingSystemType
): string => {
  const osPath = operatingSystem === 'governance' ? 'admin' : operatingSystem;
  return `/${tenantId}/${sectorId}/${osPath}`;
};

export const roleGuard = (role: UserRole | null | undefined, os: OperatingSystemType): boolean => {
  if (os === 'governance') {
    return role === 'admin';
  }
  return true;
};
