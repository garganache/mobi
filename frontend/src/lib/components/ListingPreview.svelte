<script lang="ts">
  import { fade } from 'svelte/transition';
  import { t, getAmenityLabel, getRoomLabel } from '../i18n';
  
  export let listingData: Record<string, any>;
  export let synthesis: any = null;
  export let images: string[] = [];
  export let onEdit: () => void;
  export let onSubmit: () => void;
  export let individualAnalyses: any[] = [];
  
  // Debug: log images when component receives them
  $: {
    console.log('📷 ListingPreview received images:', images);
    console.log('   - images.length:', images.length);
    if (images.length > 0) {
      console.log('   - first image:', images[0].substring(0, 100));
    }
  }

  // State for save functionality
  let isSubmitting = false;
  let error: string | null = null;
  let showSuccessModal = false;
  let savedListingId: string | null = null;

  async function handleSubmit() {
    isSubmitting = true;
    error = null;
    
    try {
      // Prepare payload
      const payload = {
        // Property data
        property_type: listingData.property_type,
        price: listingData.price,
        bedrooms: listingData.bedrooms,
        bathrooms: listingData.bathrooms,
        square_feet: listingData.square_feet,
        address: listingData.address,
        city: listingData.city,
        state: listingData.state,
        zip_code: listingData.zip_code,
        
        // All other form fields
        additional_fields: listingData,
        
        // Images with AI analysis
        images: images.map((imgUrl, index) => ({
          image_data: imgUrl,  // Base64 or URL
          order_index: index,
          ai_analysis: individualAnalyses[index] || null
        })),
        
        // Synthesis data
        synthesis: synthesis ? {
          total_rooms: synthesis.total_rooms,
          layout_type: synthesis.layout_type,
          unified_description: synthesis.unified_description,
          room_breakdown: synthesis.room_breakdown,
          property_overview: synthesis.property_overview,
          interior_features: synthesis.interior_features || [],
          exterior_features: synthesis.exterior_features || []
        } : null
      };
      
      // POST to backend
      const response = await fetch('/api/listings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Save failed' }));
        throw new Error(errorData.detail || 'Failed to save listing');
      }
      
      const result = await response.json();
      
      // Show success
      savedListingId = result.listing_id;
      showSuccessModal = true;
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to save listing';
      console.error('Save listing error:', err);
    } finally {
      isSubmitting = false;
    }
  }

  // Generate comprehensive description
  function generateDescription() {
    let desc = '';
    
    // Start with synthesis unified description if available
    if (synthesis?.unified_description) {
      desc += synthesis.unified_description + '\n\n';
    }
    
    // Add property type and style
    if (synthesis?.property_overview) {
      const propertyType = synthesis.property_overview.property_type || listingData.property_type || 'Property';
      const style = synthesis.property_overview.style || '';
      desc += `This ${propertyType}${style ? ` features ${style} styling` : ''}. `;
    } else if (listingData.property_type) {
      desc += `This ${listingData.property_type}. `;
    }
    
    // Add specific details from form data
    if (listingData.bedrooms) {
      desc += `${listingData.bedrooms} bedroom${listingData.bedrooms > 1 ? 's' : ''}, `;
    }
    if (listingData.bathrooms) {
      desc += `${listingData.bathrooms} bathroom${listingData.bathrooms > 1 ? 's' : ''}. `;
    }
    if (listingData.square_footage) {
      desc += `${listingData.square_footage} sq ft. `;
    }
    
    // Add amenities narrative
    if (synthesis?.property_overview?.common_amenities?.length > 0) {
      const amenities = synthesis.property_overview.common_amenities.map((amenity: string) => 
        getAmenityLabel(amenity)
      );
      desc += `\n\nAmenities include: ${amenities.join(', ')}.`;
    }
    
    // Add condition and other details
    if (synthesis?.property_overview?.condition) {
      desc += ` The property is in ${synthesis.property_overview.condition} condition.`;
    }
    
    // Add room breakdown if available
    if (synthesis?.room_breakdown && Object.keys(synthesis.room_breakdown).length > 0) {
      desc += '\n\nProperty features:';
      for (const [room, count] of Object.entries(synthesis.room_breakdown)) {
        const roomName = room.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        desc += ` ${count} ${roomName}${count > 1 ? 's' : ''},`;
      }
      desc = desc.slice(0, -1) + '.'; // Remove trailing comma and add period
    }
    
    return desc.trim() || t('message.beautiful_property_ready', 'ro');
  }

  // Format currency for price
  function formatPrice(price: any): string {
    if (!price) return t('message.not_specified', 'ro');
    const numPrice = typeof price === 'string' ? parseFloat(price.replace(/[^\d.]/g, '')) : price;
    if (isNaN(numPrice)) return price;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numPrice);
  }

  // Get image caption from vision analysis if available
  function getImageCaption(index: number): string {
    if (individualAnalysesFromSynthesis && individualAnalysesFromSynthesis[index]) {
      const analysis = individualAnalysesFromSynthesis[index];
      if (analysis.description) {
        return analysis.description;
      }
    }
    return `${t('label.property_image', 'ro')} ${index + 1}`;
  }

  // Group form fields by category for better organization
  function organizeFormData() {
    const categories = {
      [t('category.basic_info', 'ro')]: {},
      [t('category.location_address', 'ro')]: {},
      [t('category.property_features', 'ro')]: {},
      [t('category.financial_details', 'ro')]: {},
      [t('category.additional_info', 'ro')]: {}
    };

    Object.entries(listingData).forEach(([key, value]) => {
      if (!value || ['property_type', 'price'].includes(key)) return;
      
      const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      
      if (['address', 'city', 'state', 'zip_code', 'neighborhood'].includes(key)) {
        categories[t('category.location_address', 'ro')][formattedKey] = value;
      } else if (['price', 'deposit', 'hoa_fees', 'property_tax'].includes(key)) {
        categories[t('category.financial_details', 'ro')][formattedKey] = key === 'price' ? formatPrice(value) : value;
      } else if (['bedrooms', 'bathrooms', 'square_footage', 'lot_size', 'year_built', 'parking_spaces'].includes(key)) {
        categories[t('category.property_features', 'ro')][formattedKey] = value;
      } else if (['description', 'title', 'listing_type'].includes(key)) {
        categories[t('category.basic_info', 'ro')][formattedKey] = value;
      } else {
        categories[t('category.additional_info', 'ro')][formattedKey] = value;
      }
    });

    return categories;
  }

  // Import individual analyses if available
  $: individualAnalysesFromSynthesis = synthesis?.individual_analyses || [];
