import { api } from './client';

// ─── Drivers ──────────────────────────────────────────────────────────────────

export interface Driver {
	id: number;
	name: string;
	email: string;
	phone?: string;
	license_number?: string;
	[key: string]: unknown;
}

export const driversApi = {
	list: () => api.get<Driver[]>('/drivers/'),
	get: (id: number) => api.get<Driver>(`/drivers/${id}`),
	create: (data: Partial<Driver>) => api.post<Driver>('/drivers/', data),
	update: (id: number, data: Partial<Driver>) => api.patch<Driver>(`/drivers/${id}`, data),
	delete: (id: number) => api.delete<void>(`/drivers/${id}`)
};

// ─── Disabled Users ───────────────────────────────────────────────────────────

export interface DisabledUser {
	id: number;
	name: string;
	email: string;
	phone?: string;
	disability_type?: string;
	[key: string]: unknown;
}

export const disabledApi = {
	list: () => api.get<DisabledUser[]>('/disabled/'),
	get: (id: number) => api.get<DisabledUser>(`/disabled/${id}`),
	create: (data: Partial<DisabledUser>) => api.post<DisabledUser>('/disabled/', data),
	update: (id: number, data: Partial<DisabledUser>) => api.patch<DisabledUser>(`/disabled/${id}`, data),
	delete: (id: number) => api.delete<void>(`/disabled/${id}`)
};

// ─── Cars ─────────────────────────────────────────────────────────────────────

export interface Car {
	id: number;
	make: string;
	model: string;
	year?: number;
	plate?: string;
	driver_id?: number;
	[key: string]: unknown;
}

export const carsApi = {
	list: () => api.get<Car[]>('/cars/'),
	get: (id: number) => api.get<Car>(`/cars/${id}`),
	create: (data: Partial<Car>) => api.post<Car>('/cars/', data),
	update: (id: number, data: Partial<Car>) => api.patch<Car>(`/cars/${id}`, data),
	delete: (id: number) => api.delete<void>(`/cars/${id}`)
};

// ─── Drive Requests ───────────────────────────────────────────────────────────

export interface DriveRequest {
	id: number;
	created_at?: string;
	description: string;
	start_address: string;
	start_lat?: number;
	start_lon?: number;
	dest_address: string;
	dest_lat?: number;
	dest_lon?: number;
	is_completed: boolean;
	is_accepted?: boolean | null;
	driver: number | null;
	disabled?: number;
	disabled_rel?: DisabledUser;
	[key: string]: unknown;
}

export const driveRequestsApi = {
	list: () => api.get<DriveRequest[]>('/drive-requests/'),
	get: (id: number) => api.get<DriveRequest>(`/drive-requests/${id}`),
	create: (data: Partial<DriveRequest>) => api.post<DriveRequest>('/drive-requests/', data),
	update: (id: number, data: Partial<DriveRequest>) => api.patch<DriveRequest>(`/drive-requests/${id}`, data),
	delete: (id: number) => api.delete<void>(`/drive-requests/${id}`)
};

// ─── Shop Requests ────────────────────────────────────────────────────────────

export interface ShopRequest {
	id: number;
	created_at?: string;
	description: string;
	start_address: string;
	start_lat?: number;
	start_lon?: number;
	dest_address: string;
	dest_lat?: number;
	dest_lon?: number;
	is_completed: boolean;
	driver: number | null;
	disabled?: number;
	disabled_rel?: DisabledUser;
	[key: string]: unknown;
}

export const shopRequestsApi = {
	list: () => api.get<ShopRequest[]>('/shop-requests/'),
	get: (id: number) => api.get<ShopRequest>(`/shop-requests/${id}`),
	create: (data: Partial<ShopRequest>) => api.post<ShopRequest>('/shop-requests/', data),
	update: (id: number, data: Partial<ShopRequest>) => api.patch<ShopRequest>(`/shop-requests/${id}`, data),
	delete: (id: number) => api.delete<void>(`/shop-requests/${id}`)
};

// ─── Reviews ──────────────────────────────────────────────────────────────────

export interface Review {
	id: number;
	created_at: string;
	rating: number;
	comment?: string;
	driver: number;
	author: number;
	[key: string]: unknown;
}

export interface ReviewWithDriverName extends Review {
	driver_name: string;
}

export interface DriverStats {
	driver_id: number;
	driver_name: string;
	average_rating: number;
	total_reviews: number;
	recent_reviews: ReviewWithDriverName[];
	group_ratings: {
		label: string;
		average_rating: number;
		total_reviews: number;
	}[];
}

export const reviewsApi = {
	list: () => api.get<Review[]>('/reviews/'),
	get: (id: number) => api.get<Review>(`/reviews/${id}`),
	getByDriver: (driverId: number) => api.get<Review[]>(`/reviews/by-driver/${driverId}`),
	getDriverStats: (driverId: number, limit: number = 10) =>
		api.get<DriverStats>(`/reviews/driver/${driverId}?limit=${limit}`),
	getMyReviews: () => api.get<ReviewWithDriverName[]>('/reviews/my-reviews'),
	create: (data: Partial<Review>) => api.post<Review>('/reviews/', data),
	update: (id: number, data: Partial<Review>) => api.patch<Review>(`/reviews/${id}`, data),
	delete: (id: number) => api.delete<void>(`/reviews/${id}`)
};
