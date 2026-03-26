<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import DriverReviews from '$lib/components/DriverReviews.svelte';
	import { auth } from '$lib/stores/auth';
	import { onMount } from 'svelte';

	let driverId: number;

	onMount(() => {
		const unsub = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});
		return () => unsub();
	});

	$: driverId = Number($page.params.driverId);
</script>

<svelte:head><title>Helper Reviews — Fleet</title></svelte:head>

<div class="shell">
	<div class="header">
		<a class="back" href="/dashboard">← Back</a>
		<h1>Helper Reviews</h1>
	</div>

	{#if Number.isFinite(driverId) && driverId > 0}
		<DriverReviews {driverId} />
	{:else}
		<p class="error">Invalid helper id.</p>
	{/if}
</div>

<style>
	.shell {
		max-width: 900px;
		margin: 0 auto;
		padding: 40px 24px;
	}
	.header {
		display: flex;
		align-items: baseline;
		gap: 16px;
		margin-bottom: 24px;
	}
	.back {
		color: var(--accent);
		text-decoration: none;
		font-size: 14px;
	}
	.error {
		color: var(--danger, #dc2626);
	}
</style>

