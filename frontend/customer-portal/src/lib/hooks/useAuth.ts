'use client';

import { useAuth } from '@/lib/context/AuthContext';

export function useAuthHook() {
  return useAuth();
}

export default useAuthHook;
