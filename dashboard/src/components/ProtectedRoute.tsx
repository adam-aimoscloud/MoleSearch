import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  useEffect(() => {
    console.log('ProtectedRoute - isAuthenticated:', isAuthenticated);
    console.log('ProtectedRoute - current location:', location.pathname);
  }, [isAuthenticated, location]);

  if (!isAuthenticated) {
    console.log('ProtectedRoute - redirecting to login');
    // redirect to login page and save return URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('ProtectedRoute - rendering protected content');
  return <>{children}</>;
};

export default ProtectedRoute; 