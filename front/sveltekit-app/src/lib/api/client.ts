import { browser } from '$app/environment';

const BASE_URL = import.meta.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

function getToken(): string | null {
	if (!browser) return null;
	return localStorage.getItem('token');
}

async function request<T>(
	path: string,
	options: RequestInit = {}
): Promise<T> {
	const token = getToken();

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string>)
	};

	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const res = await fetch(`${BASE_URL}${path}`, {
		...options,
		headers
	});

	if (!res.ok) {
		const error = await res.json().catch(() => ({ detail: res.statusText }));
		throw new ApiError(res.status, error?.detail ?? 'An error occurred');
	}

	if (res.status === 204) return undefined as T;
	return res.json();
}

export class ApiError extends Error {
	constructor(
		public status: number,
		public detail: string
	) {
		super(detail);
		this.name = 'ApiError';
	}
}

export const api = {
	get: <T>(path: string) => request<T>(path),
	post: <T>(path: string, body: unknown) =>
		request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
	patch: <T>(path: string, body: unknown) =>
		request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
	delete: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};
