import type { Instrument } from '../../../api/instrumentsApi';
import { ConfirmModal } from '../../../shared/ui/ConfirmModal/ConfirmModal';

interface InstrumentStatusModalProps {
	instrument: Instrument | null;
	isLoading: boolean;
	onClose: () => void;
	onConfirm: () => void;
}

export function InstrumentStatusModal({
	instrument,
	isLoading,
	onClose,
	onConfirm
}: InstrumentStatusModalProps) {
	const isActive = instrument?.is_active ?? false;

	return (
		<ConfirmModal
			isOpen={instrument !== null}
			isLoading={isLoading}
			title={isActive ? 'Disable instrument?' : 'Enable instrument?'}
			description={
				<>
					Are you sure you want to {isActive ? 'disable' : 'enable'}{' '}
					<strong>{instrument?.code}</strong>
					{isActive
						? '? It will no longer appear among available instruments.'
						: '? It will become available to users again.'}
				</>
			}
			confirmText={isActive ? 'Disable instrument' : 'Enable instrument'}
			variant={isActive ? 'danger' : 'primary'}
			onClose={onClose}
			onConfirm={onConfirm}
		/>
	);
}
