<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { driveRequestsApi } from '$lib/api/entities'; // NOTE: Ensure this path is correct based on your setup
	import { onMount } from 'svelte';
	import { notifications } from '$lib/stores/notifications';

	// Extract the user store
	const user = auth.user;
	
	let requests: any[] = [];
	let loadingRequests = false;

	onMount(() => {
		// 1. Enforce authentication: Redirect to login if not logged in
		const unsubAuth = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});

		// 2. Listen to the user profile: If they are a driver, fetch the rides
		const unsubUser = user.subscribe((u) => {
			if (u?.role === 'driver') {
				fetchAvailableRequests();
			}
		});

		return () => {
			unsubAuth();
			unsubUser();
		};
	});

	async function fetchAvailableRequests() {
		loadingRequests = true;
		try {
			const allRequests = await driveRequestsApi.list();
			// Filter out requests that are completed or already claimed by a driver
			requests = allRequests.filter((r) => !r.is_completed && r.driver === null);
		} catch (error) {
			console.error('Failed to fetch requests:', error);
			notifications.error('Failed to load available rides.');
		} finally {
			loadingRequests = false;
		}
	}

	function logout() {
		auth.logout();
		goto('/login');
	}
</script>

<svelte:head><title>Dashboard — Fleet</title></svelte:head>

<div class="shell">
	<nav class="nav">
		<div class="nav__logo">
			<span class="nav__mark">▲</span>
			<span class="nav__name">Fleet</span>
		</div>
		<button class="nav__logout" on:click={logout}>Sign out</button>
	</nav>

	<main class="main">
		<h1>Dashboard</h1>

		{#if !$user}
			<p class="status-msg">Loading your profile...</p>

		{:else if $user.role === 'disabled'}
			<p>What would you like to do today, {$user.name}?</p>

			<div class="actions">
				<a href="/requests/new" class="action-card">
					<span class="action-card__icon">🚗</span>
					<div>
						<strong>Request a ride</strong>
						<span>Set pickup & destination</span>
					</div>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<line x1="5" y1="12" x2="19" y2="12"/>
						<polyline points="12 5 19 12 12 19"/>
					</svg>
				</a>

				<a href="/reviews" class="action-card">
					<span class="action-card__icon">⭐</span>
					<div>
						<strong>Write a review</strong>
						<span>Rate your experience</span>
					</div>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<line x1="5" y1="12" x2="19" y2="12"/>
						<polyline points="12 5 19 12 12 19"/>
					</svg>
				</a>
			</div>

		{:else if $user.role === 'driver'}
			<p>Welcome, {$user.name}. Here are the available requests waiting for a driver.</p>

			{#if loadingRequests}
				<p class="status-msg">Fetching available rides...</p>
			{:else if requests.length === 0}
				<p class="status-msg text-secondary">There are no open requests at the moment.</p>
			{:else}
				<div class="requests-list">
					{#each requests as request}
						<div class="request-card">
							<div class="request-route">
								<div class="location">
									<span class="dot dot-start"></span>
									<span><strong>From:</strong> {request.start_address}</span>
								</div>
								<div class="location">
									<span class="dot dot-dest"></span>
									<span><strong>To:</strong> {request.dest_address}</span>
								</div>
							</div>
							{#if request.description}
								<p class="request-desc">"{request.description}"</p>
							{/if}
							
							<button class="btn-primary">Accept Ride</button>
						</div>
					{/each}
				</div>
			{/if}
            
        {:else}
			<p>Hmm, we couldn't determine your role. Please try logging in again.</p>
		{/if}
	</main>
</div>

<style>
	/* ── BASE LAYOUT ──────────────────────────────────────────────────────── */
	.shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg-body); }
	
	.nav { 
		display: flex; justify-content: space-between; align-items: center; 
		padding: 1.25rem 2rem; border-bottom: 1px solid var(--border); 
		background: var(--bg-card); 
	}
	.nav__logo { display: flex; align-items: center; gap: 0.5rem; }
	.nav__mark { color: var(--accent); }
	.nav__name {
		font-family: var(--font-display); font-weight: 700;
		letter-spacing: 0.08em; text-transform: uppercase;
	}
	.nav__logout {
		background: none; border: 1px solid var(--border);
		color: var(--text-secondary); padding: 0.5rem 1rem;
		border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer;
		transition: border-color 0.2s, color 0.2s;
	}
	.nav__logout:hover { border-color: var(--border-hover); color: var(--text-primary); }

	.main { flex: 1; padding: 3rem 2rem; display: flex; flex-direction: column; gap: 1.5rem; max-width: 1200px; margin: 0 auto; width: 100%; }
	h1 { font-family: var(--font-display); font-size: 2rem; font-weight: 700; }
	p { color: var(--text-secondary); }

	/* ── PASSENGER ACTIONS ─────────────────────────────────────────────────── */
	.actions { display: flex; gap: 1rem; flex-wrap: wrap; }
	.action-card {
		display: flex; align-items: center; gap: 1rem;
		padding: 1.25rem 1.5rem;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		color: inherit; text-decoration: none;
		transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
		flex: 1; min-width: 250px; max-width: 400px;
	}
	.action-card:hover {
		border-color: var(--border-hover);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0,0,0,0.05);
	}
	.action-card__icon { font-size: 1.5rem; }
	.action-card div { display: flex; flex-direction: column; gap: 0.25rem; flex: 1; }
	.action-card div strong { font-weight: 600; font-family: var(--font-display); }
	.action-card div span { font-size: 0.875rem; color: var(--text-secondary); }
	.action-card svg { color: var(--text-secondary); transition: transform 0.2s, color 0.2s; }
	.action-card:hover svg { transform: translateX(4px); color: var(--text-primary); }

	/* ── DRIVER REQUESTS LIST ─────────────────────────────────────────────── */
	.requests-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-top: 1rem;
	}
	
	.request-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		transition: border-color 0.2s;
	}
	
	.request-card:hover { border-color: var(--border-hover); }

	.request-route { display: flex; flex-direction: column; gap: 0.75rem; }
	
	.location { display: flex; align-items: center; gap: 0.75rem; color: var(--text-primary); }
	
	.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
	.dot-start { background-color: #3b82f6; } /* Blue */
	.dot-dest { background-color: #10b981; }  /* Green */

	.request-desc {
		font-style: italic;
		color: var(--text-secondary);
		background: var(--bg-body);
		padding: 0.75rem;
		border-radius: var(--radius-sm);
		font-size: 0.9rem;
		margin: 0;
	}

	.btn-primary {
		align-self: flex-start;
		background: var(--accent, #000);
		color: #fff;
		border: none;
		padding: 0.5rem 1.25rem;
		border-radius: var(--radius-sm);
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.2s;
		margin-top: 0.5rem;
	}
	.btn-primary:hover { opacity: 0.8; }
	
	.status-msg { margin-top: 1rem; font-style: italic; }
	.text-secondary { color: var(--text-secondary); }
</style>