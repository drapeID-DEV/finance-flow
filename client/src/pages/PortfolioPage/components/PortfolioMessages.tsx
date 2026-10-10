import { Button } from '../../../shared/ui/Button/Button';

interface PortfolioMessagesProps {
	errorMessage: string;
	successMessage: string;
}

export function PortfolioMessages({
	errorMessage,
	successMessage
}: PortfolioMessagesProps) {
	return (
		<>
			{errorMessage && (
				<p className="portfolio-error" role="alert">
					{errorMessage}
				</p>
			)}

			{successMessage && (
				<p className="portfolio-success" role="status">
					{successMessage}
				</p>
			)}
		</>
	);
}

interface PortfolioLoadErrorProps {
	onRetry: () => void;
}

export function PortfolioLoadError({ onRetry }: PortfolioLoadErrorProps) {
	return (
		<div className="portfolio-message">
			<p>Failed to load portfolio.</p>
			<Button variant="primary" onClick={onRetry}>
				Try again
			</Button>
		</div>
	);
}

export function PortfolioEmpty() {
	return (
		<div className="portfolio-empty">
			<h2>Your portfolio is empty</h2>
			<p>Add a currency or metal using the form above.</p>
		</div>
	);
}
