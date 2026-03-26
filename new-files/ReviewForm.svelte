<script lang="ts">
  import { onMount } from 'svelte';
  
  export let requestId: number;
  export let requestType: 'drive' | 'shop';
  export let driverId: number;
  export let driverName: string;
  export let onSubmitSuccess: () => void;
  
  let rating = 0;
  let comment = '';
  let hoveredRating = 0;
  let isSubmitting = false;
  let error = '';
  let showSuccess = false;
  
  const submitReview = async () => {
    if (rating === 0) {
      error = 'Please select a rating';
      return;
    }
    
    isSubmitting = true;
    error = '';
    
    try {
      const response = await fetch('/api/reviews', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // In production, add auth token here
        },
        body: JSON.stringify({
          rating,
          comment: comment.trim() || null,
          driver_id: driverId,
          request_id: requestId,
          request_type: requestType
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit review');
      }
      
      showSuccess = true;
      setTimeout(() => {
        onSubmitSuccess();
      }, 1500);
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      isSubmitting = false;
    }
  };
  
  const setRating = (value: number) => {
    rating = value;
  };
  
  const setHover = (value: number) => {
    hoveredRating = value;
  };
</script>

<div class="review-form">
  {#if showSuccess}
    <div class="success-message">
      <div class="success-icon">✓</div>
      <h3>Thank you for your feedback!</h3>
      <p>Your review has been submitted successfully.</p>
    </div>
  {:else}
    <div class="form-header">
      <h2>Rate Your Experience</h2>
      <p class="helper-name">How was your experience with {driverName}?</p>
    </div>
    
    <div class="rating-section">
      <label>Your Rating</label>
      <div class="stars">
        {#each [1, 2, 3, 4, 5] as star}
          <button
            type="button"
            class="star"
            class:filled={star <= (hoveredRating || rating)}
            on:click={() => setRating(star)}
            on:mouseenter={() => setHover(star)}
            on:mouseleave={() => setHover(0)}
            disabled={isSubmitting}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </button>
        {/each}
      </div>
      {#if rating > 0}
        <p class="rating-text">
          {#if rating === 5}
            Excellent!
          {:else if rating === 4}
            Very Good
          {:else if rating === 3}
            Good
          {:else if rating === 2}
            Fair
          {:else}
            Needs Improvement
          {/if}
        </p>
      {/if}
    </div>
    
    <div class="comment-section">
      <label for="comment">Additional Comments (Optional)</label>
      <textarea
        id="comment"
        bind:value={comment}
        placeholder="Share more details about your experience..."
        maxlength="1000"
        rows="4"
        disabled={isSubmitting}
      />
      <span class="char-count">{comment.length}/1000</span>
    </div>
    
    {#if error}
      <div class="error-message">
        {error}
      </div>
    {/if}
    
    <div class="button-group">
      <button
        type="button"
        class="btn-submit"
        on:click={submitReview}
        disabled={isSubmitting || rating === 0}
      >
        {isSubmitting ? 'Submitting...' : 'Submit Review'}
      </button>
    </div>
  {/if}
</div>

<style>
  .review-form {
    max-width: 500px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
  
  .form-header {
    margin-bottom: 2rem;
    text-align: center;
  }
  
  .form-header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
  }
  
  .helper-name {
    font-size: 1rem;
    color: #666;
  }
  
  .rating-section {
    margin-bottom: 2rem;
  }
  
  label {
    display: block;
    font-size: 0.95rem;
    font-weight: 500;
    color: #333;
    margin-bottom: 0.75rem;
  }
  
  .stars {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-bottom: 0.5rem;
  }
  
  .star {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    width: 48px;
    height: 48px;
    color: #ddd;
    transition: all 0.2s ease;
  }
  
  .star:hover:not(:disabled) {
    transform: scale(1.15);
  }
  
  .star.filled {
    color: #fbbf24;
  }
  
  .star:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  .rating-text {
    text-align: center;
    font-size: 1.1rem;
    font-weight: 500;
    color: #fbbf24;
    margin-top: 0.5rem;
  }
  
  .comment-section {
    margin-bottom: 2rem;
    position: relative;
  }
  
  textarea {
    width: 100%;
    padding: 0.875rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.95rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.2s;
  }
  
  textarea:focus {
    outline: none;
    border-color: #3b82f6;
  }
  
  textarea:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }
  
  .char-count {
    position: absolute;
    bottom: -1.5rem;
    right: 0;
    font-size: 0.8rem;
    color: #999;
  }
  
  .error-message {
    padding: 0.875rem;
    background-color: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    color: #dc2626;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }
  
  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }
  
  .btn-submit {
    flex: 1;
    padding: 0.875rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-submit:hover:not(:disabled) {
    background-color: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }
  
  .btn-submit:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
    transform: none;
  }
  
  .success-message {
    text-align: center;
    padding: 2rem;
  }
  
  .success-icon {
    width: 64px;
    height: 64px;
    background-color: #10b981;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1rem;
    animation: scaleIn 0.3s ease-out;
  }
  
  @keyframes scaleIn {
    from {
      transform: scale(0);
    }
    to {
      transform: scale(1);
    }
  }
  
  .success-message h3 {
    font-size: 1.5rem;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
  }
  
  .success-message p {
    color: #666;
  }
  
  /* Accessibility */
  @media (prefers-reduced-motion: reduce) {
    .star:hover:not(:disabled),
    .btn-submit:hover:not(:disabled) {
      transform: none;
    }
    
    .success-icon {
      animation: none;
    }
  }
  
  /* Mobile responsive */
  @media (max-width: 640px) {
    .review-form {
      padding: 1.5rem;
    }
    
    .star {
      width: 40px;
      height: 40px;
    }
    
    .form-header h2 {
      font-size: 1.5rem;
    }
  }
</style>
