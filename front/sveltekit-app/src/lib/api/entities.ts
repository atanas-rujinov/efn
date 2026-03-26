import { api } from "./client";

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
    list: () => api.get<Driver[]>("/drivers/"),
    get: (id: number) => api.get<Driver>(`/drivers/${id}`),
    create: (data: Partial<Driver>) => api.post<Driver>("/drivers/", data),
    update: (id: number, data: Partial<Driver>) =>
        api.patch<Driver>(`/drivers/${id}`, data),
    delete: (id: number) => api.delete<void>(`/drivers/${id}`),
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
    list: () => api.get<DisabledUser[]>("/disabled/"),
    get: (id: number) => api.get<DisabledUser>(`/disabled/${id}`),
    create: (data: Partial<DisabledUser>) =>
        api.post<DisabledUser>("/disabled/", data),
    update: (id: number, data: Partial<DisabledUser>) =>
        api.patch<DisabledUser>(`/disabled/${id}`, data),
    delete: (id: number) => api.delete<void>(`/disabled/${id}`),
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
    list: () => api.get<Car[]>("/cars/"),
    get: (id: number) => api.get<Car>(`/cars/${id}`),
    create: (data: Partial<Car>) => api.post<Car>("/cars/", data),
    update: (id: number, data: Partial<Car>) =>
        api.patch<Car>(`/cars/${id}`, data),
    delete: (id: number) => api.delete<void>(`/cars/${id}`),
};

// ─── Drive Requests ───────────────────────────────────────────────────────────

export interface DriveRequest {
    id: number;
    user_id: number;
    driver_id?: number;
    pickup_location: string;
    dropoff_location: string;
    status?: string;
    [key: string]: unknown;
}

export const driveRequestsApi = {
    list: () => api.get<DriveRequest[]>("/drive-requests/"),
    get: (id: number) => api.get<DriveRequest>(`/drive-requests/${id}`),
    create: (data: Partial<DriveRequest>) =>
        api.post<DriveRequest>("/drive-requests/", data),
    update: (id: number, data: Partial<DriveRequest>) =>
        api.patch<DriveRequest>(`/drive-requests/${id}`, data),
    delete: (id: number) => api.delete<void>(`/drive-requests/${id}`),
};

// ─── Shop Requests ────────────────────────────────────────────────────────────

export interface ShopRequest {
    id: number;
    user_id: number;
    driver_id?: number;
    shop_name: string;
    items?: string;
    status?: string;
    [key: string]: unknown;
}

export const shopRequestsApi = {
    list: () => api.get<ShopRequest[]>("/shop-requests/"),
    get: (id: number) => api.get<ShopRequest>(`/shop-requests/${id}`),
    create: (data: Partial<ShopRequest>) =>
        api.post<ShopRequest>("/shop-requests/", data),
    update: (id: number, data: Partial<ShopRequest>) =>
        api.patch<ShopRequest>(`/shop-requests/${id}`, data),
    delete: (id: number) => api.delete<void>(`/shop-requests/${id}`),
};

// ─── Reviews ──────────────────────────────────────────────────────────────────

export interface Review {
    id: number;
    user_id: number;
    driver_id: number;
    rating: number;
    comment?: string;
    [key: string]: unknown;
}

export const reviewsApi = {
    list: () => api.get<Review[]>("/reviews/"),
    get: (id: number) => api.get<Review>(`/reviews/${id}`),
    create: (data: Partial<Review>) => api.post<Review>("/reviews/", data),
    update: (id: number, data: Partial<Review>) =>
        api.patch<Review>(`/reviews/${id}`, data),
    delete: (id: number) => api.delete<void>(`/reviews/${id}`),
};

// ─── Other Requests ───────────────────────────────────────────────────────────

export interface OtherRequest {
    id: number;
    description: string;
    dest_address: string;
    dest_lat: number;
    dest_lon: number;
    is_completed: boolean;
    is_accepted?: boolean;
    driver?: any;
    disabled?: any;
    created_at?: string;
    [key: string]: unknown;
}

export const otherRequestsApi = {
    list: () => api.get<OtherRequest[]>("/other-requests/"),
    get: (id: number) => api.get<OtherRequest>(`/other-requests/${id}`),
    create: (data: Partial<OtherRequest>) =>
        api.post<OtherRequest>("/other-requests/", data),
    update: (id: number, data: Partial<OtherRequest>) =>
        api.patch<OtherRequest>(`/other-requests/${id}`, data),
    delete: (id: number) => api.delete<void>(`/other-requests/${id}`),
};
