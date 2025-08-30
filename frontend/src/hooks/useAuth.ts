import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { loginUser, registerUser, logoutUser, refreshToken, clearError, updateUser } from '../store/slices/authSlice';
import { User } from '../types';

export const useAuth = () => {
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);

  const login = async (credentials: { username: string; password: string }) => {
    return dispatch(loginUser(credentials));
  };

  const register = async (userData: any) => {
    return dispatch(registerUser(userData));
  };

  const logout = async () => {
    return dispatch(logoutUser());
  };

  const refresh = async () => {
    return dispatch(refreshToken());
  };

  const clearAuthError = () => {
    dispatch(clearError());
  };

  const updateUserData = (userData: Partial<User>) => {
    dispatch(updateUser(userData));
  };

  return {
    user: auth.user,
    tokens: auth.tokens,
    isLoading: auth.isLoading,
    isAuthenticated: auth.isAuthenticated,
    error: auth.error,
    login,
    register,
    logout,
    refresh,
    clearError: clearAuthError,
    updateUser: updateUserData,
  };
};