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
    description?: string;
    amenities_by_room?: Record<string, string[]>;
    [key: string]: any;
  }
  
  export let id: string;
  
  let listing: Listing | null = null;
  let loading = true;
  let error: string | null = null;
  let currentImageIndex = 0;
  
  onMount(async () => {
    if (!id) {
      error = 'ID anunț lipsă';
      loading = false;
      return;
    }
    
    try {
      const res = await fetch(`/api/listings/${id}`);
      if (res.status === 404) {
        error = 'Anunțul nu a fost găsit';
        return;
      }
      if (!res.ok) throw new Error('Failed to fetch listing');
      listing = await res.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  });
  
  function nextImage() {
    if (listing && listing.images && listing.images.length > 0) {
      currentImageIndex = (currentImageIndex + 1) % listing.images.length;
    }
  }
  
  function prevImage() {
    if (listing && listing.images && listing.images.length > 0) {
      currentImageIndex = (currentImageIndex - 1 + listing.images.length) % listing.images.length;
    }
  }
  
  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('ro-RO').format(amount);
  }
</script>

<div class="listing-detail-container">
  <header class="detail-header">
    <button class="back-button" on:click={() => navigate('/listings')}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Înapoi la anunțuri
    </button>
  </header>

  {#if loading}
    <div class="loading-state">
      <div class="loading-spinner"></div>
      <p>Se încarcă anunțul...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Eroare</h3>
      <p>{error}</p>
      <div class="error-actions">
        <button class="retry-button" on:click={() => window.location.reload()}>Reîncarcă</button>
        <button class="back-button" on:click={() => navigate('/listings')}>Înapoi la anunțuri</button>
      </div>
    </div>
  {:else if listing}
    <div class="listing-detail">
      <!-- Image Gallery -->
      <div class="image-gallery">
        {#if listing.images && listing.images.length > 0}
          <div class="gallery-main">
            <img src={listing.images[currentImageIndex]} alt={listing.address || 'Proprietate'} />
            
            {#if listing.images.length > 1}
              <button class="gallery-nav prev" on:click={prevImage} aria-label="Imaginea anterioară">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button class="gallery-nav next" on:click={nextImage} aria-label="Imaginea următoare">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <div class="gallery-indicators">
                {#each listing.images as _, index}
                  <button 
                    class="indicator {index === currentImageIndex ? 'active' : ''}"
                    on:click={() => currentImageIndex = index}
                    aria-label="Imaginea {index + 1}"
                  ></button>
                {/each}
              </div>
            {/if}
          </div>
          
          {#if listing.images.length > 1}
            <div class="gallery-thumbnails">
              {#each listing.images as image, index}
                <button 
                  class="thumbnail {index === currentImageIndex ? 'active' : ''}"
                  on:click={() => currentImageIndex = index}
                >
                  <img src={image} alt="Thumbnail {index + 1}" />
                </button>
              {/each}
            </div>
          {/if}
        {:else}
          <div class="no-images">
            <div class="no-images-icon">📷</div>
            <p>Nu există imagini pentru acest anunț</p>
          </div>
        {/if}
      </div>

      <!-- Property Info -->
      <div class="property-info">
        <div class="property-header">
          <h1 class="property-title">{listing.address || 'Adresă necunoscută'}</h1>
          <p class="property-price">{formatCurrency(listing.price)} €</p>
        </div>
        
        <div class="property-specs">
          <div class="spec-item">
            <span class="spec-label">Tip proprietate:</span>
            <span class="spec-value">{listing.property_type}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">Dormitoare:</span>
            <span class="spec-value">{listing.bedrooms}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">Băi:</span>
            <span class="spec-value">{listing.bathrooms}</span>
          </div>
          {#if listing.square_feet}
            <div class="spec-item">
              <span class="spec-label">Suprafață:</span>
              <span class="spec-value">{listing.square_feet} mp</span>
            </div>
          {/if}
        </div>
        
        {#if listing.description}
          <div class="description-section">
            <h2>Descriere</h2>
            <p class="description-text">{listing.description}</p>
          </div>
        {/if}
        
        {#if listing.amenities_by_room && Object.keys(listing.amenities_by_room).length > 0}
          <div class="amenities-section">
            <h2>Facilități</h2>
            {#each Object.entries(listing.amenities_by_room) as [room, amenities]}
              <div class="room-amenities">
                <h3>{room}</h3>
                <ul class="amenities-list">
                  {#each amenities as amenity}
                    <li>{amenity}</li>
                  {/each}
                </ul>
              </div>
            {/each}
          </div>
        {/if}
        
        <!-- Additional metadata if available -->
        {#if Object.keys(listing).filter(key => !['id', 'images', 'address', 'price', 'property_type', 'bedrooms', 'bathrooms', 'square_feet', 'description', 'amenities_by_room'].includes(key)).length > 0}
          <div class="metadata-section">
            <h2>Informații suplimentare</h2>
            <div class="metadata-grid">
              {#each Object.entries(listing).filter(([key]) => !['id', 'images', 'address', 'price', 'property_type', 'bedrooms', 'bathrooms', 'square_feet', 'description', 'amenities_by_room'].includes(key)) as [key, value]}
                {#if value !== null && value !== undefined && value !== ''}
                  <div class="metadata-item">
                    <span class="metadata-label">{key.replace(/_/g, ' ')}:</span>
                    <span class="metadata-value">{typeof value === 'object' ? JSON.stringify(value) : value}</span>
                  </div>
                {/if}
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .listing-detail-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }

  .detail-header {
    margin-bottom: 1.5rem;
  }

  .back-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #374151;
    text-decoration: none;
  }

  .back-button:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }

  .back-button svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .listing-detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: start;
  }

  /* Image Gallery */
  .image-gallery {
    position: sticky;
    top: 1rem;
  }

  .gallery-main {
    position: relative;
    width: 100%;
    height: 400px;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1rem;
  }

  .gallery-main img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .gallery-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .gallery-nav:hover {
    background: rgba(0, 0, 0, 0.7);
  }

  .gallery-nav.prev {
    left: 1rem;
  }

  .gallery-nav.next {
    right: 1rem;
  }

  .gallery-nav svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .gallery-indicators {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 0.5rem;
  }

  .indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .indicator.active {
    background: white;
    transform: scale(1.2);
  }

  .gallery-thumbnails {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding: 0.5rem 0;
  }

  .thumbnail {
    flex-shrink: 0;
    width: 80px;
    height: 60px;
    border: 2px solid transparent;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 0;
    background: none;
  }

  .thumbnail.active {
    border-color: #3b82f6;
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-images {
    width: 100%;
    height: 400px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    border-radius: 12px;
    color: #6b7280;
  }

  .no-images-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  /* Property Info */
  .property-info {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }

  .property-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .property-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .property-price {
    font-size: 2rem;
    font-weight: 700;
    color: #059669;
    margin: 0;
  }

  .property-specs {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .spec-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: 8px;
  }

  .spec-label {
    font-weight: 500;
    color: #6b7280;
  }

  .spec-value {
    font-weight: 600;
    color: #1f2937;
  }

  /* Sections */
  .description-section,
  .amenities-section,
  .metadata-section {
    margin-bottom: 2rem;
  }

  .description-section h2,
  .amenities-section h2,
  .metadata-section h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 1rem 0;
  }

  .description-text {
    color: #4b5563;
    line-height: 1.6;
  }

  .room-amenities {
    margin-bottom: 1.5rem;
  }

  .room-amenities h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 0.5rem 0;
  }

  .amenities-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
  }

  .amenities-list li {
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
    color: #4b5563;
  }

  .amenities-list li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: #10b981;
    font-weight: bold;
  }

  .metadata-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .metadata-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: 8px;
  }

  .metadata-label {
    font-weight: 500;
    color: #6b7280;
  }

  .metadata-value {
    font-weight: 600;
    color: #1f2937;
  }

  /* Loading State */
  .loading-state {
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

  /* Error State */
  .error-state {
    text-align: center;
    padding: 4rem 2rem;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .error-state h3 {
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .error-state p {
    color: #6b7280;
    margin: 0 0 1.5rem 0;
  }

  .error-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .retry-button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .retry-button:hover {
    background: #2563eb;
    transform: translateY(-1px);
  }

  /* Responsive */
  @media (max-width: 768px) {
    .listing-detail {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .image-gallery {
      position: static;
    }

    .gallery-main {
      height: 300px;
    }

    .property-specs {
      grid-template-columns: 1fr;
    }

    .error-actions {
      flex-direction: column;
    }
  }

  @media (max-width: 480px) {
    .listing-detail-container {
      padding: 0.5rem;
    }

    .gallery-main {
      height: 250px;
    }

    .property-info {
      padding: 1.5rem;
    }

    .property-title {
      font-size: 1.5rem;
    }

    .property-price {
      font-size: 1.5rem;
    }
  }
</style>