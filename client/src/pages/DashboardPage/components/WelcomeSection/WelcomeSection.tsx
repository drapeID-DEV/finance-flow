import './WelcomeSection.css';

interface WelcomeSectionProps {
	email: string;
}

export function WelcomeSection({ email }: WelcomeSectionProps) {
	return (
		<section className="welcome-section">
			<h1>Dashboard</h1>
			<p>
				Welcome, <span>{email}</span>
			</p>
		</section>
	);
}
