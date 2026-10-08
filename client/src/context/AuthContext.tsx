import {
	createContext,
	useContext,
	useEffect,
	useState,
	type ReactNode
} from 'react';
import {
	getCurrentUser,
	login as loginRequest,
	logout as logoutRequest,
	type LoginRequest,
	type User
} from '../api/auth';

interface AuthContextValue {
	user: User | null;
	loading: boolean;
	login: (data: LoginRequest) => Promise<void>;
	logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
	children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
	const [user, setUser] = useState<User | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		async function loadUser() {
			try {
				const currentUser = await getCurrentUser();
				setUser(currentUser);
			} catch {
				setUser(null);
			} finally {
				setLoading(false);
			}
		}

		void loadUser();
	}, []);

	async function login(data: LoginRequest) {
		await loginRequest(data);
		const currentUser = await getCurrentUser();
		setUser(currentUser);
	}

	async function logout() {
		await logoutRequest();
		setUser(null);
	}

	return (
		<AuthContext.Provider value={{ user, loading, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth(): AuthContextValue {
	const context = useContext(AuthContext);

	if (context === undefined) {
		throw new Error('useAuth must be used within AuthProvider');
	}

	return context;
}
