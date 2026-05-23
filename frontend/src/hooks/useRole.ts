import { useAuth } from '@/hooks/useAuth';

export const useRole = () => {
  const { user } = useAuth();
  return user?.role ?? null;
};
