import {
	createApi,
	fetchBaseQuery,
	type BaseQueryFn,
	type FetchArgs,
	type FetchBaseQueryError
} from '@reduxjs/toolkit/query/react';
import { Mutex } from 'async-mutex';
import { sessionExpired } from '../store/authSlice';

const mutex = new Mutex();

const rawBaseQuery = fetchBaseQuery({
	baseUrl: 'http://localhost:8000/api/v1',
	credentials: 'include'
});

const baseQueryWithReauth: BaseQueryFn<
	string | FetchArgs,
	unknown,
	FetchBaseQueryError
> = async (args, api, extraOptions) => {
	await mutex.waitForUnlock();

	let result = await rawBaseQuery(args, api, extraOptions);

	if (result.error?.status === 401) {
		if (!mutex.isLocked()) {
			const release = await mutex.acquire();

			try {
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
			} finally {
				release();
			}
		} else {
			await mutex.waitForUnlock();

			result = await rawBaseQuery(args, api, extraOptions);

			if (result.error?.status === 401) {
				api.dispatch(sessionExpired());
			}
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
