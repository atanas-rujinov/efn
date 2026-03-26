<script lang="ts">
  import { onMount } from 'svelte';
  
  export let driverId: number;
  
  interface Review {
    id: number;
    rating: number;
    comment: string | null;
    driver_id: number;
    author_id: number;
    created_at: string;
    driver_name: string;
  }
  
  interface DriverStats {
    driver_id: number;
    driver_name: string;
    average_rating: number;
    total_reviews: number;
    recent_reviews: Review[];
  }
  
  let stats: DriverStats | null = null;
  let loading = true;
  let error = '';
  
  onMount(async () => {
    await fetchDriverStats();
  });
  
  const fetchDriverStats = async () => {
    loading = true;
    error = '';
    
    try {
      const response = await fetch(`/api/reviews/driver/${driverId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load reviews');
      }
      
      stats = await response.json();
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };
  
  const getStarArray = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => i < rating);
  };
</script>

<div class="driver-reviews">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading reviews...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <p>{error}</p>
      <button on:click={fetchDriverStats} class="retry-btn">Try Again</button>
    </div>
  {:else if stats}
    <div class="stats-header">
      <div class="driver-info">
        <h2>{stats.driver_name}</h2>
        <div class="rating-summary">
          {#if stats.total_reviews > 0}
            <div class="average-rating">
              <span class="rating-number">{stats.average_rating.toFixed(1)}</span>
              <div class="stars-small">
                {#each getStarArray(Math.round(stats.average_rating)) as filled}
                  <svg class="star" class:filled viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                {/each}
              </div>
            </div>
            <span class="review-count">
              {stats.total_reviews} {stats.total_reviews === 1 ? 'review' : 'reviews'}
            </span>
          {:else}
            <p class="no-reviews-text">No reviews yet</p>
          {/if}
        </div>
      </div>
      
      {#if stats.total_reviews > 0}
        <div class="rating-distribution">
          {#each [5, 4, 3, 2, 1] as star}
            {@const count = stats.recent_reviews.filter(r => r.rating === star).length}
            {@const percentage = stats.total_reviews > 0 ? (count / stats.total_reviews) * 100 : 0}
            <div class="rating-bar">
              <span class="star-label">{star} ★</span>
              <div class="bar-container">
                <div class="bar-fill" style="width: {percentage}%"></div>
              </div>
              <span class="count">{count}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>
    
    {#if stats.recent_reviews.length > 0}
      <div class="reviews-list">
        <h3>Recent Reviews</h3>
        {#each stats.recent_reviews as review}
          <div class="review-card">
            <div class="review-header">
              <div class="stars">
                {#each getStarArray(review.rating) as filled}
                  <svg class="star" class:filled viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                {/each}
              </div>
              <span class="review-date">{formatDate(review.created_at)}</span>
            </div>
            {#if review.comment}
              <p class="review-comment">{review.comment}</p>
            {:else}
              <p class="no-comment">No additional comments</p>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .driver-reviews {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .loading {
    text-align: center;
    padding: 3rem;
  }
  
  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-state {
    text-align: center;
    padding: 3rem;
    color: #dc2626;
  }
  
  .retry-btn {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
  }
  
  .retry-btn:hover {
    background-color: #2563eb;
  }
  
  .stats-header {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }
  
  .driver-info h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1rem;
  }
  
  .rating-summary {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .average-rating {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .rating-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
  }
  
  .stars-small {
    display: flex;
    gap: 0.25rem;
  }
  
  .star {
    width: 24px;
    height: 24px;
    fill: #ddd;
  }
  
  .star.filled {
    fill: #fbbf24;
  }
  
  .review-count {
    color: #666;
    font-size: 0.95rem;
  }
  
  .no-reviews-text {
    color: #999;
    font-style: italic;
  }
  
  .rating-distribution {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
  }
  
  .rating-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .star-label {
    width: 40px;
    font-size: 0.9rem;
    color: #666;
  }
  
  .bar-container {
    flex: 1;
    height: 8px;
    background-color: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .bar-fill {
    height: 100%;
    background-color: #fbbf24;
    transition: width 0.3s ease;
  }
  
  .count {
    width: 40px;
    text-align: right;
    font-size: 0.85rem;
    color: #999;
  }
  
  .reviews-list {
    margin-top: 2rem;
  }
  
  .reviews-list h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1rem;
  }
  
  .review-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  
  .review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .stars {
    display: flex;
    gap: 0.25rem;
  }
  
  .review-date {
    font-size: 0.85rem;
    color: #999;
  }
  
  .review-comment {
    color: #333;
    line-height: 1.6;
    margin: 0;
  }
  
  .no-comment {
    color: #999;
    font-style: italic;
    margin: 0;
  }
  
  /* Mobile responsive */
  @media (max-width: 640px) {
    .stats-header {
      padding: 1.5rem;
    }
    
    .driver-info h2 {
      font-size: 1.5rem;
    }
    
    .rating-number {
      font-size: 2rem;
    }
    
    .rating-summary {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .review-card {
      padding: 1.25rem;
    }
  }
</style>
