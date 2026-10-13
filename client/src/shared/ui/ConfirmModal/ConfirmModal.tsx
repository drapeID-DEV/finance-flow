import { useEffect, type ReactNode } from 'react';
import { Button } from '../Button/Button';
import './ConfirmModal.css';

interface ConfirmModalProps {
	isOpen: boolean;
	title: string;
	description: ReactNode;
	confirmText: string;
	cancelText?: string;
	isLoading?: boolean;
	variant?: 'danger' | 'primary';
	onClose: () => void;
	onConfirm: () => void;
}

export function ConfirmModal({
	isOpen,
	title,
	description,
	confirmText,
	cancelText = 'Cancel',
	isLoading = false,
	variant = 'primary',
	onClose,
	onConfirm
}: ConfirmModalProps) {
	useEffect(() => {
		if (!isOpen) {
			return;
		}

		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape' && !isLoading) {
				onClose();
			}
		};

		window.addEventListener('keydown', handleKeyDown);

		return () => {
			window.removeEventListener('keydown', handleKeyDown);
		};
	}, [isOpen, isLoading, onClose]);

	if (!isOpen) {
		return null;
	}

	return (
		<div
			className="confirm-modal-overlay"
			onMouseDown={(event) => {
				if (event.target === event.currentTarget && !isLoading) {
					onClose();
				}
			}}
		>
			<section
				className="confirm-modal"
				role="alertdialog"
				aria-modal="true"
				aria-labelledby="confirm-modal-title"
				aria-describedby="confirm-modal-description"
			>
				<div
					className={`confirm-modal-icon confirm-modal-icon--${variant}`}
					aria-hidden="true"
				>
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
				<h2 id="confirm-modal-title">{title}</h2>
				<div
					id="confirm-modal-description"
					className="confirm-modal-description"
				>
					{description}
				</div>
				<div className="confirm-modal-actions">
					<Button
						type="button"
						variant="secondary"
						disabled={isLoading}
						onClick={onClose}
					>
						{cancelText}
					</Button>
					<Button
						type="button"
						variant={variant}
						disabled={isLoading}
						onClick={onConfirm}
					>
						{isLoading ? 'Please wait...' : confirmText}
					</Button>
				</div>
			</section>
		</div>
	);
}
