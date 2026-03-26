<script lang="ts">
	import { reviewsApi } from '$lib/api/entities';

	export let driverId: number;
	export let compact: boolean = true;

	interface Stats {
		average_rating: number;
		total_reviews: number;
	}

	let stats: Stats | null = null;
	let loading = true;

	const fetchStats = async () => {
		loading = true;
		try {
			const data = await reviewsApi.getDriverStats(driverId, 0);
			stats = {
				average_rating: data.average_rating,
				total_reviews: data.total_reviews
			};
		} catch {
			// Silent fail: rating is non-critical UI.
			stats = null;
		} finally {
			loading = false;
		}
	};

	$: if (driverId) {
		fetchStats();
	}

	const getStarArray = (rating: number) => {
		return Array.from({ length: 5 }, (_, i) => i < Math.round(rating));
	};
</script>

{#if !loading && stats && stats.total_reviews > 0}
	<div class="helper-rating" class:compact>
		<div class="stars">
			{#each getStarArray(stats.average_rating) as filled}
				<svg class="star" class:filled viewBox="0 0 24 24" aria-hidden="true">
					<path
						d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
					/>
				</svg>
			{/each}
		</div>
		{#if !compact}
			<span class="rating-text">
				{stats.average_rating.toFixed(1)} ({stats.total_reviews}
				{stats.total_reviews === 1 ? 'review' : 'reviews'})
			</span>
		{:else}
			<span class="rating-text">{stats.average_rating.toFixed(1)}</span>
		{/if}
	</div>
{:else if !loading && stats && stats.total_reviews === 0}
	<div class="helper-rating no-reviews">
		<span class="no-reviews-text">New Helper</span>
	</div>
{/if}

<style>
	.helper-rating {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.helper-rating.compact {
		gap: 0.35rem;
	}

	.stars {
		display: flex;
		gap: 0.15rem;
	}

	.star {
		width: 16px;
		height: 16px;
		fill: #ddd;
	}

	.compact .star {
		width: 14px;
		height: 14px;
	}

	.star.filled {
		fill: #fbbf24;
	}

	.rating-text {
		font-size: 0.85rem;
		color: #666;
		font-weight: 500;
	}

	.compact .rating-text {
		font-size: 0.8rem;
	}

	.no-reviews {
		padding: 0.25rem 0.5rem;
		background-color: #f3f4f6;
		border-radius: 4px;
	}

	.no-reviews-text {
		font-size: 0.8rem;
		color: #6b7280;
		font-style: italic;
	}
</style>
