import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TextInput from './TextInput.svelte';

describe('TextInput', () => {
  it('renders with correct label', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
      },
    });

    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('displays initial value', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: 'Initial Value',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.value).toBe('Initial Value');
  });

  it('displays placeholder text', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        placeholder: 'Enter text here',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.placeholder).toBe('Enter text here');
  });

  it('updates value on user input', async () => {
    const user = userEvent.setup();
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, 'New Value');

    expect(input.value).toBe('New Value');
  });

  it('handles empty value', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.value).toBe('');
  });

  it('handles special characters', async () => {
    const user = userEvent.setup();
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    const specialText = 'test@example.com';
    await user.type(input, specialText);

    expect(input.value).toBe(specialText);
  });

  it('shows validation error when provided', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        error: 'This field is required',
      },
    });

    expect(screen.getByText('This field is required')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('applies correct ARIA attributes', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input).toHaveAttribute('aria-label', 'Test Label');
    expect(input).toHaveAttribute('aria-invalid', 'false');
  });

  it('applies correct ARIA attributes when error is present', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        error: 'Error message',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'test-input-error');
  });

  it('applies error class when error is present', () => {
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        error: 'Error message',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.classList.contains('error')).toBe(true);
  });

  it('handles clearing input value', async () => {
    const user = userEvent.setup();
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: 'Initial',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.clear(input);

    expect(input.value).toBe('');
  });

  it('handles multiple updates', async () => {
    const user = userEvent.setup();
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    
    await user.type(input, 'First');

    await user.clear(input);
    await user.type(input, 'Second');
  });

  it('renders with correct id attribute', () => {
    render(TextInput, {
      props: {
        id: 'custom-id',
        label: 'Test Label',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.id).toBe('custom-id');
  });

  it('handles long text input', async () => {
    const user = userEvent.setup();
    const longText = 'a'.repeat(1000);
    render(TextInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: '',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, longText);

    expect(input.value).toBe(longText);
  });
});
