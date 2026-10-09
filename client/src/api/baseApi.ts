import {
	createApi,
	fetchBaseQuery,
	type BaseQueryFn,
	type FetchArgs,
	type FetchBaseQueryError
} from '@reduxjs/toolkit/query/react';
import { sessionExpired } from '../store/authSlice';

const rawBaseQuery = fetchBaseQuery({
	baseUrl: 'http://localhost:8000/api/v1',
	credentials: 'include'
});

const baseQueryWithReauth: BaseQueryFn<
	string | FetchArgs,
	unknown,
	FetchBaseQueryError
> = async (args, api, extraOptions) => {
	let result = await rawBaseQuery(args, api, extraOptions);

	if (result.error?.status === 401) {
		const refreshResult = await rawBaseQuery(
			{
				url: '/auth/refresh',
				method: 'POST'
			},
			api,
			extraOptions
		);

		if (refreshResult.data) {
			result = await rawBaseQuery(args, api, extraOptions);
		} else {
			api.dispatch(sessionExpired());
		}
	}

	return result;
};

export const baseApi = createApi({
	reducerPath: 'api',
	baseQuery: baseQueryWithReauth,
	tagTypes: ['Auth', 'Instrument', 'Rate', 'Portfolio', 'Alert'],
	endpoints: () => ({})
});
