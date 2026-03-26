<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { authApi } from '$lib/api/auth';
	import Toast from '$lib/components/Toast.svelte';
	import '../app.css';

	const { token, user } = auth;

	// Reactively watch for auth state changes.
	// If you have a token but don't have a profile yet, fetch it instantly.
	$: if ($token && !$user) {
		authApi.me().then(profile => {
			auth.setUser(profile);
		}).catch(error => {
			console.error('Session expired or invalid:', error);
			auth.logout();
		});
	}
</script>

<slot />
<Toast />