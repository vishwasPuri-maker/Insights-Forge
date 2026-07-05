export interface Tenant {
  id: string;
  name: string;
  slug: string;
  industry: string;
  created_at: string;
  status: 'active' | 'suspended' | 'provisioning';
}
