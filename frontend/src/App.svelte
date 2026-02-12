<script lang="ts">
  import { Router, Route } from 'svelte-routing';
  import Sidebar from './lib/components/Sidebar.svelte';
  import Home from './routes/Home.svelte';
  import ListingsPage from './routes/listings/ListingsPage.svelte';
  import ListingDetail from './routes/listings/detail/ListingDetail.svelte';
</script>

<Router>
  <div class="app-container">
    <Sidebar />
    <main class="main-content">
      <Route path="/" component={Home} />
      <Route path="/listings" component={ListingsPage} />
      <Route path="/listings/:id" let:params>
        <ListingDetail id={params.id} />
      </Route>
    </main>
  </div>
</Router>

<style>
  .app-container {
    display: flex;
    min-height: 100vh;
  }
  
  .main-content {
    flex: 1;
    margin-left: 250px; /* Sidebar width */
    padding: 2rem;
    transition: margin-left 0.3s ease;
  }
  
  @media (max-width: 768px) {
    .main-content {
      margin-left: 0; /* Full width on mobile */
    }
  }
</style>