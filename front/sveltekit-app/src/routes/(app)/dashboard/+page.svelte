<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { driveRequestsApi } from '$lib/api/entities';
	import { onMount, tick } from 'svelte';
	import { notifications } from '$lib/stores/notifications';

	// Extract the user store
	const user = auth.user;
	
	let requests: any[] = [];
	let loadingRequests = false;
	let activeRide: any = null;
	let myRequests: any[] = [];
	let loadingMyRequests = false;

	// ── Map State ──
	let mapEl: HTMLDivElement;
	let map: any;
	let L: any;

	onMount(() => {
		// 1. Enforce authentication
		const unsubAuth = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});

		// 2. Fetch rides based on role
		const unsubUser = user.subscribe((u) => {
			if (u?.role === 'driver') {
				fetchAvailableRequests();
			} else if (u?.role === 'disabled') {
				fetchMyRequests(u.id);
			}
		});

		return () => {
			unsubAuth();
			unsubUser();
			if (map) map.remove();
		};
	});

	async function fetchAvailableRequests() {
		loadingRequests = true;
		try {
			const allRequests = await driveRequestsApi.list();

			// Check if this driver already has an accepted ride in progress
			const myActiveRide = allRequests.find(
				(r) => !r.is_completed && r.is_accepted && r.driver === $user?.id
			);
			if (myActiveRide) {
				activeRide = myActiveRide;
				await tick();
				initMap();
				return;
			}

			// Filter for unclaimed, not accepted, and incomplete rides
			requests = allRequests.filter((r) => !r.is_completed && r.driver === null && !r.is_accepted);
		} catch (error) {
			console.error('Failed to fetch requests:', error);
			notifications.error('Failed to load available rides.');
		} finally {
			loadingRequests = false;
		}
	}

	async function fetchMyRequests(userId: number) {
		loadingMyRequests = true;
		try {
			const all = await driveRequestsApi.list();
			myRequests = all
				.filter((r: any) => r.disabled_rel?.id === userId && !r.is_completed)
				.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
		} catch (error) {
			console.error('Failed to fetch your requests:', error);
			notifications.error('Failed to load your requests.');
		} finally {
			loadingMyRequests = false;
		}
	}

	async function acceptRequest(request: any) {
		try {
			// Update the request with current driver ID
			const updated = await driveRequestsApi.update(request.id, { 
				driver: $user?.id,
				is_accepted: true
			});
			activeRide = updated;
			notifications.success('Ride accepted!');
			
			await tick();
			initMap();
		} catch (error) {
			console.error('Accept error:', error);
			notifications.error('Could not accept the ride.');
		}
	}

	async function cancelRide() {
		if (!activeRide) return;
		try {
			await driveRequestsApi.update(activeRide.id, { is_accepted: false, driver: null });
		} catch (error) {
			console.error('Cancel error:', error);
		} finally {
			activeRide = null;
			fetchAvailableRequests();
		}
	}

	async function completeRide() {
		if (!activeRide) return;
		try {
			await driveRequestsApi.update(activeRide.id, { is_completed: true });
			notifications.success('Ride completed!');
			activeRide = null;
			fetchAvailableRequests();
		} catch (error) {
			notifications.error('Failed to complete ride.');
		}
	}

	// ── Leaflet Loader ──
	async function loadLeaflet(): Promise<void> {
		return new Promise((resolve) => {
			if ((window as any).L) { L = (window as any).L; resolve(); return; }
			const link = document.createElement('link');
			link.rel = 'stylesheet';
			link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
			document.head.appendChild(link);

			const script = document.createElement('script');
			script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
			script.onload = () => { L = (window as any).L; resolve(); };
			document.head.appendChild(script);
		});
	}

	function makeIcon(color: string) {
		return L.divIcon({
			className: '',
			html: `<div style="width:18px;height:18px;border-radius:50% 50% 50% 0;background:${color};border:2px solid #fff;transform:rotate(-45deg);box-shadow:0 2px 8px rgba(0,0,0,0.4)"></div>`,
			iconSize: [18, 18],
			iconAnchor: [9, 18],
		});
	}

	async function initMap() {
		await loadLeaflet();
		if (!mapEl || !activeRide) return;

		map = L.map(mapEl, { zoomControl: true });
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

		const start = [activeRide.start_lat, activeRide.start_lon];
		const dest = [activeRide.dest_lat, activeRide.dest_lon];

		L.marker(start, { icon: makeIcon('#3b82f6') }).addTo(map).bindTooltip('Pickup');
		L.marker(dest, { icon: makeIcon('#10b981') }).addTo(map).bindTooltip('Destination');

		L.polyline([start, dest], { color: 'var(--accent)', weight: 3, dashArray: '5 10' }).addTo(map);
		map.fitBounds(L.latLngBounds([start, dest]), { padding: [40, 40] });
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

		{:else}
			{#if $user.role === 'disabled'}
				<p>Welcome back, {$user.name}.</p>
				<div class="actions">
					<a href="/requests/new" class="action-card">
						<span class="action-card__icon">🚗</span>
						<div>
							<strong>Request a ride</strong>
							<span>Set pickup & destination</span>
						</div>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
						</svg>
					</a>
				</div>

				<section class="my-requests-section">
					<h2>Your Active Requests</h2>
					{#if loadingMyRequests}
						<p class="status-msg">Loading your requests...</p>
					{:else if myRequests.length === 0}
						<p class="status-msg text-secondary">You have no active requests.</p>
					{:else}
						<div class="requests-list">
							{#each myRequests as req}
								<div class="request-card">
									<div class="request-card__header">
										<div class="request-route">
											<div class="location">
												<span class="dot dot-start"></span>
												<span><strong>From:</strong> {req.start_address}</span>
											</div>
											<div class="location">
												<span class="dot dot-dest"></span>
												<span><strong>To:</strong> {req.dest_address}</span>
											</div>
										</div>
										{#if req.is_accepted}
											<span class="badge badge-accepted">✓ Driver on the way</span>
										{:else}
											<span class="badge badge-pending">⏳ Awaiting driver</span>
										{/if}
									</div>
									{#if req.description}<p class="request-desc">"{req.description}"</p>{/if}
								</div>
							{/each}
						</div>
					{/if}
				</section>

			{:else if $user.role === 'driver'}
				{#if activeRide}
					<div class="active-ride-view">
						<header class="view-header">
							<button class="back-link" on:click={cancelRide}>← Back to List</button>
							<h2>Active Ride</h2>
						</header>

						<div class="ride-grid">
							<div class="map-section">
								<div bind:this={mapEl} class="mini-map"></div>
								<div class="route-details">
									<div class="location">
										<span class="dot dot-start"></span>
										<span><strong>Pickup:</strong> {activeRide.start_address}</span>
									</div>
									<div class="location">
										<span class="dot dot-dest"></span>
										<span><strong>Destination:</strong> {activeRide.dest_address}</span>
									</div>
								</div>
							</div>

							<aside class="passenger-card">
								<h3>Passenger Information</h3>
								<div class="info-group">
									<span class="label">Name</span>
									<span class="value">{activeRide.disabled_rel.name}</span>
								</div>
								<div class="info-group">
									<span class="label">Disability</span>
									<span class="value">{activeRide.disabled_rel.disability}</span>
								</div>
								<div class="info-group">
									<span class="label">Phone Number</span>
									<span class="value phone-number">{activeRide.disabled_rel.phone || 'No phone provided'}</span>
								</div>
								
								<button class="btn-primary complete-btn" on:click={completeRide}>
									Mark as Completed
								</button>
							</aside>
						</div>
					</div>

				{:else}
					<p>Welcome, {$user.name}. Here are the available requests.</p>
					{#if loadingRequests}
						<p class="status-msg">Fetching available rides...</p>
					{:else if requests.length === 0}
						<p class="status-msg text-secondary">There are no open requests at the moment.</p>
					{:else}
						<div class="requests-list">
							{#each requests as request}
								<div class="request-card">
									<div class="requester-info">
										<span class="requester-avatar">{request.disabled_rel.name.charAt(0).toUpperCase()}</span>
										<div>
											<span class="requester-name">{request.disabled_rel.name}</span>
											<span class="requester-disability">{request.disabled_rel.disability}</span>
										</div>
									</div>
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
									{#if request.description}<p class="request-desc">"{request.description}"</p>{/if}
									<button class="btn-primary btn-small" on:click={() => acceptRequest(request)}>
										Accept Ride
									</button>
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			{:else}
				<p>Role unknown. Please try logging in again.</p>
			{/if}
		{/if}
	</main>
</div>

<style>
	.shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg-body); }
	.nav { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; border-bottom: 1px solid var(--border); background: var(--bg-card); }
	.nav__logo { display: flex; align-items: center; gap: 0.5rem; }
	.nav__mark { color: var(--accent); }
	.nav__name { font-family: var(--font-display); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
	.nav__logout { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; }
	.main { flex: 1; padding: 3rem 2rem; display: flex; flex-direction: column; gap: 1.5rem; max-width: 1200px; margin: 0 auto; width: 100%; }
	h1 { font-family: var(--font-display); font-size: 2rem; font-weight: 700; }

	.active-ride-view { display: flex; flex-direction: column; gap: 1.5rem; }
	.view-header { display: flex; flex-direction: column; gap: 0.5rem; }
	.back-link { background: none; border: none; color: var(--text-secondary); cursor: pointer; text-align: left; padding: 0; font-size: 0.9rem; }
	.ride-grid { display: grid; grid-template-columns: 1fr 350px; gap: 2rem; }
	@media (max-width: 900px) { .ride-grid { grid-template-columns: 1fr; } }

	.mini-map { height: 400px; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; margin-bottom: 1.5rem; }
	:global(.leaflet-tile) { filter: brightness(0.85) saturate(0.8); }

	.passenger-card { background: var(--bg-card); padding: 1.5rem; border-radius: var(--radius); border: 1px solid var(--border); display: flex; flex-direction: column; gap: 1.25rem; height: fit-content; }
	.info-group { display: flex; flex-direction: column; gap: 0.25rem; }
	.label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }
	.phone-number { color: var(--accent); font-weight: 700; font-family: monospace; font-size: 1.1rem; }
	.complete-btn { width: 100%; margin-top: 1rem; }

	.actions { display: flex; gap: 1rem; flex-wrap: wrap; }
	.action-card { display: flex; align-items: center; gap: 1rem; padding: 1.25rem 1.5rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); color: inherit; text-decoration: none; transition: transform 0.2s; flex: 1; min-width: 250px; }
	.action-card:hover { transform: translateY(-2px); border-color: var(--border-hover); }

	.requests-list { display: flex; flex-direction: column; gap: 1rem; }
	.request-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
	.requester-info { display: flex; align-items: center; gap: 0.75rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
	.requester-avatar { width: 2.25rem; height: 2.25rem; border-radius: 50%; background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; }
	.location { display: flex; align-items: center; gap: 0.75rem; }
	.dot { width: 10px; height: 10px; border-radius: 50%; }
	.dot-start { background: #3b82f6; }
	.dot-dest { background: #10b981; }
	.request-desc { font-style: italic; color: var(--text-secondary); background: var(--bg-body); padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.9rem; }
	.btn-small {
		padding: 0.35rem 0.8rem;
		font-size: 0.8rem;
		width: fit-content; /* prevents stretching */
		align-self: flex-start; /* keeps it compact */
	}
	.btn-primary { background: var(--accent); color: #fff; border: none; padding: 0.5rem 1.25rem; border-radius: var(--radius-sm); font-weight: 600; cursor: pointer; }

	.my-requests-section { display: flex; flex-direction: column; gap: 1rem; }
	.my-requests-section h2 { font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; }
	.request-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
	.badge { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
	.badge-accepted { background: #d1fae5; color: #065f46; }
	.badge-pending { background: #fef3c7; color: #92400e; }
</style>