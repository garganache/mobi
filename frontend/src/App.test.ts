import { render, fireEvent, screen } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import App from './App.svelte';

describe('App', () => {
  it('renders textarea and save button', () => {
    render(App);
    expect(screen.getByLabelText('Description')).toBeTruthy();
    expect(screen.getByText('Save')).toBeTruthy();
  });

  it('calls fetch on save', async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
    // @ts-ignore
    global.fetch = mockFetch;

    render(App);
    const textarea = screen.getByLabelText('Description') as HTMLTextAreaElement;
    const button = screen.getByText('Save');

    await fireEvent.input(textarea, { target: { value: 'Hello' } });
    await fireEvent.click(button);

    expect(mockFetch).toHaveBeenCalled();
  });
});
