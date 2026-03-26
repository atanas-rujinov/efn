<script lang="ts">
  /**
   * Example: Dashboard page for disabled users
   * Shows how to integrate the review system into request management
   */
  
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import HelperRating from '$lib/components/HelperRating.svelte';
  
  interface Request {
    id: number;
    type: 'drive' | 'shop';
    description: string;
    start_address: string;
    dest_address: string;
    is_completed: boolean;
    driver: {
      id: number;
      name: string;
    } | null;
    created_at: string;
  }
  
  let activeRequests: Request[] = [];
  let completedRequests: Request[] = [];
  let loading = true;
  
  onMount(async () => {
    await loadRequests();
  });
  
  const loadRequests = async () => {
    try {
      // Load drive requests
      const driveRes = await fetch('/api/drive-requests/my-requests');
      const driveData = await driveRes.json();
      
      // Load shop requests
      const shopRes = await fetch('/api/shop-requests/my-requests');
      const shopData = await shopRes.json();
      
      // Combine and categorize
      const allRequests = [
        ...driveData.requests.map(r => ({ ...r, type: 'drive' })),
        ...shopData.requests.map(r => ({ ...r, type: 'shop' }))
      ];
      
      activeRequests = allRequests.filter(r => !r.is_completed);
      completedRequests = allRequests.filter(r => r.is_completed);
      
    } catch (error) {
      console.error('Failed to load requests:', error);
    } finally {
      loading = false;
    }
  };
  
  const goToComplete = (request: Request) => {
    goto(`/complete-request?id=${request.id}&type=${request.type}`);
  };
  
  const viewHelperReviews = (driverId: number) => {
    goto(`/helper/${driverId}/reviews`);
  };
</script>

<div class="dashboard">
  <h1>My Requests</h1>
  
  {#if loading}
    <div class="loading">Loading...</div>
  {:else}
    <!-- Active Requests -->
    <section class="requests-section">
      <h2>Active Requests</h2>
      {#if activeRequests.length === 0}
        <p class="empty-state">No active requests</p>
      {:else}
        <div class="requests-grid">
          {#each activeRequests as request}
            <div class="request-card">
              <div class="request-header">
                <span class="request-type">
                  {request.type === 'drive' ? '🚗 Drive' : '🛒 Shopping'}
                </span>
                {#if request.driver}
                  <button 
                    class="helper-name"
                    on:click={() => viewHelperReviews(request.driver.id)}
                  >
                    {request.driver.name}
                  </button>
                  <HelperRating driverId={request.driver.id} compact={true} />
                {:else}
                  <span class="no-helper">Waiting for helper...</span>
                {/if}
              </div>
              
              <div class="request-details">
                <p class="route">
                  <strong>From:</strong> {request.start_address}<br>
                  <strong>To:</strong> {request.dest_address}
                </p>
                {#if request.description}
                  <p class="description">{request.description}</p>
                {/if}
              </div>
              
              {#if request.driver}
                <button 
                  class="btn-complete"
                  on:click={() => goToComplete(request)}
                >
                  Complete & Review
                </button>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </section>
    
    <!-- Completed Requests -->
    <section class="requests-section">
      <h2>Completed Requests</h2>
      {#if completedRequests.length === 0}
        <p class="empty-state">No completed requests yet</p>
      {:else}
        <div class="requests-grid">
          {#each completedRequests as request}
            <div class="request-card completed">
              <div class="completed-badge">✓ Completed</div>
              <div class="request-header">
                <span class="request-type">
                  {request.type === 'drive' ? '🚗 Drive' : '🛒 Shopping'}
                </span>
                {#if request.driver}
                  <button 
                    class="helper-name"
                    on:click={() => viewHelperReviews(request.driver.id)}
                  >
                    {request.driver.name}
                  </button>
                  <HelperRating driverId={request.driver.id} compact={true} />
                {/if}
              </div>
              
              <div class="request-details">
                <p class="route">
                  <strong>From:</strong> {request.start_address}<br>
                  <strong>To:</strong> {request.dest_address}
                </p>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</div>

<style>
  .dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  h1 {
    font-size: 2rem;
    color: #1a1a1a;
    margin-bottom: 2rem;
  }
  
  h2 {
    font-size: 1.5rem;
    color: #333;
    margin-bottom: 1rem;
  }
  
  .loading {
    text-align: center;
    padding: 3rem;
    color: #666;
  }
  
  .requests-section {
    margin-bottom: 3rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #999;
    font-style: italic;
  }
  
  .requests-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }
  
  .request-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .request-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  
  .request-card.completed {
    opacity: 0.85;
  }
  
  .completed-badge {
    background-color: #10b981;
    color: white;
    padding: 0.5rem;
    border-radius: 6px;
    text-align: center;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  .request-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  
  .request-type {
    font-weight: 600;
    color: #3b82f6;
    font-size: 0.95rem;
  }
  
  .helper-name {
    background: none;
    border: none;
    color: #1a1a1a;
    font-weight: 500;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;
  }
  
  .helper-name:hover {
    color: #3b82f6;
  }
  
  .no-helper {
    color: #999;
    font-style: italic;
    font-size: 0.9rem;
  }
  
  .request-details {
    margin-bottom: 1rem;
  }
  
  .route {
    color: #333;
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }
  
  .description {
    color: #666;
    font-size: 0.85rem;
    font-style: italic;
    margin-top: 0.5rem;
  }
  
  .btn-complete {
    width: 100%;
    padding: 0.75rem;
    background-color: #10b981;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .btn-complete:hover {
    background-color: #059669;
  }
  
  @media (max-width: 768px) {
    .dashboard {
      padding: 1rem;
    }
    
    .requests-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
