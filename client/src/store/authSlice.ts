import { createSlice } from '@reduxjs/toolkit';

interface AuthState {
	sessionExpired: boolean;
}

const initialState: AuthState = {
	sessionExpired: false
};

const authSlice = createSlice({
	name: 'auth',
	initialState,
	reducers: {
		sessionExpired: (state) => {
			state.sessionExpired = true;
		},
		sessionRestored: (state) => {
			state.sessionExpired = false;
		}
	}
});

export const { sessionExpired, sessionRestored } = authSlice.actions;
export default authSlice.reducer;
