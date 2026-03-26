<script lang="ts">
	import { notifications } from '$lib/stores/notifications';
</script>

<div class="toast-container">
	{#each $notifications as notif (notif.id)}
		<div class="toast toast--{notif.type}" role="alert">
			<span class="toast__icon">
				{#if notif.type === 'success'}✓{:else if notif.type === 'error'}✕{:else}i{/if}
			</span>
			<span class="toast__message">{notif.message}</span>
			<button class="toast__close" on:click={() => notifications.remove(notif.id)}>✕</button>
		</div>
	{/each}
</div>

<style>
	.toast-container {
		position: fixed;
		bottom: 2rem;
		right: 2rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		z-index: 9999;
		pointer-events: none;
	}

	.toast {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 1.25rem;
		border-radius: 8px;
		backdrop-filter: blur(12px);
		border: 1px solid rgba(255, 255, 255, 0.08);
		font-size: 0.875rem;
		font-family: inherit;
		pointer-events: all;
		animation: slideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
		max-width: 360px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
	}

	.toast--success {
		background: rgba(16, 185, 129, 0.15);
		border-color: rgba(16, 185, 129, 0.3);
		color: #6ee7b7;
	}

	.toast--error {
		background: rgba(239, 68, 68, 0.15);
		border-color: rgba(239, 68, 68, 0.3);
		color: #fca5a5;
	}

	.toast--info {
		background: rgba(99, 102, 241, 0.15);
		border-color: rgba(99, 102, 241, 0.3);
		color: #a5b4fc;
	}

	.toast__icon {
		font-size: 0.75rem;
		font-weight: 700;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		background: currentColor;
		color: #0f0f13;
		flex-shrink: 0;
	}

	.toast__message {
		flex: 1;
	}

	.toast__close {
		background: none;
		border: none;
		color: currentColor;
		cursor: pointer;
		opacity: 0.6;
		font-size: 0.75rem;
		padding: 0;
		transition: opacity 0.2s;
	}

	.toast__close:hover {
		opacity: 1;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateX(20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}
</style>
