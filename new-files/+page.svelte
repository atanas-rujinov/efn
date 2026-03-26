<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import ReviewForm from '$lib/components/ReviewForm.svelte';
  
  let requestId: number;
  let requestType: 'drive' | 'shop';
  let requestDetails: any = null;
  let loading = true;
  let error = '';
  let isCompleting = false;
  let showReviewForm = false;
  
  onMount(async () => {
    // Get request ID and type from URL params
    const params = new URLSearchParams(window.location.search);
    requestId = parseInt(params.get('id') || '0');
    requestType = (params.get('type') || 'drive') as 'drive' | 'shop';
    
    if (!requestId) {
      error = 'Invalid request';
      loading = false;
      return;
    }
    
    await loadRequestDetails();
  });
  
  const loadRequestDetails = async () => {
    try {
      const response = await fetch(`/api/${requestType}-requests/${requestId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load request details');
      }
      
      requestDetails = await response.json();
      loading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
      loading = false;
    }
  };
  
  const completeRequest = async () => {
    if (!confirm('Are you sure you want to mark this request as completed?')) {
      return;
    }
    
    isCompleting = true;
    
    try {
      const response = await fetch(`/api/${requestType}-requests/${requestId}/complete`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to complete request');
      }
      
      // Show review form
      showReviewForm = true;
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      isCompleting = false;
    }
  };
  
  const handleReviewSuccess = () => {
    // Redirect to dashboard after successful review
    goto('/dashboard');
  };
  
  const skipReview = () => {
    goto('/dashboard');
  };
</script>

<svelte:head>
  <title>Complete Request - Accessibility Helper</title>
</svelte:head>

<div class="complete-page">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading request details...</p>
    </div>
  {:else if error && !requestDetails}
    <div class="error-state">
      <h2>Error</h2>
      <p>{error}</p>
      <button on:click={() => goto('/dashboard')} class="btn-secondary">
        Back to Dashboard
      </button>
    </div>
  {:else if showReviewForm && requestDetails}
    <ReviewForm
      requestId={requestId}
      requestType={requestType}
      driverId={requestDetails.driver}
      driverName={requestDetails.driver_name || 'Your helper'}
      onSubmitSuccess={handleReviewSuccess}
    />
    <div class="skip-section">
      <button on:click={skipReview} class="btn-text">Skip for now</button>
    </div>
  {:else if requestDetails}
    <div class="request-details">
      <h1>Complete Request</h1>
      
      <div class="details-card">
        <h2>{requestType === 'drive' ? 'Drive' : 'Shopping'} Request</h2>
        
        <div class="info-section">
          <div class="info-row">
            <span class="label">Helper:</span>
            <span class="value">{requestDetails.driver_name || 'Unknown'}</span>
          </div>
          
          <div class="info-row">
            <span class="label">From:</span>
            <span class="value">{requestDetails.start_address}</span>
          </div>
          
          <div class="info-row">
            <span class="label">To:</span>
            <span class="value">{requestDetails.dest_address}</span>
          </div>
          
          {#if requestDetails.description}
            <div class="info-row">
              <span class="label">Description:</span>
              <span class="value">{requestDetails.description}</span>
            </div>
          {/if}
        </div>
        
        {#if requestDetails.is_completed}
          <div class="completed-badge">
            ✓ Request Completed
          </div>
        {:else}
          <div class="action-section">
            <p class="completion-text">
              Has this request been completed successfully?
            </p>
            <button
              on:click={completeRequest}
              disabled={isCompleting}
              class="btn-primary"
            >
              {isCompleting ? 'Completing...' : 'Mark as Completed'}
            </button>
          </div>
        {/if}
        
        {#if error}
          <div class="error-message">
            {error}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .complete-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .loading {
    text-align: center;
    color: white;
  }
  
  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-state {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    max-width: 400px;
  }
  
  .error-state h2 {
    color: #dc2626;
    margin-bottom: 1rem;
  }
  
  .request-details {
    width: 100%;
    max-width: 600px;
  }
  
  .request-details h1 {
    color: white;
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
  }
  
  .details-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  }
  
  .details-card h2 {
    font-size: 1.5rem;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
  }
  
  .info-section {
    margin-bottom: 1.5rem;
  }
  
  .info-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .info-row:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  
  .label {
    font-weight: 600;
    color: #666;
    min-width: 100px;
  }
  
  .value {
    color: #1a1a1a;
    flex: 1;
  }
  
  .completed-badge {
    background-color: #10b981;
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 1.1rem;
  }
  
  .action-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 2px solid #e5e7eb;
  }
  
  .completion-text {
    font-size: 1rem;
    color: #666;
    margin-bottom: 1rem;
    text-align: center;
  }
  
  .btn-primary {
    width: 100%;
    padding: 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary:hover:not(:disabled) {
    background-color: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }
  
  .btn-primary:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
    transform: none;
  }
  
  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    cursor: pointer;
    margin-top: 1rem;
  }
  
  .btn-secondary:hover {
    background-color: #2563eb;
  }
  
  .error-message {
    margin-top: 1rem;
    padding: 0.875rem;
    background-color: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    color: #dc2626;
    font-size: 0.9rem;
  }
  
  .skip-section {
    text-align: center;
    margin-top: 1rem;
  }
  
  .btn-text {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 0.95rem;
    text-decoration: underline;
    padding: 0.5rem;
  }
  
  .btn-text:hover {
    opacity: 0.8;
  }
  
  /* Mobile responsive */
  @media (max-width: 640px) {
    .complete-page {
      padding: 1rem;
    }
    
    .details-card {
      padding: 1.5rem;
    }
    
    .request-details h1 {
      font-size: 1.5rem;
    }
    
    .info-row {
      flex-direction: column;
      gap: 0.25rem;
    }
    
    .label {
      min-width: auto;
    }
  }
</style>
