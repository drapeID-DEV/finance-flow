import { type ReactNode } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useGetCurrentUserQuery } from '../api/authApi';

interface ProtectedRouteProps {
	children?: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
	const location = useLocation();

	const { data: user, isLoading, isError } = useGetCurrentUserQuery();

	if (isLoading) {
		return <h1>Loading...</h1>;
	}

	if (isError || !user) {
		return <Navigate to="/login" replace state={{ from: location }} />;
	}

	return children ? <>{children}</> : <Outlet />;
}
