import { apiClient } from './client';

export interface RegisterRequest {
	email: string;
	password: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface RegisterResponse {
	id: number;
	email: string;
	role: string;
}

export interface LoginResponse {
	message: string;
}

export interface User {
	id: number;
	email: string;
	role: string;
}

export async function register(
	data: RegisterRequest
): Promise<RegisterResponse> {
	const response = await apiClient.post<RegisterResponse>(
		'/auth/register',
		data
	);

	return response.data;
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
	const response = await apiClient.post<LoginResponse>('/auth/login', data);

	return response.data;
}

export async function getCurrentUser(): Promise<User> {
	const response = await apiClient.get<User>('/auth/me');

	return response.data;
}

export async function logout(): Promise<void> {
	await apiClient.post('/auth/logout');
}
