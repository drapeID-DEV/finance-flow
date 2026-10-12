import { useEffect, useRef, useState } from 'react';
import { useGetAlertsQuery, type Alert } from '../../api/alertApi';
import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import './AlertNotificationListener.css';

interface ToastNotification {
	id: string;
	title: string;
	message: string;
}

export function AlertNotificationListener() {
	const { data: alerts } = useGetAlertsQuery(undefined, {
		pollingInterval: 30_000,
		refetchOnFocus: true,
		refetchOnReconnect: true
	});

	const { data: instrumentsData } = useGetInstrumentsQuery({
		page: 1,
		page_size: 100
	});

	const previousAlerts = useRef<Map<number, string> | null>(null);
	const [notifications, setNotifications] = useState<ToastNotification[]>([]);

	useEffect(() => {
		if (!alerts) return;

		const previous = previousAlerts.current;

		if (previous) {
			const codes = new Map(
				(instrumentsData?.items ?? []).map((item) => [
					item.id,
					item.code
				])
			);

			const newNotifications: ToastNotification[] = [];

			for (const alert of alerts) {
				const previousStatus = previous.get(alert.id);

				// Notify only when an existing alert changes active -> triggered.
				if (
					alert.status !== 'triggered' ||
					!previousStatus?.startsWith('active:')
				) {
					continue;
				}

				const code =
					codes.get(alert.instrument_id) ??
					`Instrument #${alert.instrument_id}`;

				const target = Number(alert.value).toLocaleString(undefined, {
					maximumFractionDigits: 8
				});

				const condition =
					alert.direction === 'above'
						? 'reached or exceeded'
						: 'fell to or below';

				newNotifications.push({
					id: `${alert.id}-${alert.triggered_at ?? Date.now()}`,
					title: `${code} price alert triggered`,
					message: `The rate ${condition} your target of ${target} UAH.`
				});
			}

			if (newNotifications.length > 0) {
				setNotifications((current) => [
					...current,
					...newNotifications
				]);
			}
		}

		previousAlerts.current = new Map(
			alerts.map((alert: Alert) => [
				alert.id,
				`${alert.status}:${alert.triggered_at ?? ''}`
			])
		);
	}, [alerts, instrumentsData]);

	useEffect(() => {
		const timers = notifications.map((notification) =>
			window.setTimeout(() => {
				setNotifications((current) =>
					current.filter((item) => item.id !== notification.id)
				);
			}, 7000)
		);

		return () => timers.forEach(window.clearTimeout);
	}, [notifications]);

	const dismiss = (id: string) => {
		setNotifications((current) => current.filter((item) => item.id !== id));
	};

	return (
		<div
			className="alert-toast-container"
			aria-live="polite"
			aria-atomic="false"
		>
			{notifications.map((notification) => (
				<article
					className="alert-toast"
					key={notification.id}
					role="status"
				>
					<div className="alert-toast-icon" aria-hidden="true">
						!
					</div>

					<div className="alert-toast-content">
						<strong>{notification.title}</strong>
						<p>{notification.message}</p>
					</div>

					<button
						className="alert-toast-close"
						type="button"
						aria-label="Dismiss notification"
						onClick={() => dismiss(notification.id)}
					>
						×
					</button>
				</article>
			))}
		</div>
	);
}
