export interface Sector {
  id: string;
  tenant_id: string;
  name: string;
  description: string;
  type: 'retail' | 'service_operations' | 'education' | 'agriculture' | 'custom';
}
