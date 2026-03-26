<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { notifications } from '$lib/stores/notifications';
	import { driveRequestsApi, reviewsApi, driversApi } from '$lib/api/entities';
import type { DriveRequest, Driver, Review } from '$lib/api/entities';
	import { onMount } from 'svelte';
	import ReviewForm from '$lib/components/ReviewForm.svelte';
	import ReviewCard from '$lib/components/ReviewCard.svelte';

	const user = auth.user;

	let completedRequests: DriveRequest[] = [];
	let selectedRequest: DriveRequest | null = null;
	let selectedDriver: Driver | null = null;
	let existingReviews: any[] = [];
let currentReview: Review | null = null;
	let loading = false;
	let driverId: number | null = null;
let preselectedRequestId: number | null = null;

	onMount(() => {
		const params = new URLSearchParams(window.location.search);
		const requestIdParam = Number(params.get('requestId'));
		preselectedRequestId = Number.isFinite(requestIdParam) && requestIdParam > 0 ? requestIdParam : null;

		const unsubAuth = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});

		const unsubUser = user.subscribe((u) => {
			if (u?.role === 'disabled') {
				fetchCompletedRequests();
			}
		});

		return () => {
			unsubAuth();
			unsubUser();
		};
	});

	async function fetchCompletedRequests() {
		loading = true;
		try {
			const allRequests = await driveRequestsApi.list();
			// Filter for completed requests by the current user
			completedRequests = allRequests.filter(
				(r) => r.is_completed && r.disabled_rel?.id === $user?.id
			);
			if (preselectedRequestId) {
				const preferred = completedRequests.find((r) => r.id === preselectedRequestId);
				if (preferred) {
					preselectedRequestId = null;
					await selectRequest(preferred);
				}
			}
		} catch (error) {
			console.error('Failed to fetch requests:', error);
			notifications.error('Failed to load your requests.');
		} finally {
			loading = false;
		}
	}

	async function selectRequest(request: DriveRequest) {
		selectedRequest = request;
		driverId = request.driver;

		if (!driverId) {
			notifications.error('No driver assigned to this request');
			return;
		}

		try {
			// Fetch driver details
			selectedDriver = await driversApi.get(driverId);

			// Fetch existing reviews for this driver by this user
			const allReviews = await reviewsApi.list();
			existingReviews = allReviews.filter(
				(r) => r.driver === driverId && r.author === $user?.id
			);
			currentReview = existingReviews.length > 0 ? (existingReviews[0] as Review) : null;
		} catch (error) {
			console.error('Failed to fetch driver info:', error);
			notifications.error('Failed to load driver information.');
		}
	}

	function back() {
		selectedRequest = null;
		selectedDriver = null;
		existingReviews = [];
	currentReview = null;
	}

	function handleReviewSuccess() {
		notifications.success('Review submitted!');
		setTimeout(() => {
			fetchCompletedRequests();
			back();
		}, 1500);
	}

	function logout() {
		auth.logout();
		goto('/login');
	}
</script>

<svelte:head><title>Write a Review — Fleet</title></svelte:head>