</script>

<div class="listing-preview">
  <!-- Hero Section: Main image + title -->
  <div class="preview-hero">
    <h1>{t('header.preview_listing', 'ro')}</h1>
    <p class="subtitle">{t('message.review_before_publish', 'ro')}</p>
    {#if listingData.property_type || listingData.title}
      <h2 class="property-title">
        {listingData.title || `${listingData.property_type} ${t('header.listing', 'ro')}`}
      </h2>
    {/if}
  </div>

  <!-- Property Description -->
  <section class="description-section">
    <h2>{t('header.property_description', 'ro')}</h2>
    <div class="generated-description">
      {generateDescription()}
    </div>
  </section>

  <!-- Image Gallery -->
  {#if images.length > 0}
    <section class="images-section">
      <h2>{t('header.property_images', 'ro')} ({images.length})</h2>
      <div class="image-grid">
        {#each images as image, i}
          <div class="preview-image">
            <img src={image} alt={getImageCaption(i)} />
            <div class="image-caption">
              {getImageCaption(i)}
            </div>
          </div>
        {/each}
      </div>
    </section>
  {/if}

  <!-- Property Details -->
  <section class="details-section">
    <h2>{t('header.property_details', 'ro')}</h2>
    <div class="details-grid">
      <!-- Basic Info -->
      <div class="detail-category">
        <h3>{t('header.basic_info', 'ro')}</h3>
        <dl>
          <dt>{t('field.property_type', 'ro')}:</dt>
          <dd>{listingData.property_type || t('message.not_specified', 'ro')}</dd>
          {#if listingData.price}
            <dt>{t('field.price', 'ro')}:</dt>
            <dd>{formatPrice(listingData.price)}</dd>
          {/if}
          {#if listingData.title}
            <dt>{t('field.title', 'ro')}:</dt>
            <dd>{listingData.title}</dd>
          {/if}
        </dl>
      </div>

      <!-- Features & Amenities -->
      {#if synthesis?.property_overview?.common_amenities?.length > 0}
        <div class="detail-category">
          <h3>{t('header.features_amenities', 'ro')}</h3>
          <ul class="amenity-list">
            {#each (synthesis.property_overview.common_amenities || []) as amenity}
              <li>{getAmenityLabel(amenity)}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Room Breakdown -->
      {#if synthesis?.room_breakdown && Object.keys(synthesis.room_breakdown).length > 0}
        <div class="detail-category">
          <h3>{t('header.room_breakdown', 'ro')}</h3>
          <ul>
            {#each Object.entries(synthesis.room_breakdown) as [room, count]}
              <li>{count}x {getRoomLabel(room)}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Organized Form Fields -->
      {#each Object.entries(organizeFormData()) as [category, fields]}
        {#if Object.keys(fields).length > 0}
          <div class="detail-category">
            <h3>{category}</h3>
            <dl>
              {#each Object.entries(fields) as [key, value]}
                <dt>{key}:</dt>
                <dd>{value}</dd>
              {/each}
            </dl>
          </div>
        {/if}
      {/each}
    </div>
  </section>

  <!-- Actions -->
  <div class="preview-actions">
    <button class="btn-secondary" on:click={onEdit} disabled={isSubmitting}>
      ← {t('button.edit', 'ro')} {t('header.listing', 'ro')}
    </button>
    <button 
      class="btn-primary" 
      on:click={handleSubmit}
      disabled={isSubmitting}
    >
      {#if isSubmitting}
        <span class="spinner"></span>
        {t('button.saving', 'ro')}...
      {:else}
        {t('button.publish_listing', 'ro')} →
      {/if}
    </button>
  </div>

  {#if error}
    <div class="error-message">
      <p>❌ {error}</p>
    </div>
  {/if}

  {#if showSuccessModal}
    <div class="success-modal" transition:fade>
      <div class="modal-content">
        <h2>✅ {t('success.listing_saved', 'ro')}!</h2>
        <p>{t('message.listing_has_been_saved', 'ro')}</p>
        <p class="listing-id">{t('label.listing_id', 'ro')}: #{savedListingId}</p>
        
        <div class="modal-actions">
          <button class="btn-secondary" on:click={() => window.location.href = '/'}>
            {t('button.create_another', 'ro')}
          </button>
          <button class="btn-primary" on:click={() => window.location.href = `/listings/${savedListingId}`}>
            {t('button.view_listing', 'ro')}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  /* Preview page styles */
  .listing-preview {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .preview-hero {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
  }

  .preview-hero h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    font-size: 1.125rem;
    color: #6b7280;
    margin: 0 0 1rem 0;
  }

  .property-title {
    font-size: 1.875rem;
    font-weight: 600;
    color: #374151;
    margin: 1rem 0 0 0;
  }

  .description-section,
  .images-section,
  .details-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
  }

  .description-section h2,
  .images-section h2,
  .details-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 1rem 0;
    border-bottom: 2px solid #f3f4f6;
    padding-bottom: 0.75rem;
  }

  .generated-description {
    font-size: 1.125rem;
    line-height: 1.7;
    color: #374151;
    white-space: pre-wrap;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .preview-image {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .preview-image:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.15);
  }

  .preview-image img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  .image-caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
    color: white;
    padding: 1.5rem 1rem 0.75rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .detail-category {
    background: #f9fafb;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
  }

  .detail-category h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 1rem 0;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .detail-category dl {
    margin: 0;
  }

  .detail-category dt {
    font-weight: 600;
    color: #374151;
    margin-top: 0.75rem;
  }

  .detail-category dd {
    margin: 0.25rem 0 0 0;
    color: #6b7280;
  }

  .amenity-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .amenity-list li {
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .preview-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 3rem;
    padding: 2rem 0;
  }

  .error-message {
    text-align: center;
    margin-top: 1rem;
    padding: 1rem;
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    color: #dc2626;
  }

  .spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .success-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    text-align: center;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  }

  .modal-content h2 {
    color: #10b981;
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
  }

  .modal-content p {
    color: #374151;
    margin: 0.5rem 0;
    line-height: 1.6;
  }

  .listing-id {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: #6b7280;
    background: #f3f4f6;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    display: inline-block;
    margin: 1rem 0;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
  }

  .btn-primary,
  .btn-secondary {
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
  }

  .btn-primary {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 8px 15px -3px rgba(37, 99, 235, 0.4);
  }

  .btn-secondary {
    background: #e5e7eb;
    color: #374151;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #d1d5db;
    transform: translateY(-1px);
  }

  .btn-primary:disabled,
  .btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  @media (max-width: 768px) {
    .modal-actions {
      flex-direction: column;
      align-items: center;
    }

    .modal-actions button {
      width: 100%;
      max-width: 300px;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .listing-preview {
      padding: 1rem;
    }

    .preview-hero h1 {
      font-size: 2rem;
    }

    .property-title {
      font-size: 1.5rem;
    }

    .description-section,
    .images-section,
    .details-section {
      padding: 1.5rem;
    }

    .image-grid {
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem;
    }

    .details-grid {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .preview-actions {
      flex-direction: column;
      align-items: center;
    }

    .btn-primary,
    .btn-secondary {
      width: 100%;
      max-width: 300px;
    }
  }

  @media (max-width: 480px) {
    .listing-preview {
      padding: 0.5rem;
    }

    .preview-hero {
      padding: 1rem 0;
    }

    .preview-hero h1 {
      font-size: 1.75rem;
    }

    .description-section,
    .images-section,
    .details-section {
      padding: 1rem;
    }

    .image-grid {
      grid-template-columns: 1fr;
    }

    .generated-description {
      font-size: 1rem;
    }
  }
</style>