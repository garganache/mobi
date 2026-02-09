import './app.css';
import App from './App.svelte';
import { mount } from 'svelte'; // Import the mount function

// Instead of: const app = new App({...})
const app = mount(App, {
  target: document.getElementById('app') as HTMLElement,
});

export default app;