<div class="shell">
	<nav class="nav">
		<div class="nav__logo">
			<span class="nav__mark">▲</span>
			<span class="nav__name">Fleet</span>
		</div>
		<button class="nav__logout" on:click={logout}>Sign out</button>
	</nav>

	<main class="main">
		{#if !selectedRequest}
			<div class="header">
				<div>
					<h1>Write a Review</h1>
					<p>Share your experience with your helper</p>
				</div>
				<a href="/dashboard" class="back-link">← Back to Dashboard</a>
			</div>

			{#if loading}
				<p class="status-msg">Loading your requests...</p>
			{:else if completedRequests.length === 0}
				<div class="empty-state">
					<p>No completed requests yet.</p>
					<a href="/dashboard" class="btn-primary">Request a service</a>
				</div>
			{:else}
				<div class="requests-list">
					<h2>Select a request to review</h2>
					{#each completedRequests as request (request.id)}
						<div class="request-item" on:click={() => selectRequest(request)}>
							<div class="request-info">
								<h3>Request #{request.id}</h3>
								<p class="description">{request.description}</p>
								<div class="locations">
									<span>📍 {request.start_address}</span>
									<span>→</span>
									<span>📍 {request.dest_address}</span>
								</div>
							</div>
							<svg
								width="20"
								height="20"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<polyline points="9 18 15 12 9 6" />
							</svg>
						</div>
					{/each}
				</div>
			{/if}
		{:else if selectedDriver}
			<div class="review-section">
				<button class="back-btn" on:click={back}>← Back</button>

				<div class="review-container">
					{#if currentReview}
						<div class="existing-reviews">
							<h2>Your current review for {selectedDriver.name}</h2>
							<ReviewCard review={currentReview} driver={selectedDriver} />
						</div>
					{/if}
					<ReviewForm
						driver={selectedDriver}
						authorId={$user?.id || 0}
						existingReview={currentReview}
						onSuccess={handleReviewSuccess}
					/>
				</div>
			</div>
		{/if}
	</main>
</div>

<style>
	.shell {
		display: flex;
		min-height: 100vh;
		background: var(--bg);
	}

	.nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 64px;
		background: var(--bg-card);
		border-bottom: 1px solid var(--border);
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 24px;
		z-index: 100;
	}

	.nav__logo {
		display: flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-display);
		font-size: 18px;
		font-weight: 700;
	}

	.nav__mark {
		color: var(--accent);
	}

	.nav__logout {
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		font-size: 14px;
		transition: color var(--transition);

		&:hover {
			color: var(--text-primary);
		}
	}

	.main {
		flex: 1;
		margin-top: 64px;
		padding: 40px 24px;
		max-width: 900px;
		margin-left: auto;
		margin-right: auto;
		width: 100%;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 40px;
	}

	.header h1 {
		font-family: var(--font-display);
		font-size: 32px;
		font-weight: 700;
		margin-bottom: 8px;
	}

	.header p {
		color: var(--text-secondary);
		font-size: 15px;
	}

	.back-link {
		color: var(--accent);
		font-size: 14px;
		transition: color var(--transition);

		&:hover {
			color: var(--accent-hover);
		}
	}

	.status-msg,
	.empty-state p {
		color: var(--text-secondary);
		text-align: center;
		padding: 40px;
	}

	.empty-state {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 60px 24px;
		text-align: center;
	}

	.btn-primary {
		display: inline-block;
		margin-top: 16px;
		padding: 10px 20px;
		background: var(--accent);
		color: var(--bg);
		border-radius: var(--radius-sm);
		font-weight: 600;
		font-size: 14px;
		transition: all var(--transition);

		&:hover {
			background: var(--accent-hover);
			transform: translateY(-2px);
		}
	}

	.requests-list {
		margin-top: 32px;
	}

	.requests-list h2 {
		font-family: var(--font-display);
		font-size: 18px;
		font-weight: 600;
		margin-bottom: 16px;
		color: var(--text-primary);
	}

	.request-item {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 16px;
		margin-bottom: 12px;
		cursor: pointer;
		display: flex;
		justify-content: space-between;
		align-items: center;
		transition: all var(--transition);

		&:hover {
			border-color: var(--accent);
			background: var(--bg-elevated);
		}
	}

	.request-info {
		flex: 1;
	}

	.request-item h3 {
		font-size: 15px;
		font-weight: 600;
		margin-bottom: 4px;
	}

	.description {
		font-size: 14px;
		color: var(--text-secondary);
		margin-bottom: 8px;
	}

	.locations {
		display: flex;
		gap: 8px;
		font-size: 13px;
		color: var(--text-muted);
		flex-wrap: wrap;
	}

	.review-section {
		padding: 24px;
	}

	.back-btn {
		background: transparent;
		border: none;
		color: var(--accent);
		cursor: pointer;
		font-size: 14px;
		margin-bottom: 24px;
		transition: color var(--transition);

		&:hover {
			color: var(--accent-hover);
		}
	}

	.review-container {
		max-width: 600px;
	}

	.existing-reviews h2 {
		font-family: var(--font-display);
		font-size: 18px;
		font-weight: 600;
		margin-bottom: 16px;
		color: var(--text-primary);
	}

	@media (max-width: 640px) {
		.nav {
			padding: 0 16px;
		}

		.main {
			padding: 24px 16px;
		}

		.header {
			flex-direction: column;
			gap: 16px;
		}

		.header h1 {
			font-size: 24px;
		}

		.locations {
			gap: 4px;
		}
	}
</style>
