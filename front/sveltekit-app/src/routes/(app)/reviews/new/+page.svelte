<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { reviewsApi, driveRequestsApi } from '$lib/api/entities';
	import { notifications } from '$lib/stores/notifications';
	import { onMount } from 'svelte';

	const user = auth.user;

	// Drivers the user has completed at least one ride with
	type EligibleDriver = {
		id: number;
		name: string;
		existingReview: { id: number; rating: number; comment: string } | null;
	};

	let eligibleDrivers: EligibleDriver[] = [];
	let loading = true;

	// Selected driver / form state
	let selectedDriver: EligibleDriver | null = null;
	let rating = 0;
	let hovered = 0;
	let comment = '';
	let submitting = false;

	onMount(() => {
		const unsubAuth = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});

		const unsubUser = user.subscribe(async (u) => {
			if (!u) return;
			if (u.role !== 'disabled') {
				goto('/dashboard');
				return;
			}
			await loadEligibleDrivers(u.id);
		});

		return () => {
			unsubAuth();
			unsubUser();
		};
	});

	async function loadEligibleDrivers(userId: number) {
		loading = true;
		try {
			// Fetch all completed rides for this user
			const all = await driveRequestsApi.list();
			const completed = all.filter(
				(r: any) =>
					r.disabled_rel?.id === userId &&
					r.is_completed &&
					(r.driver_rel?.id ?? r.driver)
			);

			// Deduplicate by driver id — driver_rel is the nested object when loaded,
			// but fall back to the integer driver field + myReviews for the name
			const driverMap = new Map<number, EligibleDriver>();
			for (const ride of completed) {
				const driverId: number = ride.driver_rel?.id ?? ride.driver;
				const driverName: string = ride.driver_rel?.name ?? `Driver #${driverId}`;
				if (driverId && !driverMap.has(driverId)) {
					driverMap.set(driverId, { id: driverId, name: driverName, existingReview: null });
				}
			}

			// Load existing reviews by this user to pre-fill + resolve driver names
			const myReviews: any[] = await reviewsApi.myReviews();
			for (const review of myReviews) {
				if (driverMap.has(review.driver)) {
					const entry = driverMap.get(review.driver)!;
					// Use driver_name from review as fallback if we didn't get it from the ride
					if (entry.name.startsWith('Driver #') && review.driver_name) {
						entry.name = review.driver_name;
					}
					entry.existingReview = {
						id: review.id,
						rating: review.rating,
						comment: review.comment ?? ''
					};
				}
			}

			eligibleDrivers = Array.from(driverMap.values());
		} catch (e) {
			console.error('Failed to load eligible drivers:', e);
			notifications.error('Could not load your ride history.');
		} finally {
			loading = false;
		}
	}

	function selectDriver(driver: EligibleDriver) {
		selectedDriver = driver;
		// Pre-fill if they already reviewed this driver
		if (driver.existingReview) {
			rating = driver.existingReview.rating;
			comment = driver.existingReview.comment;
		} else {
			rating = 0;
			comment = '';
		}
		hovered = 0;
	}

	function back() {
		selectedDriver = null;
		rating = 0;
		hovered = 0;
		comment = '';
	}

	async function submit() {
		if (!selectedDriver || rating === 0) return;
		submitting = true;
		try {
			await reviewsApi.create({
				driver: selectedDriver.id,
				author: $user!.id,
				rating,
				comment: comment.trim() || null
			});

			notifications.success(
				selectedDriver.existingReview
					? 'Review updated successfully!'
					: 'Review submitted successfully!'
			);

			// Refresh so card shows updated state
			await loadEligibleDrivers($user!.id);
			back();
		} catch (e: any) {
			notifications.error(e?.message ?? 'Failed to submit review.');
		} finally {
			submitting = false;
		}
	}

	function starLabel(n: number) {
		return ['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent'][n] ?? '';
	}
</script>

<svelte:head><title>Leave a Review — Accessride</title></svelte:head>

