// Matches UserOut / UserCreate in openapi.json.

export type UserRoleValue = 'user' | 'manager' | 'admin';
export type SectorValue = 'retail' | 'service' | 'education' | 'agriculture';

export interface UserOut {
  id: string;
  organization_id: string;
  email: string;
  role: string;
  sector: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  role?: UserRoleValue;
  sector: SectorValue;
}
