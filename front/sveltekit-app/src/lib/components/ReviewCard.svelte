<script lang="ts">
	import type { Review, Driver } from '$lib/api/entities';

	export let review: Review;
	export let driver: Driver;

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function renderStars(rating: number) {
		return '★'.repeat(rating) + '☆'.repeat(5 - rating);
	}
</script>

<div class="review-item">
	<div class="review-header">
		<div>
			<h4>{driver.name}</h4>
			<span class="date">{formatDate(review.created_at)}</span>
		</div>
		<div class="stars-display">{renderStars(review.rating)}</div>
	</div>

	{#if review.comment}
		<p class="comment">{review.comment}</p>
	{/if}
</div>

<style>
	.review-item {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 16px;
		margin-bottom: 12px;
	}

	.review-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 12px;
	}

	.review-header h4 {
		font-size: 15px;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 4px;
	}

	.date {
		font-size: 12px;
		color: var(--text-muted);
	}

	.stars-display {
		color: var(--accent);
		font-size: 14px;
		letter-spacing: 2px;
	}

	.comment {
		font-size: 14px;
		color: var(--text-secondary);
		line-height: 1.5;
		margin: 0;
	}
</style>
