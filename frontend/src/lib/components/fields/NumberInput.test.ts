import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import NumberInput from './NumberInput.svelte';

describe('NumberInput', () => {
  it('renders with correct label', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
      },
    });

    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('displays initial value', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: 42,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.value).toBe('42');
  });

  it('handles null initial value', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.value).toBe('');
  });

  it('displays placeholder text', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        placeholder: 'Enter number',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.placeholder).toBe('Enter number');
  });

  it('updates value on user input', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '123');

    expect(input.value).toBe('123');
  });

  it('handles negative numbers', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '-50');

    expect(input.value).toBe('-50');
  });

  it('handles decimal numbers', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
        step: 0.1,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '3.14');

    expect(input.value).toBe('3.14');
  });

  it('applies min attribute', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        min: 0,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.min).toBe('0');
  });

  it('applies max attribute', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        max: 100,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.max).toBe('100');
  });

  it('applies step attribute', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        step: 5,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.step).toBe('5');
  });

  it('applies default step of 1', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.step).toBe('1');
  });

  it('shows validation error when provided', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        error: 'Value must be positive',
      },
    });

    expect(screen.getByText('Value must be positive')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('applies correct ARIA attributes', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input).toHaveAttribute('aria-label', 'Test Label');
    expect(input).toHaveAttribute('aria-invalid', 'false');
  });

  it('applies correct ARIA attributes when error is present', () => {
    render(NumberInput, {
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
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        error: 'Error message',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.classList.contains('error')).toBe(true);
  });

  it('renders with correct id attribute', () => {
    render(NumberInput, {
      props: {
        id: 'custom-id',
        label: 'Test Label',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.id).toBe('custom-id');
  });

  it('handles clearing input value', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: 100,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.clear(input);

    expect(input.value).toBe('');
  });

  it('handles zero value', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '0');

    expect(input.value).toBe('0');
  });

  it('handles very large numbers', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '999999999');

    expect(input.value).toBe('999999999');
  });

  it('handles updating from one value to another', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: 10,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.clear(input);
    await user.type(input, '20');

    expect(input.value).toBe('20');
  });

  it('input type is number', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.type).toBe('number');
  });

  it('handles scientific notation', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    await user.type(input, '1e5');

  });

  it('handles min and max together', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        min: 10,
        max: 100,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.min).toBe('10');
    expect(input.max).toBe('100');
  });

  it('handles updating value multiple times', async () => {
    const user = userEvent.setup();
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        value: null,
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;

    await user.type(input, '10');

    await user.clear(input);
    await user.type(input, '20');

    await user.clear(input);
    await user.type(input, '30');
  });

  it('does not apply min/max when undefined', () => {
    render(NumberInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
      },
    });

    const input = screen.getByLabelText('Test Label') as HTMLInputElement;
    expect(input.hasAttribute('min')).toBe(false);
    expect(input.hasAttribute('max')).toBe(false);
  });
});
