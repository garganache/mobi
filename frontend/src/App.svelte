<script lang="ts">
  import { onMount } from 'svelte';

  let text = '';
  let status: string | null = null;
  let loading = false;
  let history: { id: number; text: string; created_at: string }[] = [];

  async function loadLatest() {
    try {
      const res = await fetch('/api/description/latest');
      if (res.ok) {
        const data = await res.json();
        text = data.text;
      }
    } catch (e) {
      console.error('Failed to load latest description', e);
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/description?limit=10');
      if (res.ok) {
        history = await res.json();
      }
    } catch (e) {
      console.error('Failed to load description history', e);
    }
  }

  async function save() {
    status = null;
    loading = true;
    try {
      const res = await fetch('/api/description', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (res.ok) {
        status = 'Saved successfully';
        await loadHistory();
      } else {
        const data = await res.json().catch(() => ({}));
        status = data.detail ?? 'Save failed';
      }
    } catch (e) {
      status = 'Network error';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadLatest();
    loadHistory();
  });
</script>

<main>
  <h1>Mobi Description</h1>

  <label for="description">Description</label>
  <textarea
    id="description"
    bind:value={text}
    rows="4"
    cols="40"
    placeholder="Type a description..."
  ></textarea>

  <button on:click={save} disabled={loading}>
    {#if loading}
      Saving...
    {:else}
      Save
    {/if}
  </button>

  {#if status}
    <p data-testid="status">{status}</p>
  {/if}

  {#if history.length}
    <section style="margin-top: 2rem;">
      <h2>Recent descriptions</h2>
      <ul>
        {#each history as item}
          <li>{item.text}</li>
        {/each}
      </ul>
    </section>
  {/if}
</main>
