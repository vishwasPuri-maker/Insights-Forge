import { apiClient } from '@/services/apiClient';
import type { UserOut, UserCreate } from '@/types/user';

export const userClient = {
  // GET /api/v1/users
  list: async (limit = 50, offset = 0): Promise<UserOut[]> => {
    const { data } = await apiClient.get<UserOut[]>('/users', { params: { limit, offset } });
    return data;
  },

  // POST /api/v1/users
  create: async (body: UserCreate): Promise<UserOut> => {
    const { data } = await apiClient.post<UserOut>('/users', body);
    return data;
  },

  // DELETE /api/v1/users/{user_id}
  remove: async (userId: string): Promise<void> => {
    await apiClient.delete(`/users/${userId}`);
  },
};
