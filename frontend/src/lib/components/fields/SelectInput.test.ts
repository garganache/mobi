import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import SelectInput from './SelectInput.svelte';

describe('SelectInput', () => {
  const testOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
  ];

  it('renders with correct label', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
      },
    });

    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('renders all options', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
      },
    });

    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
    expect(screen.getByText('Option 3')).toBeInTheDocument();
  });

  it('renders placeholder option', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        placeholder: 'Choose an option',
      },
    });

    expect(screen.getByText('Choose an option')).toBeInTheDocument();
  });

  it('displays initial value', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        value: 'option2',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select.value).toBe('option2');
  });

  it('updates value on user selection', async () => {
    const user = userEvent.setup();
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    await user.selectOptions(select, 'option2');

    expect(select.value).toBe('option2');
  });

  it('handles empty value', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select.value).toBe('');
  });

  it('shows validation error when provided', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        error: 'Please select an option',
      },
    });

    expect(screen.getByText('Please select an option')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('applies correct ARIA attributes', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select).toHaveAttribute('aria-label', 'Test Label');
    expect(select).toHaveAttribute('aria-invalid', 'false');
  });

  it('applies correct ARIA attributes when error is present', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        error: 'Error message',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select).toHaveAttribute('aria-invalid', 'true');
    expect(select).toHaveAttribute('aria-describedby', 'test-select-error');
  });

  it('applies error class when error is present', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        error: 'Error message',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select.classList.contains('error')).toBe(true);
  });

  it('renders with correct id attribute', () => {
    render(SelectInput, {
      props: {
        id: 'custom-id',
        label: 'Test Label',
        options: testOptions,
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    expect(select.id).toBe('custom-id');
  });

  it('handles empty options array', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: [],
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    // Should only have placeholder option
    expect(select.options.length).toBe(1);
  });

  it('handles changing selection multiple times', async () => {
    const user = userEvent.setup();
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;

    await user.selectOptions(select, 'option1');

    await user.selectOptions(select, 'option3');

    await user.selectOptions(select, 'option2');
  });

  it('handles options with special characters in labels', () => {
    const specialOptions = [
      { value: 'opt1', label: 'Option & Special' },
      { value: 'opt2', label: 'Option <with> tags' },
      { value: 'opt3', label: 'Option "quotes"' },
    ];

    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: specialOptions,
      },
    });

    expect(screen.getByText('Option & Special')).toBeInTheDocument();
    expect(screen.getByText('Option <with> tags')).toBeInTheDocument();
    expect(screen.getByText('Option "quotes"')).toBeInTheDocument();
  });

  it('handles options with special characters in values', async () => {
    const user = userEvent.setup();
    const specialOptions = [
      { value: 'value-with-dash', label: 'Option 1' },
      { value: 'value_with_underscore', label: 'Option 2' },
      { value: 'value.with.dots', label: 'Option 3' },
    ];

    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: specialOptions,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    await user.selectOptions(select, 'value-with-dash');

  });

  it('placeholder option is disabled', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
        placeholder: 'Select one',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    const placeholderOption = select.options[0];
    expect(placeholderOption.disabled).toBe(true);
  });

  it('renders with default placeholder when not provided', () => {
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: testOptions,
      },
    });

    expect(screen.getByText('Select an option')).toBeInTheDocument();
  });

  it('handles single option', async () => {
    const user = userEvent.setup();
    const singleOption = [{ value: 'only-option', label: 'Only Option' }];
    render(SelectInput, {
      props: {
        id: 'test-select',
        label: 'Test Label',
        options: singleOption,
        value: '',
      },
    });

    const select = screen.getByLabelText('Test Label') as HTMLSelectElement;
    await user.selectOptions(select, 'only-option');

  });
});
