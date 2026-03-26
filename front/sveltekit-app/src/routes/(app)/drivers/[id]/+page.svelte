<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth';
	import { reviewsApi } from '$lib/api/entities';
	import { onMount } from 'svelte';

	const user = auth.user;

	let stats: any = null;
	let loading = true;
	let error = false;

	$: driverId = Number($page.params.id);

	onMount(() => {
		const unsub = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});
		loadStats();
		return unsub;
	});

	async function loadStats() {
		loading = true;
		error = false;
		try {
			stats = await reviewsApi.driverStats(driverId);
		} catch (e) {
			console.error(e);
			error = true;
		} finally {
			loading = false;
		}
	}

	function stars(rating: number) {
		const full = Math.round(rating);
		return '★'.repeat(full) + '☆'.repeat(5 - full);
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleDateString('en-GB', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>{stats?.driver_name ?? 'Driver'} — Fleet</title>
</svelte:head>

<div class="shell">
	<nav class="nav">
		<div class="nav__logo">
			<span class="nav__mark">▲</span>
			<span class="nav__name">Fleet</span>
		</div>
		<button class="nav__back" on:click={() => history.back()}>← Back</button>
	</nav>

	<main class="main">
		{#if loading}
			<p class="status-msg">Loading driver profile…</p>

		{:else if error}
			<p class="status-msg">Could not load this driver's profile.</p>

		{:else if stats}
			<!-- Header -->
			<div class="profile-header">
				<div class="profile-avatar">{stats.driver_name.charAt(0).toUpperCase()}</div>
				<div class="profile-info">
					<h1>{stats.driver_name}</h1>
					<div class="rating-row">
						<span class="stars-display">{stars(stats.average_rating)}</span>
						<span class="rating-num">{stats.average_rating.toFixed(1)}</span>
						<span class="review-count">({stats.total_reviews} review{stats.total_reviews !== 1 ? 's' : ''})</span>
					</div>
				</div>
			</div>

			<!-- Group ratings -->
			{#if Object.keys(stats.group_ratings).length > 0}
				<section class="section">
					<h2 class="section-title">Ratings by disability group</h2>
					<div class="group-grid">
						{#each Object.entries(stats.group_ratings) as [group, avg]}
							<div class="group-card">
								<span class="group-name">{group}</span>
								<span class="group-stars">{stars(Number(avg))}</span>
								<span class="group-avg">{Number(avg).toFixed(1)}</span>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Reviews list -->
			<section class="section">
				<h2 class="section-title">Recent reviews</h2>
				{#if stats.recent_reviews.length === 0}
					<p class="status-msg">No reviews yet.</p>
				{:else}
					<div class="reviews-list">
						{#each stats.recent_reviews as review}
							<div class="review-card">
								<div class="review-header">
									<span class="review-stars">{stars(review.rating)}</span>
									<span class="review-date">{formatDate(review.created_at)}</span>
								</div>
								{#if review.comment}
									<p class="review-comment">"{review.comment}"</p>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</section>

			<!-- CTA for disabled users -->
			{#if $user?.role === 'disabled'}
				<a href="/reviews/new" class="btn-primary cta-btn">Leave a review</a>
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
	.nav__back { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; }
	.nav__back:hover { border-color: var(--border-hover); }

	.main { flex: 1; padding: 3rem 2rem; display: flex; flex-direction: column; gap: 2rem; max-width: 800px; margin: 0 auto; width: 100%; }
	.status-msg { color: var(--text-secondary); }

	/* Profile header */
	.profile-header { display: flex; align-items: center; gap: 1.5rem; }
	.profile-avatar { width: 4.5rem; height: 4.5rem; border-radius: 50%; background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; font-weight: 800; flex-shrink: 0; box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
	.profile-info { display: flex; flex-direction: column; gap: 0.4rem; }
	h1 { font-family: var(--font-display); font-size: 1.75rem; font-weight: 700; margin: 0; }
	.rating-row { display: flex; align-items: center; gap: 0.5rem; }
	.stars-display { color: #f59e0b; font-size: 1.2rem; letter-spacing: 0.05em; }
	.rating-num { font-weight: 700; font-size: 1.1rem; }
	.review-count { color: var(--text-secondary); font-size: 0.9rem; }

	/* Sections */
	.section { display: flex; flex-direction: column; gap: 1rem; }
	.section-title { font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.8rem; }

	/* Group ratings */
	.group-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem; }
	.group-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.25rem; }
	.group-name { font-size: 0.8rem; color: var(--text-secondary); font-weight: 600; text-transform: capitalize; }
	.group-stars { color: #f59e0b; font-size: 1rem; letter-spacing: 0.05em; }
	.group-avg { font-weight: 700; font-size: 1rem; }

	/* Reviews */
	.reviews-list { display: flex; flex-direction: column; gap: 0.75rem; }
	.review-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.6rem; }
	.review-header { display: flex; align-items: center; justify-content: space-between; }
	.review-stars { color: #f59e0b; font-size: 1.1rem; letter-spacing: 0.05em; }
	.review-date { font-size: 0.8rem; color: var(--text-secondary); }
	.review-comment { font-style: italic; color: var(--text-secondary); background: var(--bg-body); padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.9rem; margin: 0; }

	/* CTA */
	.cta-btn { align-self: flex-start; text-decoration: none; padding: 0.65rem 1.5rem; font-size: 0.95rem; }
	.btn-primary { background: var(--accent); color: #fff; border: none; padding: 0.5rem 1.25rem; border-radius: var(--radius-sm); font-weight: 600; cursor: pointer; }
</style>