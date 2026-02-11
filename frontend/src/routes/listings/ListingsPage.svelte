<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  
  interface Listing {
    id: string;
    images: string[];
    address?: string;
    price: number;
    property_type: string;
    bedrooms: number;
    bathrooms: number;
    square_feet?: number;
  }
  
  let listings: Listing[] = [];
  let loading = true;
  let error: string | null = null;
  
  onMount(async () => {
    try {
      const res = await fetch('/api/listings');
      if (!res.ok) throw new Error('Failed to fetch listings');
      listings = await res.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  });
  
  function handleCardClick(id: string) {
    navigate(`/listings/${id}`);
  }
</script>

<div class="listings-container">
  <header class="listings-header">
    <h1>Anunțurile Mele</h1>
    <button class="back-button" on:click={() => navigate('/')}>← Înapoi la creare</button>
  </header>

  {#if loading}
    <div class="loading-state">
      <div class="loading-spinner"></div>
      <p>Se încarcă anunțurile...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Eroare</h3>
      <p>{error}</p>
      <button class="retry-button" on:click={() => window.location.reload()}>Reîncarcă</button>
    </div>
  {:else if listings.length === 0}
    <div class="empty-state">
      <div class="empty-icon">🏠</div>
      <h3>Nu aveți anunțuri încă</h3>
      <p>Creați primul anunț pentru a începe</p>
      <button class="create-button" on:click={() => navigate('/')}>Creează anunț</button>
    </div>
  {:else}
    <div class="listings-grid">
      {#each listings as listing}
        <div class="listing-card" on:click={() => handleCardClick(listing.id)} on:keypress={(e) => e.key === 'Enter' && handleCardClick(listing.id)} role="button" tabindex="0">
          <div class="card-image">
            {#if listing.images && listing.images.length > 0}
              <img src={listing.images[0]} alt={listing.address || 'Proprietate'} />
            {:else}
              <div class="no-image">
                <span>Fără imagine</span>
              </div>
            {/if}
          </div>
          <div class="card-content">
            <h3 class="card-title">{listing.address || 'Adresă necunoscută'}</h3>
            <p class="card-price">{new Intl.NumberFormat('ro-RO').format(listing.price)} €</p>
            <p class="card-details">
              {listing.property_type} • {listing.bedrooms} dormitoare • {listing.bathrooms} băi
            </p>
            {#if listing.square_feet}
              <p class="card-square-feet">{listing.square_feet} mp</p>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .listings-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .listings-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .listings-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
  }

  .back-button {
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .back-button:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }

  .listings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .listing-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .listing-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: #3b82f6;
  }

  .listing-card:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .card-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
    background: #f3f4f6;
  }

  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-image {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    color: #6b7280;
  }

  .card-content {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
    line-height: 1.4;
  }

  .card-price {
    font-size: 1.25rem;
    font-weight: 700;
    color: #059669;
    margin: 0 0 0.5rem 0;
  }

  .card-details {
    color: #6b7280;
    margin: 0 0 0.25rem 0;
    font-size: 0.875rem;
  }

  .card-square-feet {
    color: #374151;
    margin: 0;
    font-weight: 500;
  }

  /* States */
  .loading-state,
  .error-state,
  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top: 4px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-icon,
  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .error-state h3,
  .empty-state h3 {
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .error-state p,
  .empty-state p {
    color: #6b7280;
    margin: 0 0 1.5rem 0;
  }

  .retry-button,
  .create-button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .retry-button:hover,
  .create-button:hover {
    background: #2563eb;
    transform: translateY(-1px);
  }

  /* Responsive */
  @media (max-width: 768px) {
    .listings-container {
      padding: 1rem;
    }

    .listings-header {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }

    .listings-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 480px) {
    .listings-container {
      padding: 0.5rem;
    }

    .listing-card {
      margin: 0 -0.5rem;
    }
  }
</style>