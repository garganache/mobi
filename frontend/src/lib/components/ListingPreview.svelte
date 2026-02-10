<script lang="ts">
  export let listingData: Record<string, any>;
  export let synthesis: any = null;
  export let images: string[] = [];
  export let onEdit: () => void;
  export let onSubmit: () => void;

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
        amenity.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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
    
    return desc.trim() || 'A beautiful property ready for you to call home.';
  }

  // Format currency for price
  function formatPrice(price: any): string {
    if (!price) return 'Not specified';
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
    if (individualAnalyses && individualAnalyses[index]) {
      const analysis = individualAnalyses[index];
      if (analysis.description) {
        return analysis.description;
      }
    }
    return `Property image ${index + 1}`;
  }

  // Group form fields by category for better organization
  function organizeFormData() {
    const categories = {
      'Basic Information': {},
      'Location & Address': {},
      'Property Features': {},
      'Financial Details': {},
      'Additional Information': {}
    };

    Object.entries(listingData).forEach(([key, value]) => {
      if (!value || ['property_type', 'price'].includes(key)) return;
      
      const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      
      if (['address', 'city', 'state', 'zip_code', 'neighborhood'].includes(key)) {
        categories['Location & Address'][formattedKey] = value;
      } else if (['price', 'deposit', 'hoa_fees', 'property_tax'].includes(key)) {
        categories['Financial Details'][formattedKey] = key === 'price' ? formatPrice(value) : value;
      } else if (['bedrooms', 'bathrooms', 'square_footage', 'lot_size', 'year_built', 'parking_spaces'].includes(key)) {
        categories['Property Features'][formattedKey] = value;
      } else if (['description', 'title', 'listing_type'].includes(key)) {
        categories['Basic Information'][formattedKey] = value;
      } else {
        categories['Additional Information'][formattedKey] = value;
      }
    });

    return categories;
  }

  // Import individual analyses if available
  let individualAnalyses: any[] = [];
  if (synthesis?.individual_analyses) {
    individualAnalyses = synthesis.individual_analyses;
  }
</script>

<div class="listing-preview">
  <!-- Hero Section: Main image + title -->
  <div class="preview-hero">
    <h1>Your Listing Preview</h1>
    <p class="subtitle">Review everything before publishing</p>
    {#if listingData.property_type || listingData.title}
      <h2 class="property-title">
        {listingData.title || `${listingData.property_type} Listing`}
      </h2>
    {/if}
  </div>

  <!-- Property Description -->
  <section class="description-section">
    <h2>Property Description</h2>
    <div class="generated-description">
      {generateDescription()}
    </div>
  </section>

  <!-- Image Gallery -->
  {#if images.length > 0}
    <section class="images-section">
      <h2>Property Images ({images.length})</h2>
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
    <h2>Property Details</h2>
    <div class="details-grid">
      <!-- Basic Info -->
      <div class="detail-category">
        <h3>Basic Information</h3>
        <dl>
          <dt>Property Type:</dt>
          <dd>{listingData.property_type || 'Not specified'}</dd>
          {#if listingData.price}
            <dt>Price:</dt>
            <dd>{formatPrice(listingData.price)}</dd>
          {/if}
          {#if listingData.title}
            <dt>Title:</dt>
            <dd>{listingData.title}</dd>
          {/if}
        </dl>
      </div>

      <!-- Features & Amenities -->
      {#if synthesis?.property_overview?.common_amenities?.length > 0}
        <div class="detail-category">
          <h3>Features & Amenities</h3>
          <ul class="amenity-list">
            {#each (synthesis.property_overview.common_amenities || []) as amenity}
              <li>{amenity.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Room Breakdown -->
      {#if synthesis?.room_breakdown && Object.keys(synthesis.room_breakdown).length > 0}
        <div class="detail-category">
          <h3>Room Breakdown</h3>
          <ul>
            {#each Object.entries(synthesis.room_breakdown) as [room, count]}
              <li>{count}x {room.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</li>
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
    <button class="btn-secondary" on:click={onEdit}>
      ← Edit Listing
    </button>
    <button class="btn-primary" on:click={onSubmit}>
      Publish Listing →
    </button>
  </div>
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

  .btn-primary {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
  }

  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 15px -3px rgba(37, 99, 235, 0.4);
  }

  .btn-secondary {
    background: #e5e7eb;
    color: #374151;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
  }

  .btn-secondary:hover {
    background: #d1d5db;
    transform: translateY(-1px);
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