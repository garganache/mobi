<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';

  export let message: string = '';
  export let avatar: 'ai' | 'user' = 'ai';
  export let typing = false;
  export let showAvatar = true;
  export let animationDuration = 300;

  // Split message into paragraphs for better formatting
  $: paragraphs = message ? message.split('\n\n').filter(p => p.trim()) : [];

  // Simulate typing effect
  let displayedText = '';
  let currentIndex = 0;

  $: if (typing && message) {
    displayedText = '';
    currentIndex = 0;
    typeText();
  } else {
    displayedText = message;
  }

  function typeText() {
    if (currentIndex < message.length) {
      displayedText = message.slice(0, currentIndex + 1);
      currentIndex++;
      setTimeout(typeText, 30 + Math.random() * 20); // Random typing speed
    }
  }
</script>

<div 
  class="ai-message {avatar}"
  in:fly={{ x: avatar === 'ai' ? -20 : 20, duration: animationDuration }}
  role="article"
  aria-label={avatar === 'ai' ? 'AI assistant message' : 'User message'}
>
  {#if showAvatar}
    <div 
      class="avatar {avatar}"
      in:scale={{ duration: animationDuration, start: 0.8 }}
    >
      {#if avatar === 'ai'}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="8" r="4" />
          <path d="M12 14c-4 0-8 2-8 6v1h16v-1c0-4-4-6-8-6z" />
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="8" r="4" />
          <path d="M12 14c-4 0-8 2-8 6v1h16v-1c0-4-4-6-8-6z" />
        </svg>
      {/if}
    </div>
  {/if}

  <div class="message-content">
    <div class="message-bubble">
      {#if paragraphs.length > 0}
        {#each paragraphs as paragraph, i}
          <p class="message-paragraph" in:fade={{ delay: i * 100, duration: animationDuration }}>
            {typing && avatar === 'ai' ? displayedText.split('\n\n')[i] || '' : paragraph}
          </p>
        {/each}
      {:else}
        <p class="message-paragraph">
          {typing && avatar === 'ai' ? displayedText : message}
        </p>
      {/if}
      
      {#if typing && avatar === 'ai'}
        <span class="typing-indicator" in:fade={{ delay: 500 }}>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </span>
      {/if}
    </div>
    
    {#if !typing && message}
      <div class="message-actions" in:fade={{ delay: animationDuration }}>
        <button 
          class="action-button"
          title="Copy message"
          on:click={() => navigator.clipboard.writeText(message)}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .ai-message {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
    align-items: flex-start;
  }

  .ai-message.user {
    flex-direction: row-reverse;
  }

  .avatar {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.2s ease;
  }

  .avatar.ai {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  .avatar.user {
    background: #e5e7eb;
    color: #6b7280;
  }

  .avatar svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .message-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 70%;
  }

  .ai-message.user .message-content {
    align-items: flex-end;
  }

  .message-bubble {
    padding: 1rem 1.25rem;
    border-radius: 1rem;
    position: relative;
    word-wrap: break-word;
    max-width: 100%;
  }

  .ai-message.ai .message-bubble {
    background: #f3f4f6;
    color: #1f2937;
    border-bottom-left-radius: 0.25rem;
  }

  .ai-message.user .message-bubble {
    background: #3b82f6;
    color: white;
    border-bottom-right-radius: 0.25rem;
  }

  .message-paragraph {
    margin: 0 0 0.75rem 0;
    line-height: 1.6;
  }

  .message-paragraph:last-child {
    margin-bottom: 0;
  }

  .typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    margin-left: 0.5rem;
  }

  .typing-dot {
    width: 0.5rem;
    height: 0.5rem;
    background: currentColor;
    border-radius: 50%;
    opacity: 0.4;
    animation: typing 1.4s infinite ease-in-out;
  }

  .typing-dot:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-dot:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 60%, 100% {
      opacity: 0.4;
      transform: scale(1);
    }
    30% {
      opacity: 1;
      transform: scale(1.2);
    }
  }

  .message-actions {
    display: flex;
    gap: 0.5rem;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .ai-message:hover .message-actions {
    opacity: 1;
  }

  .action-button {
    background: none;
    border: none;
    padding: 0.5rem;
    border-radius: 0.375rem;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .action-button:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .action-button svg {
    width: 1rem;
    height: 1rem;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .ai-message {
      gap: 0.5rem;
    }

    .avatar {
      width: 2rem;
      height: 2rem;
    }

    .avatar svg {
      width: 1rem;
      height: 1rem;
    }

    .message-content {
      max-width: 80%;
    }

    .message-bubble {
      padding: 0.75rem 1rem;
      font-size: 0.875rem;
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .avatar.user {
      background: #374151;
      color: #9ca3af;
    }

    .ai-message.ai .message-bubble {
      background: #374151;
      color: #f9fafb;
    }

    .action-button:hover {
      background: #4b5563;
      color: #f9fafb;
    }
  }

  /* Accessibility */
  @media (prefers-reduced-motion: reduce) {
    .typing-dot {
      animation: none;
    }

    .message-bubble,
    .avatar {
      transition: none;
    }
  }
</style>