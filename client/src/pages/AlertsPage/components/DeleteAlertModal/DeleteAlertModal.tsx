import { useEffect } from 'react';
import './DeleteAlertModal.css';
import { Button } from '../../../../shared/ui/Button/Button';

interface DeleteAlertModalProps {
	isOpen: boolean;
	isDeleting: boolean;
	alertName: string;
	onClose: () => void;
	onConfirm: () => void;
}

export function DeleteAlertModal({
	isOpen,
	isDeleting,
	alertName,
	onClose,
	onConfirm
}: DeleteAlertModalProps) {
	useEffect(() => {
		if (!isOpen) {
			return;
		}

		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape' && !isDeleting) {
				onClose();
			}
		};

		window.addEventListener('keydown', handleKeyDown);

		return () => {
			window.removeEventListener('keydown', handleKeyDown);
		};
	}, [isOpen, isDeleting, onClose]);

	if (!isOpen) {
		return null;
	}

	return (
		<div
			className="delete-modal-overlay"
			onMouseDown={(event) => {
				if (event.target === event.currentTarget && !isDeleting) {
					onClose();
				}
			}}
		>
			<section
				className="delete-modal"
				role="alertdialog"
				aria-modal="true"
				aria-labelledby="delete-modal-title"
				aria-describedby="delete-modal-description"
			>
				<div className="delete-modal-icon" aria-hidden="true">
					<svg
						width="28"
						height="28"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						strokeWidth="1.8"
						strokeLinecap="round"
						strokeLinejoin="round"
					>
						<path d="M12 9v4" />
						<path d="M12 17h.01" />
						<path d="M10.3 3.9 2.6 17.2A2 2 0 0 0 4.3 20h15.4a2 2 0 0 0 1.7-2.8L13.7 3.9a2 2 0 0 0-3.4 0Z" />
					</svg>
				</div>
				<h2 id="delete-modal-title">Delete price alert?</h2>
				<p id="delete-modal-description">
					Are you sure you want to delete the alert for{' '}
					<strong>{alertName}</strong>? This action cannot be undone.
				</p>
				<div className="delete-modal-actions">
					<Button
						type="button"
						variant="secondary"
						disabled={isDeleting}
						onClick={onClose}
					>
						Cancel
					</Button>
					<Button
						type="button"
						variant="danger"
						disabled={isDeleting}
						onClick={onConfirm}
					>
						{isDeleting ? 'Deleting...' : 'Delete alert'}
					</Button>
				</div>
			</section>
		</div>
	);
}
