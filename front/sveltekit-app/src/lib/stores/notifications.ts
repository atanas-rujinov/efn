import { writable } from 'svelte/store';

export type NotificationType = 'success' | 'error' | 'info';

export interface Notification {
	id: string;
	type: NotificationType;
	message: string;
}

function createNotificationStore() {
	const { subscribe, update } = writable<Notification[]>([]);

	function add(type: NotificationType, message: string, duration = 4000) {
		const id = crypto.randomUUID();
		update((n) => [...n, { id, type, message }]);
		setTimeout(() => remove(id), duration);
	}

	function remove(id: string) {
		update((n) => n.filter((notif) => notif.id !== id));
	}

	return {
		subscribe,
		success: (msg: string) => add('success', msg),
		error: (msg: string) => add('error', msg),
		info: (msg: string) => add('info', msg),
		remove
	};
}

export const notifications = createNotificationStore();
