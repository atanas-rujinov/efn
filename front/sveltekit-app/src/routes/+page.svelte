<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';

	onMount(() => {
		const unsub = auth.isAuthenticated.subscribe((val) => {
			if (val) goto('/dashboard');
			else goto('/login');
		});
		return unsub;
	});
</script>
