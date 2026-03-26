import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { Role } from '$lib/api/auth';

interface User {
	id: number;
	name: string;
	email: string;
	role: Role;
	disability?: string;
}

function createAuthStore() {
	const token = writable<string | null>(
		browser ? localStorage.getItem('token') : null
	);
	const user = writable<User | null>(null);

	const isAuthenticated = derived(token, ($t) => !!$t);

	function setToken(t: string) {
		if (browser) localStorage.setItem('token', t);
		token.set(t);
	}

	function setUser(u: User) { user.set(u); }

	function logout() {
		if (browser) localStorage.removeItem('token');
		token.set(null);
		user.set(null);
	}

	return { token, user, isAuthenticated, setToken, setUser, logout };
}

export const auth = createAuthStore();
