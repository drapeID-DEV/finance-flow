import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const baseApi = createApi({
	reducerPath: 'api',
	baseQuery: fetchBaseQuery({
		baseUrl: 'http://localhost:8000/api/v1',
		credentials: 'include'
	}),
	tagTypes: ['Auth', 'Instrument', 'Rate', 'Portfolio', 'Alert'],
	endpoints: () => ({})
});
