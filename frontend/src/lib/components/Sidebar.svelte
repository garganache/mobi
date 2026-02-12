<script lang="ts">
  import { navigate, useLocation } from 'svelte-routing';
  import { t } from '../i18n';
  
  let isOpen = false;
  const location = useLocation();
  
  $: currentPath = $location?.pathname || '/';
  
  function toggleMobileMenu() {
    isOpen = !isOpen;
  }
  
  function handleLinkClick(event: Event, path: string) {
    event.preventDefault();
    navigate(path);
    // Close mobile menu on navigation
    isOpen = false;
  }
  
  $: isActiveCreate = currentPath === '/' || currentPath === '/create';
  $: isActiveListings = currentPath.startsWith('/listings');
</script>

<aside class="sidebar" class:mobile-open={isOpen}>
  <!-- Mobile hamburger menu -->
  <button 
    class="mobile-toggle" 
    on:click={toggleMobileMenu}
    aria-label="Toggle navigation menu"
    aria-expanded={isOpen}
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="hamburger-icon">
      {#if isOpen}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      {:else}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      {/if}
    </svg>
  </button>

  <!-- Navigation menu -->
  <nav class="nav-menu">
    <a 
      href="/" 
      class="nav-link"
      class:active={isActiveCreate}
      on:click={(e) => handleLinkClick(e, '/')}
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Creează Anunț Nou
    </a>
    
    <a 
      href="/listings" 
      class="nav-link"
      class:active={isActiveListings}
      on:click={(e) => handleLinkClick(e, '/listings')}
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      Anunțurile Mele
    </a>
  </nav>
</aside>

<!-- Mobile overlay -->
{#if isOpen}
  <div class="mobile-overlay" on:click={toggleMobileMenu}></div>
{/if}

<style>
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 250px;
    height: 100vh;
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
    border-right: 1px solid #374151;
    z-index: 1000;
    transition: transform 0.3s ease;
    overflow-y: auto;
  }

  .mobile-toggle {
    display: none;
    position: absolute;
    top: 1rem;
    right: -3rem;
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 0.375rem;
    padding: 0.5rem;
    cursor: pointer;
    color: #d1d5db;
    transition: all 0.2s ease;
  }

  .mobile-toggle:hover {
    background: #374151;
    color: #f9fafb;
  }

  .hamburger-icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  .nav-menu {
    padding: 2rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.5rem;
    color: #d1d5db;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
  }

  .nav-link:hover {
    background: rgba(59, 130, 246, 0.1);
    color: #f9fafb;
    border-left-color: #3b82f6;
  }

  .nav-link.active {
    background: rgba(59, 130, 246, 0.15);
    color: #f9fafb;
    border-left-color: #3b82f6;
    font-weight: 600;
  }

  .nav-icon {
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;
  }

  .mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }

  /* Mobile responsive styles */
  @media (max-width: 768px) {
    .sidebar {
      transform: translateX(-100%);
      width: 280px;
    }

    .sidebar.mobile-open {
      transform: translateX(0);
    }

    .mobile-toggle {
      display: block;
    }

    .mobile-overlay {
      display: block;
    }
  }

  /* Ensure main content doesn't overlap with sidebar */
  :global(body) {
    margin-left: 0;
  }

  @media (min-width: 769px) {
    :global(body) {
      margin-left: 250px;
    }
  }

  /* Scrollbar styling for dark theme */
  .sidebar::-webkit-scrollbar {
    width: 6px;
  }

  .sidebar::-webkit-scrollbar-track {
    background: #1f2937;
  }

  .sidebar::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 3px;
  }

  .sidebar::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
  }
</style>