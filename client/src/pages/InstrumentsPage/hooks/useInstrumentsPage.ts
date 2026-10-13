import { useState } from 'react';
import { useGetCurrentUserQuery } from '../../../api/authApi';
import {
	useGetInstrumentsQuery,
	useGetAllAdminInstrumentsQuery,
	useUpdateInstrumentStatusMutation,
	type Instrument,
	type InstrumentsQuery
} from '../../../api/instrumentsApi';

const PAGE_SIZE = 20;

export function useInstrumentsPage() {
	const [page, setPage] = useState(1);
	const [search, setSearch] = useState('');
	const [type, setType] = useState<'' | 'currency' | 'metal'>('');
	const [actionError, setActionError] = useState('');
	const [instrumentToToggle, setInstrumentToToggle] =
		useState<Instrument | null>(null);

	const {
		data: user,
		isLoading: isUserLoading,
		isError: isUserError
	} = useGetCurrentUserQuery();

	const isAdmin = user?.role === 'admin';

	const queryParams: InstrumentsQuery = {
		page,
		page_size: PAGE_SIZE,
		search,
		...(type ? { type } : {})
	};

	const userQuery = useGetInstrumentsQuery(queryParams, {
		skip: isUserLoading || isUserError || isAdmin
	});

	const adminQuery = useGetAllAdminInstrumentsQuery(queryParams, {
		skip: isUserLoading || isUserError || !isAdmin
	});

	const [updateStatus, { isLoading: isUpdating }] =
		useUpdateInstrumentStatusMutation();

	const activeQuery = isAdmin ? adminQuery : userQuery;
	const data = activeQuery.data;
	const isLoading = isUserLoading || activeQuery.isLoading;
	const isFetching = activeQuery.isFetching;
	const isError = isUserError || activeQuery.isError;

	const handleSearchChange = (value: string) => {
		setSearch(value);
		setPage(1);
	};

	const handleTypeChange = (value: '' | 'currency' | 'metal') => {
		setType(value);
		setPage(1);
	};

	const handleReset = () => {
		setSearch('');
		setType('');
		setPage(1);
	};

	const handleToggleStatus = async (instrument: Instrument) => {
		const action = instrument.is_active ? 'disable' : 'enable';

		setActionError('');

		try {
			await updateStatus({
				code: instrument.code,
				is_active: !instrument.is_active
			}).unwrap();

			setInstrumentToToggle(null);
		} catch {
			setActionError(
				`Failed to ${action} ${instrument.code}. Please try again.`
			);
		}
	};

	return {
		isAdmin,
		page,
		setPage,
		search,
		type,
		actionError,
		instrumentToToggle,
		setInstrumentToToggle,
		data,
		isLoading,
		isFetching,
		isError,
		isUpdating,
		refetch: activeQuery.refetch,
		handleSearchChange,
		handleTypeChange,
		handleReset,
		handleToggleStatus
	};
}