<div class="shell">
	<nav class="nav">
		<div class="nav__logo">
			<span class="nav__mark">▲</span>
			<span class="nav__name">Accessride</span>
		</div>
		<button class="nav__back" on:click={() => goto('/dashboard')}>← Dashboard</button>
	</nav>

	<main class="main">
		<h1>Leave a Review</h1>
		<p class="subtitle">Rate the helpers you've completed rides with.</p>

		{#if loading}
			<p class="status-msg">Loading your ride history…</p>

		{:else if eligibleDrivers.length === 0}
			<div class="empty-state">
				<span class="empty-icon">🙁</span>
				<p>You don't have any completed requests yet.</p>
				<a href="/requests/new" class="btn-primary">Request help</a>
			</div>

		{:else if !selectedDriver}
			<!-- Driver selection list -->
			<div class="drivers-list">
				{#each eligibleDrivers as driver}
					<button class="driver-card" on:click={() => selectDriver(driver)}>
						<div class="driver-card__left">
							<span class="avatar">{driver.name.charAt(0).toUpperCase()}</span>
							<div class="driver-card__info">
								<span class="driver-card__name">{driver.name}</span>
								{#if driver.existingReview}
									<span class="badge badge-reviewed">
										{'★'.repeat(driver.existingReview.rating)} Reviewed
									</span>
								{:else}
									<span class="badge badge-pending">⏳ Not yet reviewed</span>
								{/if}
							</div>
						</div>
						<svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none"
							stroke="currentColor" stroke-width="2">
							<line x1="5" y1="12" x2="19" y2="12"/>
							<polyline points="12 5 19 12 12 19"/>
						</svg>
					</button>
				{/each}
			</div>

		{:else}
			<!-- Review form -->
			<div class="form-card">
				<header class="form-header">
					<button class="back-link" on:click={back}>← All helpers</button>
					<div class="form-driver-info">
						<span class="avatar avatar-lg">{selectedDriver.name.charAt(0).toUpperCase()}</span>
						<div>
							<span class="driver-card__name">{selectedDriver.name}</span>
							{#if selectedDriver.existingReview}
								<span class="edit-hint">Submitting will update your existing review.</span>
							{/if}
						</div>
					</div>
				</header>

				<!-- Star picker -->
				<div class="stars-section">
					<span class="field-label">Your rating</span>
					<div class="stars" role="group" aria-label="Star rating">
						{#each [1, 2, 3, 4, 5] as n}
							<button
								class="star"
								class:active={n <= (hovered || rating)}
								on:mouseenter={() => (hovered = n)}
								on:mouseleave={() => (hovered = 0)}
								on:click={() => (rating = n)}
								aria-label="{n} star{n > 1 ? 's' : ''}"
							>★</button>
						{/each}
					</div>
					{#if hovered || rating}
						<span class="star-label">{starLabel(hovered || rating)}</span>
					{/if}
				</div>

				<!-- Comment -->
				<div class="field">
					<label class="field-label" for="comment">Comment <span class="optional">(optional)</span></label>
					<textarea
						id="comment"
						class="textarea"
						rows="4"
						placeholder="Describe your experience…"
						bind:value={comment}
					></textarea>
				</div>

				<button
					class="btn-primary submit-btn"
					disabled={rating === 0 || submitting}
					on:click={submit}
				>
					{#if submitting}
						Submitting…
					{:else if selectedDriver.existingReview}
						Update Review
					{:else}
						Submit Review
					{/if}
				</button>
			</div>
		{/if}
	</main>
</div>

<style>
	.shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg-body); }

	.nav { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; border-bottom: 1px solid var(--border); background: var(--bg-card); }
	.nav__logo { display: flex; align-items: center; gap: 0.5rem; }
	.nav__mark { color: var(--accent); }
	.nav__name { font-family: var(--font-display); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
	.nav__back { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; }
	.nav__back:hover { border-color: var(--border-hover); }

	.main { flex: 1; padding: 3rem 2rem; display: flex; flex-direction: column; gap: 1.5rem; max-width: 720px; margin: 0 auto; width: 100%; }
	h1 { font-family: var(--font-display); font-size: 2rem; font-weight: 700; }
	.subtitle { color: var(--text-secondary); margin-top: -0.75rem; }
	.status-msg { color: var(--text-secondary); }

	/* Empty state */
	.empty-state { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 4rem 2rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); text-align: center; color: var(--text-secondary); }
	.empty-icon { font-size: 2.5rem; }

	/* Driver list */
	.drivers-list { display: flex; flex-direction: column; gap: 0.75rem; }
	.driver-card { display: flex; align-items: center; justify-content: space-between; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.5rem; cursor: pointer; text-align: left; color: inherit; transition: transform 0.15s, border-color 0.15s; }
	.driver-card:hover { transform: translateY(-2px); border-color: var(--border-hover); }
	.driver-card__left { display: flex; align-items: center; gap: 1rem; }
	.driver-card__info { display: flex; flex-direction: column; gap: 0.35rem; }
	.driver-card__name { font-weight: 700; font-size: 1rem; }
	.chevron { color: var(--text-secondary); flex-shrink: 0; }

	/* Avatar */
	.avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; background: var(--accent); color: rgb(0, 0, 0); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; flex-shrink: 0; }
	.avatar-lg { width: 3rem; height: 3rem; font-size: 1.25rem; }

	/* Badges */
	.badge { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
	.badge-reviewed { background: #d1fae5; color: #065f46; }
	.badge-pending { background: #fef3c7; color: #92400e; }

	/* Form card */
	.form-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem; display: flex; flex-direction: column; gap: 1.75rem; }
	.form-header { display: flex; flex-direction: column; gap: 1rem; }
	.back-link { background: none; border: none; color: var(--text-secondary); cursor: pointer; text-align: left; padding: 0; font-size: 0.875rem; }
	.back-link:hover { color: var(--text-primary); }
	.form-driver-info { display: flex; align-items: center; gap: 1rem; }
	.edit-hint { font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem; display: block; }

	/* Stars */
	.stars-section { display: flex; flex-direction: column; gap: 0.5rem; }
	.stars { display: flex; gap: 0.25rem; }
	.star { background: none; border: none; font-size: 2.25rem; cursor: pointer; color: var(--border); line-height: 1; padding: 0; transition: color 0.1s, transform 0.1s; }
	.star.active { color: #f59e0b; }
	.star:hover { transform: scale(1.15); }
	.star-label { font-size: 0.875rem; color: var(--text-secondary); font-weight: 600; height: 1.25rem; }

	/* Field */
	.field { display: flex; flex-direction: column; gap: 0.5rem; }
	.field-label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; letter-spacing: 0.05em; }
	.optional { text-transform: none; font-weight: 400; }
	.textarea { background: var(--bg-body); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.75rem 1rem; color: var(--text-primary); font-size: 0.95rem; font-family: inherit; resize: vertical; transition: border-color 0.15s; }
	.textarea:focus { outline: none; border-color: var(--accent); }

	/* Submit */
	.submit-btn { width: 100%; padding: 0.75rem; font-size: 1rem; }
	.btn-primary { background: var(--accent); color: rgb(0, 0, 0); border: none; padding: 0.5rem 1.25rem; border-radius: var(--radius-sm); font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
	.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
	.btn-primary:not(:disabled):hover { opacity: 0.88; }
</style>