import { baseApi } from './baseApi';

export interface LoginRequest {
	email: string;
	password: string;
}

export interface RegisterRequest {
	email: string;
	password: string;
}

export interface User {
	id: number;
	email: string;
	role: string;
}

export interface LoginResponse {
	message: string;
}

export interface RegisterResponse {
	id: number;
	email: string;
	role: string;
}

export const authApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		login: builder.mutation<LoginResponse, LoginRequest>({
			query: (data) => ({
				url: '/auth/login',
				method: 'POST',
				body: data
			}),
			invalidatesTags: ['Auth']
		}),
		register: builder.mutation<RegisterResponse, RegisterRequest>({
			query: (data) => ({
				url: '/auth/register',
				method: 'POST',
				body: data
			})
		}),
		getCurrentUser: builder.query<User, void>({
			query: () => '/auth/me',
			providesTags: ['Auth']
		}),
		logout: builder.mutation<{ message: string }, void>({
			query: () => ({
				url: '/auth/logout',
				method: 'POST'
			}),
			invalidatesTags: ['Auth']
		})
	})
});

export const {
	useLoginMutation,
	useRegisterMutation,
	useGetCurrentUserQuery,
	useLogoutMutation
} = authApi;
