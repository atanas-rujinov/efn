<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { driveRequestsApi, otherRequestsApi } from '$lib/api/entities';
	import { notifications } from '$lib/stores/notifications';
	import { ApiError } from '$lib/api/client';

	// ── Tab state ─────────────────────────────────────────
	let activeTab: 'ride' | 'other' = 'ride';

	function switchTab(tab: 'ride' | 'other') {
		activeTab = tab;
		// Clear pin mode on tab switch
		pinMode = null;
	}

	// ── Ride form state ───────────────────────────────────
	let description = '';

	let startAddress = '';
	let startLat: number | null = null;
	let startLon: number | null = null;

	let destAddress = '';
	let destLat: number | null = null;
	let destLon: number | null = null;

	// ── Other request form state ──────────────────────────
	let otherDescription = '';
	let otherDestAddress = '';
	let otherDestLat: number | null = null;
	let otherDestLon: number | null = null;
	let otherDestQuery = '';
	let otherDestResults: NominatimResult[] = [];
	let otherDestSearching = false;
	let otherDestDebounce: ReturnType<typeof setTimeout>;

	let loading = false;

	// ── Map state ─────────────────────────────────────────
	let mapEl: HTMLDivElement;
	let map: any;
	let L: any;
	let startMarker: any = null;
	let destMarker: any = null;
	let routeLine: any = null;

	// Which pin is the user placing? null = neither
	let pinMode: 'start' | 'dest' | null = null;

	// ── Address search ────────────────────────────────────
	let startQuery = '';
	let destQuery = '';
	let startResults: NominatimResult[] = [];
	let destResults: NominatimResult[] = [];
	let startSearching = false;
	let destSearching = false;

	interface NominatimResult {
		place_id: number;
		display_name: string;
		lat: string;
		lon: string;
	}

	let startDebounce: ReturnType<typeof setTimeout>;
	let destDebounce: ReturnType<typeof setTimeout>;

	function searchAddress(query: string, which: 'start' | 'dest') {
		if (which === 'start') {
			clearTimeout(startDebounce);
			if (!query.trim()) { startResults = []; return; }
			startSearching = true;
			startDebounce = setTimeout(() => doSearch(query, 'start'), 400);
		} else {
			clearTimeout(destDebounce);
			if (!query.trim()) { destResults = []; return; }
			destSearching = true;
			destDebounce = setTimeout(() => doSearch(query, 'dest'), 400);
		}
	}

	function searchOtherDest(query: string) {
		clearTimeout(otherDestDebounce);
		if (!query.trim()) { otherDestResults = []; return; }
		otherDestSearching = true;
		otherDestDebounce = setTimeout(() => doSearchOtherDest(query), 400);
	}

	async function doSearch(query: string, which: 'start' | 'dest') {
		try {
			const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
			const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
			const data: NominatimResult[] = await res.json();
			if (which === 'start') { startResults = data; startSearching = false; }
			else { destResults = data; destSearching = false; }
		} catch {
			if (which === 'start') startSearching = false;
			else destSearching = false;
		}
	}

	async function doSearchOtherDest(query: string) {
		try {
			const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
			const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
			otherDestResults = await res.json();
		} catch {}
		otherDestSearching = false;
	}

	function pickResult(result: NominatimResult, which: 'start' | 'dest') {
		const lat = parseFloat(result.lat);
		const lon = parseFloat(result.lon);
		const short = result.display_name.split(',').slice(0, 2).join(',').trim();

		if (which === 'start') {
			startAddress = short; startQuery = short;
			startLat = lat; startLon = lon;
			startResults = [];
			placeMarker('start', lat, lon);
		} else {
			destAddress = short; destQuery = short;
			destLat = lat; destLon = lon;
			destResults = [];
			placeMarker('dest', lat, lon);
		}
		fitBounds();
	}

	function pickOtherDest(result: NominatimResult) {
		const lat = parseFloat(result.lat);
		const lon = parseFloat(result.lon);
		const short = result.display_name.split(',').slice(0, 2).join(',').trim();
		otherDestAddress = short; otherDestQuery = short;
		otherDestLat = lat; otherDestLon = lon;
		otherDestResults = [];
		// reuse destMarker slot for other tab
		destMarker?.remove();
		destMarker = L.marker([lat, lon], { icon: makeIcon('#ff4757') })
			.addTo(map)
			.bindTooltip('Destination', { permanent: false });
		startMarker?.remove(); startMarker = null;
		routeLine?.remove(); routeLine = null;
		map.setView([lat, lon], 14);
	}

	// ── Leaflet helpers ───────────────────────────────────
	function makeIcon(color: string) {
		return L.divIcon({
			className: '',
			html: `<div style="
				width:22px;height:22px;border-radius:50% 50% 50% 0;
				background:${color};border:2px solid rgb(0, 0, 0);
				transform:rotate(-45deg);
				box-shadow:0 2px 8px rgba(0,0,0,0.4)"></div>`,
			iconSize: [22, 22],
			iconAnchor: [11, 22],
		});
	}

	function placeMarker(which: 'start' | 'dest', lat: number, lon: number) {
		if (!map) return;
		if (which === 'start') {
			startMarker?.remove();
			startMarker = L.marker([lat, lon], { icon: makeIcon('#e8ff47') })
				.addTo(map)
				.bindTooltip('Pickup', { permanent: false });
		} else {
			destMarker?.remove();
			destMarker = L.marker([lat, lon], { icon: makeIcon('#ff4757') })
				.addTo(map)
				.bindTooltip('Destination', { permanent: false });
		}
		drawRoute();
	}

	function drawRoute() {
		routeLine?.remove();
		if (startMarker && destMarker) {
			routeLine = L.polyline(
				[startMarker.getLatLng(), destMarker.getLatLng()],
				{ color: '#e8ff47', weight: 2, dashArray: '6 6', opacity: 0.7 }
			).addTo(map);
		}
	}

	function fitBounds() {
		if (!map) return;
		if (startMarker && destMarker) {
			map.fitBounds(
				L.latLngBounds([startMarker.getLatLng(), destMarker.getLatLng()]),
				{ padding: [48, 48] }
			);
		} else if (startMarker) {
			map.setView(startMarker.getLatLng(), 14);
		} else if (destMarker) {
			map.setView(destMarker.getLatLng(), 14);
		}
	}

	async function reverseGeocode(lat: number, lon: number): Promise<string> {
		try {
			const res = await fetch(
				`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`,
				{ headers: { 'Accept-Language': 'en' } }
			);
			const data = await res.json();
			return data.display_name?.split(',').slice(0, 2).join(',').trim() ?? `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
		} catch {
			return `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
		}
	}

	// ── Mount map ─────────────────────────────────────────
	onMount(async () => {
		await loadLeaflet();

		map = L.map(mapEl, { zoomControl: true }).setView([42.698, 23.322], 12);

		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '© OpenStreetMap contributors',
			maxZoom: 19,
		}).addTo(map);

		const attr = mapEl.querySelector('.leaflet-control-attribution') as HTMLElement;
		if (attr) attr.style.cssText = 'background:rgba(13,16,24,0.8);color:#7a8099;font-size:10px;';

		map.on('click', async (e: any) => {
			if (!pinMode) return;
			const { lat, lng } = e.latlng;
			const address = await reverseGeocode(lat, lng);

			if (activeTab === 'ride') {
				if (pinMode === 'start') {
					startLat = lat; startLon = lng;
					startAddress = address; startQuery = address;
					placeMarker('start', lat, lng);
				} else {
					destLat = lat; destLon = lng;
					destAddress = address; destQuery = address;
					placeMarker('dest', lat, lng);
				}
			} else {
				// other tab only has a destination pin
				otherDestLat = lat; otherDestLon = lng;
				otherDestAddress = address; otherDestQuery = address;
				destMarker?.remove();
				destMarker = L.marker([lat, lng], { icon: makeIcon('#ff4757') })
					.addTo(map)
					.bindTooltip('Destination', { permanent: false });
				startMarker?.remove(); startMarker = null;
				routeLine?.remove(); routeLine = null;
			}
			pinMode = null;
			fitBounds();
		});
	});

	onDestroy(() => { map?.remove(); });

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

	// ── Submit: Ride ──────────────────────────────────────
	async function handleSubmit() {
		if (!startAddress || startLat === null || startLon === null) {
			notifications.error('Please set a pickup location.');
			return;
		}
		if (!destAddress || destLat === null || destLon === null) {
			notifications.error('Please set a destination.');
			return;
		}

		loading = true;
		try {
			await driveRequestsApi.create({
				description: description.trim() || undefined,
				start_address: startAddress,
				start_lat: startLat,
				start_lon: startLon,
				dest_address: destAddress,
				dest_lat: destLat,
				dest_lon: destLon,
				is_completed: false,
			});
			notifications.success('Ride request submitted!');
			goto('/dashboard');
		} catch (e) {
			if (e instanceof ApiError) notifications.error(e.detail);
			else notifications.error('Something went wrong. Please try again.');
		} finally {
			loading = false;
		}
	}

	// ── Submit: Other ─────────────────────────────────────
	async function handleOtherSubmit() {
		if (!otherDestAddress || otherDestLat === null || otherDestLon === null) {
			notifications.error('Please set a destination.');
			return;
		}

		loading = true;
		try {
			await otherRequestsApi.create({
				description: otherDescription.trim() || undefined,
				dest_address: otherDestAddress,
				dest_lat: otherDestLat,
				dest_lon: otherDestLon,
				is_completed: false,
			});
			notifications.success('Request submitted!');
			goto('/dashboard');
		} catch (e) {
			if (e instanceof ApiError) notifications.error(e.detail);
			else notifications.error('Something went wrong. Please try again.');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>New request — Accessride</title></svelte:head>

<div class="page">
	<!-- Top nav -->
	<nav class="nav">
		<a href="/dashboard" class="nav__back">
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<line x1="19" y1="12" x2="5" y2="12"/>
				<polyline points="12 19 5 12 12 5"/>
			</svg>
			Back
		</a>
		<div class="nav__logo">
			<span class="nav__mark">▲</span>
			<span class="nav__name">Accessride</span>
		</div>
		<div style="width:64px" />
	</nav>

	<div class="layout">
		<!-- Left: form -->
		<aside class="form-col">
			<header class="form-header">
				<p class="eyebrow">New request</p>
				<h1 class="title">What do you need?</h1>
				<p class="subtitle">Choose the type of assistance and fill in the details below.</p>
			</header>

			<!-- ── Tab toggle ── -->
			<div class="tabs" role="tablist">
				<button
					role="tab"
					aria-selected={activeTab === 'ride'}
					class="tab"
					class:tab--active={activeTab === 'ride'}
					on:click={() => switchTab('ride')}
				>
					<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="10"/>
						<path d="M8 12h8M12 8l4 4-4 4"/>
					</svg>
					Ride
				</button>
				<button
					role="tab"
					aria-selected={activeTab === 'other'}
					class="tab"
					class:tab--active={activeTab === 'other'}
					on:click={() => switchTab('other')}
				>
					<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>
					</svg>
					Other
				</button>
			</div>

			<!-- ══ RIDE FORM ══════════════════════════════════ -->
			{#if activeTab === 'ride'}
				<!-- Pickup -->
				<section class="section">
					<div class="section__head">
						<span class="section__dot section__dot--start" />
						<h2>Pickup location</h2>
					</div>

					<div class="address-field">
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
								</svg>
							</span>
							<input
								type="text"
								placeholder="Search pickup address…"
								bind:value={startQuery}
								on:input={() => searchAddress(startQuery, 'start')}
								disabled={loading}
							/>
							{#if startSearching}
								<span class="searching-spinner" />
							{/if}
						</div>

						{#if startResults.length > 0}
							<ul class="results">
								{#each startResults as r}
									<li>
										<button type="button" on:click={() => pickResult(r, 'start')}>
											<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
												<circle cx="12" cy="10" r="3"/>
											</svg>
											{r.display_name}
										</button>
									</li>
								{/each}
							</ul>
						{/if}

						<button
							type="button"
							class="pin-btn"
							class:active={pinMode === 'start'}
							on:click={() => pinMode = pinMode === 'start' ? null : 'start'}
						>
							<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
								<circle cx="12" cy="10" r="3"/>
							</svg>
							{pinMode === 'start' ? 'Click the map to pin…' : 'Pin on map'}
						</button>

						{#if startAddress}
							<p class="address-confirmed">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<polyline points="20 6 9 17 4 12"/>
								</svg>
								{startAddress}
							</p>
						{/if}
					</div>
				</section>

				<!-- Destination -->
				<section class="section">
					<div class="section__head">
						<span class="section__dot section__dot--dest" />
						<h2>Destination</h2>
					</div>

					<div class="address-field">
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
								</svg>
							</span>
							<input
								type="text"
								placeholder="Search destination address…"
								bind:value={destQuery}
								on:input={() => searchAddress(destQuery, 'dest')}
								disabled={loading}
							/>
							{#if destSearching}
								<span class="searching-spinner" />
							{/if}
						</div>

						{#if destResults.length > 0}
							<ul class="results">
								{#each destResults as r}
									<li>
										<button type="button" on:click={() => pickResult(r, 'dest')}>
											<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
												<circle cx="12" cy="10" r="3"/>
											</svg>
											{r.display_name}
										</button>
									</li>
								{/each}
							</ul>
						{/if}

						<button
							type="button"
							class="pin-btn"
							class:active={pinMode === 'dest'}
							on:click={() => pinMode = pinMode === 'dest' ? null : 'dest'}
						>
							<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
								<circle cx="12" cy="10" r="3"/>
							</svg>
							{pinMode === 'dest' ? 'Click the map to pin…' : 'Pin on map'}
						</button>

						{#if destAddress}
							<p class="address-confirmed">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<polyline points="20 6 9 17 4 12"/>
								</svg>
								{destAddress}
							</p>
						{/if}
					</div>
				</section>

				<!-- Notes -->
				<section class="section">
					<div class="section__head">
						<span class="section__dot section__dot--notes" />
						<h2>Notes <span class="optional">required</span></h2>
					</div>
					<textarea
						placeholder="Any special instructions for the driver — mobility aids, preferred route, etc."
						bind:value={description}
						rows="3"
						disabled={loading}
					/>
				</section>

				{#if pinMode}
					<div class="map-hint">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="12" r="10"/>
							<line x1="12" y1="8" x2="12" y2="12"/>
							<line x1="12" y1="16" x2="12.01" y2="16"/>
						</svg>
						Click anywhere on the map to drop the {pinMode === 'start' ? 'pickup' : 'destination'} pin
					</div>
				{/if}

				<button
					class="btn-submit"
					on:click={handleSubmit}
					disabled={loading || !startAddress || !destAddress}
				>
					{#if loading}
						<span class="spinner" /> Submitting…
					{:else}
						Submit ride request
						<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
							<line x1="5" y1="12" x2="19" y2="12"/>
							<polyline points="12 5 19 12 12 19"/>
						</svg>
					{/if}
				</button>

			<!-- ══ OTHER FORM ═════════════════════════════════ -->
			{:else}
				<!-- Description -->
				<section class="section">
					<div class="section__head">
						<span class="section__dot section__dot--notes" />
						<h2>Description <span class="optional">required</span></h2>
					</div>
					<textarea
						placeholder="Describe what you need help with — errands, appointments, etc."
						bind:value={otherDescription}
						rows="3"
						disabled={loading}
					/>
				</section>

				<!-- Destination -->
				<section class="section">
					<div class="section__head">
						<span class="section__dot section__dot--dest" />
						<h2>Destination</h2>
					</div>

					<div class="address-field">
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
								</svg>
							</span>
							<input
								type="text"
								placeholder="Search destination address…"
								bind:value={otherDestQuery}
								on:input={() => searchOtherDest(otherDestQuery)}
								disabled={loading}
							/>
							{#if otherDestSearching}
								<span class="searching-spinner" />
							{/if}
						</div>

						{#if otherDestResults.length > 0}
							<ul class="results">
								{#each otherDestResults as r}
									<li>
										<button type="button" on:click={() => pickOtherDest(r)}>
											<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
												<circle cx="12" cy="10" r="3"/>
											</svg>
											{r.display_name}
										</button>
									</li>
								{/each}
							</ul>
						{/if}

						<button
							type="button"
							class="pin-btn"
							class:active={pinMode === 'dest'}
							on:click={() => pinMode = pinMode === 'dest' ? null : 'dest'}
						>
							<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
								<circle cx="12" cy="10" r="3"/>
							</svg>
							{pinMode === 'dest' ? 'Click the map to pin…' : 'Pin on map'}
						</button>

						{#if otherDestAddress}
							<p class="address-confirmed">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<polyline points="20 6 9 17 4 12"/>
								</svg>
								{otherDestAddress}
							</p>
						{/if}
					</div>
				</section>

				{#if pinMode}
					<div class="map-hint">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="12" r="10"/>
							<line x1="12" y1="8" x2="12" y2="12"/>
							<line x1="12" y1="16" x2="12.01" y2="16"/>
						</svg>
						Click anywhere on the map to drop the destination pin
					</div>
				{/if}

				<button
					class="btn-submit btn-submit--other"
					on:click={handleOtherSubmit}
					disabled={loading || !otherDestAddress}
				>
					{#if loading}
						<span class="spinner" /> Submitting…
					{:else}
						Submit request
						<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
							<line x1="5" y1="12" x2="19" y2="12"/>
							<polyline points="12 5 19 12 12 19"/>
						</svg>
					{/if}
				</button>
			{/if}
		</aside>

		<!-- Right: map -->
		<div class="map-col">
			<div class="map-container" class:cursor-crosshair={!!pinMode}>
				<div bind:this={mapEl} class="map" />
				{#if pinMode}
					<div class="map-overlay">
						<span class="map-overlay__label">
							{activeTab === 'ride' && pinMode === 'start' ? '📍 Click to set pickup' : '🏁 Click to set destination'}
						</span>
					</div>
				{/if}
			</div>

			<!-- Legend -->
			<div class="legend">
				{#if activeTab === 'ride'}
					<div class="legend__item">
						<span class="legend__dot legend__dot--start" />
						Pickup
					</div>
				{/if}
				<div class="legend__item">
					<span class="legend__dot legend__dot--dest" />
					Destination
				</div>
				{#if activeTab === 'ride'}
					<div class="legend__item legend__item--line">
						<span class="legend__line" />
						Route preview
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	/* ── Page shell ── */
	.page {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg);
	}

	/* ── Nav ── */
	.nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 2rem;
		border-bottom: 1px solid var(--border);
		background: var(--bg-card);
		position: sticky;
		top: 0;
		z-index: 100;
	}
	.nav__back {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
		transition: color 0.2s;
		width: 64px;
	}
	.nav__back:hover { color: var(--text-primary); }
	.nav__logo { display: flex; align-items: center; gap: 0.4rem; }
	.nav__mark { color: var(--accent); }
	.nav__name {
		font-family: var(--font-display);
		font-weight: 700; font-size: 1rem;
		letter-spacing: 0.08em; text-transform: uppercase;
	}

	/* ── Layout ── */
	.layout {
		flex: 1;
		display: grid;
		grid-template-columns: 420px 1fr;
		overflow: hidden;
	}
	@media (max-width: 900px) {
		.layout { grid-template-columns: 1fr; }
		.map-col { height: 380px; }
	}

	/* ── Form column ── */
	.form-col {
		padding: 2rem 1.75rem;
		overflow-y: auto;
		border-right: 1px solid var(--border);
		display: flex;
		flex-direction: column;
		gap: 1.75rem;
	}

	.form-header { display: flex; flex-direction: column; gap: 0.4rem; }
	.eyebrow {
		font-size: 0.75rem; text-transform: uppercase;
		letter-spacing: 0.1em; color: var(--accent); font-weight: 600;
	}
	.title {
		font-family: var(--font-display);
		font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em;
	}
	.subtitle { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.6; }

	/* ── Tabs ── */
	.tabs {
		display: flex;
		gap: 0;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 3px;
	}
	.tab {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.4rem;
		padding: 0.55rem 1rem;
		background: none;
		border: none;
		border-radius: calc(var(--radius-sm) - 2px);
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-family: var(--font-body);
		font-weight: 500;
		cursor: pointer;
		transition: background 0.18s, color 0.18s;
	}
	.tab:hover:not(.tab--active) {
		color: var(--text-primary);
		background: var(--bg-card);
	}
	.tab--active {
		background: var(--bg-card);
		color: var(--accent);
		box-shadow: 0 1px 4px rgba(0,0,0,0.25);
	}

	/* ── Sections ── */
	.section { display: flex; flex-direction: column; gap: 0.875rem; }
	.section__head {
		display: flex; align-items: center; gap: 0.625rem;
	}
	.section__head h2 {
		font-family: var(--font-display);
		font-size: 0.875rem; font-weight: 600;
		text-transform: uppercase; letter-spacing: 0.06em;
		color: var(--text-secondary);
		display: flex; align-items: center; gap: 0.5rem;
	}
	.optional {
		font-size: 0.7rem; background: var(--bg-elevated);
		border: 1px solid var(--border); border-radius: 4px;
		padding: 1px 5px; color: var(--text-muted);
		text-transform: none; letter-spacing: 0;
	}
	.section__dot {
		width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
	}
	.section__dot--start { background: var(--accent); }
	.section__dot--dest  { background: var(--danger); }
	.section__dot--notes { background: var(--text-muted); }

	/* ── Address field ── */
	.address-field { display: flex; flex-direction: column; gap: 0.625rem; }

	.input-wrap { position: relative; display: flex; align-items: center; }
	.icon {
		position: absolute; left: 0.875rem;
		color: var(--text-muted); pointer-events: none;
		display: flex; align-items: center; transition: color 0.2s;
	}
	.input-wrap:focus-within .icon { color: var(--accent); }
	.input-wrap input {
		width: 100%;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 0.75rem 2.5rem 0.75rem 2.6rem;
		color: var(--text-primary);
		font-size: 0.9rem;
		outline: none;
		transition: border-color 0.2s, box-shadow 0.2s;
		-webkit-appearance: none;
	}
	.input-wrap input::placeholder { color: var(--text-muted); }
	.input-wrap input:focus {
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-dim);
	}
	.input-wrap input:disabled { opacity: 0.5; cursor: not-allowed; }

	.searching-spinner {
		position: absolute; right: 0.875rem;
		width: 14px; height: 14px;
		border: 2px solid var(--border); border-top-color: var(--accent);
		border-radius: 50%; animation: spin 0.6s linear infinite;
	}

	/* ── Results dropdown ── */
	.results {
		list-style: none;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		overflow: hidden;
		max-height: 220px;
		overflow-y: auto;
	}
	.results li button {
		width: 100%;
		display: flex; align-items: flex-start; gap: 0.625rem;
		padding: 0.625rem 0.875rem;
		background: none; border: none;
		color: var(--text-secondary);
		font-size: 0.8125rem; font-family: var(--font-body);
		text-align: left; cursor: pointer;
		transition: background 0.15s, color 0.15s;
		line-height: 1.4;
	}
	.results li button svg { flex-shrink: 0; margin-top: 2px; color: var(--text-muted); }
	.results li button:hover { background: var(--bg-card); color: var(--text-primary); }
	.results li + li { border-top: 1px solid var(--border); }

	/* ── Pin button ── */
	.pin-btn {
		display: inline-flex; align-items: center; gap: 0.45rem;
		padding: 0.5rem 0.875rem;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		color: var(--text-secondary);
		font-size: 0.8125rem; font-family: var(--font-body);
		cursor: pointer; align-self: flex-start;
		transition: border-color 0.2s, color 0.2s, background 0.2s;
	}
	.pin-btn:hover { border-color: var(--border-hover); color: var(--text-primary); }
	.pin-btn.active {
		border-color: var(--accent);
		background: var(--accent-dim);
		color: var(--accent);
	}

	/* ── Confirmed address ── */
	.address-confirmed {
		display: flex; align-items: center; gap: 0.4rem;
		font-size: 0.8rem; color: var(--success);
	}

	/* ── Textarea ── */
	textarea {
		width: 100%;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 0.75rem 0.875rem;
		color: var(--text-primary);
		font-size: 0.9rem; font-family: var(--font-body);
		resize: vertical; outline: none;
		transition: border-color 0.2s, box-shadow 0.2s;
		-webkit-appearance: none;
		min-height: 80px;
	}
	textarea::placeholder { color: var(--text-muted); }
	textarea:focus {
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-dim);
	}
	textarea:disabled { opacity: 0.5; cursor: not-allowed; }

	/* ── Map hint ── */
	.map-hint {
		display: flex; align-items: center; gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: var(--accent-dim);
		border: 1px solid rgba(232,255,71,0.2);
		border-radius: var(--radius-sm);
		font-size: 0.8125rem; color: var(--accent);
	}

	/* ── Submit ── */
	.btn-submit {
		display: flex; align-items: center; justify-content: center; gap: 0.5rem;
		width: 100%; padding: 0.9rem;
		background: var(--accent); color: #080a0f;
		font-family: var(--font-display); font-size: 0.9375rem;
		font-weight: 700; letter-spacing: 0.02em;
		border: none; border-radius: var(--radius-sm); cursor: pointer;
		transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
	}
	.btn-submit:hover:not(:disabled) {
		background: var(--accent-hover); transform: translateY(-1px);
		box-shadow: 0 4px 20px rgba(232,255,71,0.25);
	}
	.btn-submit:active:not(:disabled) { transform: translateY(0); }
	.btn-submit:disabled { opacity: 0.45; cursor: not-allowed; }

	/* Other tab submit uses a muted variant */
	.btn-submit--other {
		background: var(--bg-elevated);
		color: var(--text-primary);
		border: 1px solid var(--border);
	}
	.btn-submit--other:hover:not(:disabled) {
		background: var(--bg-card);
		border-color: var(--accent);
		color: var(--accent);
		box-shadow: 0 4px 20px rgba(232,255,71,0.1);
	}

	.spinner {
		width: 15px; height: 15px;
		border: 2px solid rgba(8,10,15,0.3); border-top-color: #080a0f;
		border-radius: 50%; animation: spin 0.6s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	/* ── Map column ── */
	.map-col {
		display: flex;
		flex-direction: column;
		position: relative;
	}
	.map-container {
		flex: 1;
		position: relative;
	}
	.map-container.cursor-crosshair :global(.leaflet-container) {
		cursor: crosshair !important;
	}
	.map {
		width: 100%;
		height: 100%;
		min-height: 500px;
	}
	/* Dark-ish map tint */
	:global(.leaflet-tile) { filter: brightness(0.85) saturate(0.8); }
	:global(.leaflet-container) { background: var(--bg); }
	:global(.leaflet-control-zoom a) {
		background: var(--bg-card) !important;
		color: var(--text-primary) !important;
		border-color: var(--border) !important;
	}

	.map-overlay {
		position: absolute; top: 1rem; left: 50%;
		transform: translateX(-50%);
		z-index: 500; pointer-events: none;
	}
	.map-overlay__label {
		background: var(--bg-card);
		border: 1px solid var(--accent);
		border-radius: 20px;
		padding: 0.4rem 1rem;
		font-size: 0.8125rem; color: var(--accent);
		white-space: nowrap;
		box-shadow: 0 4px 16px rgba(0,0,0,0.4);
	}

	.legend {
		display: flex; gap: 1.5rem;
		padding: 0.75rem 1.25rem;
		background: var(--bg-card);
		border-top: 1px solid var(--border);
	}
	.legend__item {
		display: flex; align-items: center; gap: 0.4rem;
		font-size: 0.775rem; color: var(--text-secondary);
	}
	.legend__dot {
		width: 10px; height: 10px; border-radius: 50%;
	}
	.legend__dot--start { background: var(--accent); }
	.legend__dot--dest  { background: var(--danger); }
	.legend__line {
		width: 20px; height: 2px;
		background: repeating-linear-gradient(
			to right, var(--accent) 0, var(--accent) 4px, transparent 4px, transparent 8px
		);
	}
</style>