<script lang="ts">
	import { notifications } from '$lib/stores/notifications';
	import { reviewsApi } from '$lib/api/entities';
	import type { Driver } from '$lib/api/entities';

	export let driver: Driver;
	export let authorId: number;
	export let onSuccess: (() => void) | undefined = undefined;

	let rating = 5;
	let comment = '';
	let loading = false;

	async function handleSubmit() {
		if (!driver?.id) {
			notifications.error('Driver information missing');
			return;
		}

		loading = true;
		try {
			await reviewsApi.create({
				rating,
				comment: comment || undefined,
				driver: driver.id,
				author: authorId
			});
			notifications.success('Review submitted successfully!');
			rating = 5;
			comment = '';
			onSuccess?.();
		} catch (error: any) {
			if (error.detail) {
				notifications.error(error.detail);
			} else {
				notifications.error('Failed to submit review. Please try again.');
			}
		} finally {
			loading = false;
		}
	}
</script>

<div class="review-card">
	<div class="review-header">
		<h3>Rate your experience</h3>
		<p class="helper-name">{driver.name}</p>
	</div>

	<form on:submit|preventDefault={handleSubmit}>
		<div class="rating-section">
			<label>Rating</label>
			<div class="stars">
				{#each [1, 2, 3, 4, 5] as star}
					<button
						type="button"
						class="star"
						class:active={star <= rating}
						on:click={() => (rating = star)}
						aria-label="Rate {star} stars"
					>
						★
					</button>
				{/each}
			</div>
			<span class="rating-text">{rating} out of 5 stars</span>
		</div>

		<div class="input-wrap">
			<label for="comment">Comment (optional)</label>
			<textarea
				id="comment"
				bind:value={comment}
				placeholder="Share your experience..."
				rows="4"
				disabled={loading}
				maxlength="500"
			/>
			<span class="char-count">{comment.length}/500</span>
		</div>

		<button type="submit" class="submit-btn" disabled={loading}>
			{loading ? 'Submitting...' : 'Submit Review'}
		</button>
	</form>
</div>

<style>
	.review-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 24px;
		max-width: 500px;
	}

	.review-header {
		margin-bottom: 24px;
	}

	.review-header h3 {
		font-family: var(--font-display);
		font-size: 20px;
		font-weight: 600;
		margin-bottom: 8px;
		color: var(--text-primary);
	}

	.helper-name {
		color: var(--accent);
		font-size: 14px;
		font-weight: 500;
	}

	.rating-section {
		margin-bottom: 24px;
	}

	.rating-section > label {
		display: block;
		color: var(--text-secondary);
		font-size: 13px;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-bottom: 12px;
	}

	.stars {
		display: flex;
		gap: 8px;
		margin-bottom: 12px;
	}

	.star {
		background: none;
		border: none;
		font-size: 32px;
		cursor: pointer;
		color: var(--text-muted);
		transition: all var(--transition);
		line-height: 1;

		&:hover {
			color: var(--accent);
			transform: scale(1.15);
		}

		&.active {
			color: var(--accent);
		}
	}

	.rating-text {
		display: block;
		color: var(--text-secondary);
		font-size: 13px;
		margin-top: 8px;
	}

	.input-wrap {
		margin-bottom: 20px;
		position: relative;
	}

	.input-wrap label {
		display: block;
		color: var(--text-secondary);
		font-size: 13px;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-bottom: 8px;
	}

	textarea {
		width: 100%;
		padding: 12px;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		color: var(--text-primary);
		font-size: 14px;
		font-family: var(--font-body);
		resize: vertical;
		transition: all var(--transition);

		&::placeholder {
			color: var(--text-muted);
		}

		&:hover {
			border-color: var(--border-hover);
		}

		&:focus {
			outline: none;
			border-color: var(--accent);
			box-shadow: 0 0 0 3px var(--accent-dim);
		}

		&:disabled {
			opacity: 0.6;
			cursor: not-allowed;
		}
	}

	.char-count {
		display: block;
		text-align: right;
		color: var(--text-muted);
		font-size: 12px;
		margin-top: 4px;
	}

	.submit-btn {
		width: 100%;
		padding: 12px 16px;
		background: var(--accent);
		color: var(--bg);
		border: none;
		border-radius: var(--radius-sm);
		font-family: var(--font-display);
		font-size: 15px;
		font-weight: 600;
		cursor: pointer;
		transition: all var(--transition);

		&:hover:not(:disabled) {
			background: var(--accent-hover);
			transform: translateY(-2px);
			box-shadow: 0 8px 16px rgba(232, 255, 71, 0.2);
		}

		&:active:not(:disabled) {
			transform: translateY(0);
		}

		&:disabled {
			opacity: 0.6;
			cursor: not-allowed;
		}
	}
</style>
