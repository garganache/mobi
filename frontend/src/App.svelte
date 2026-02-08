<script lang="ts">
  import { onMount } from 'svelte';

  let text = '';
  let status: string | null = null;
  let loading = false;

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
</main>
