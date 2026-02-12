import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import MultiImageUpload from './MultiImageUpload.svelte';

// TODO: Update these tests for Svelte 5 event system and Romanian i18n
// Currently skipped due to Svelte 5 migration ($on no longer valid)
describe.skip('MultiImageUpload - Multi-Image Batch Upload', () => {
  it('should support multiple file selection', () => {
    render(MultiImageUpload, {
      props: {}
    });

    const fileInput = screen.getByLabelText('Multi-image upload zone').querySelector('input[type="file"]');
    expect(fileInput).toBeTruthy();
    expect(fileInput?.multiple).toBe(true);
  });

  it('should trigger batch upload when analyze button is clicked', async () => {
    const mockAnalysisComplete = vi.fn();
    const { component } = render(MultiImageUpload, {
      props: {}
    });

    component.$on('analysisComplete', mockAnalysisComplete);

    // Create mock files
    const mockFiles = [
      new File(['image1'], 'test1.jpg', { type: 'image/jpeg' }),
      new File(['image2'], 'test2.jpg', { type: 'image/jpeg' })
    ];

    // Mock the fetch API
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        synthesis: {
          total_rooms: 2,
          room_breakdown: { bedroom: 1, kitchen: 1 },
          unified_description: 'Test property with 2 rooms',
          property_overview: {
            property_type: 'apartment',
            style: 'modern',
            total_rooms: 2,
            room_breakdown: { bedroom: 1, kitchen: 1 },
            common_amenities: ['granite_counters'],
            common_materials: ['granite_counters'],
            condition: 'good'
          }
        },
        individual_analyses: [
          { description: 'Test room 1', property_type: 'bedroom', rooms: { bedroom: 1 }, amenities: ['hardwood_floors'] },
          { description: 'Test room 2', property_type: 'kitchen', rooms: { kitchen: 1 }, amenities: ['granite_counters'] }
        ]
      })
    });

    // First upload files
    const fileInput = screen.getByLabelText('Multi-image upload zone').querySelector('input[type="file"]');
    await userEvent.upload(fileInput, mockFiles);

    // Then click analyze button
    const analyzeButton = screen.getByText('Analyze 2 Images');
    await userEvent.click(analyzeButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/analyze-batch', {
        method: 'POST',
        body: expect.any(FormData)
      });
    });

    await waitFor(() => {
      expect(mockAnalysisComplete).toHaveBeenCalledWith({ 
        synthesis: expect.objectContaining({
          total_rooms: 2,
          unified_description: 'Test property with 2 rooms'
        }),
        individualAnalyses: expect.any(Array)
      });
    });
  });

  it('should display analysis progress', async () => {
    render(MultiImageUpload, {
      props: {}
    });

    // Mock the fetch API with a delay
    global.fetch = vi.fn().mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({
            synthesis: { total_rooms: 1 },
            individual_analyses: [{ description: 'Test' }]
          })
        }), 100)
      )
    );

    const mockFiles = [
      new File(['image'], 'test.jpg', { type: 'image/jpeg' })
    ];

    // Upload files
    const fileInput = screen.getByLabelText('Multi-image upload zone').querySelector('input[type="file"]');
    await userEvent.upload(fileInput, mockFiles);

    // Click analyze button
    const analyzeButton = screen.getByText('Analyze 1 Image');
    await userEvent.click(analyzeButton);

    // Check if progress is shown
    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    });
  });

  it('should display synthesis results after analysis', async () => {
    const mockAnalysisComplete = vi.fn();
    const { component } = render(MultiImageUpload, {
      props: {}
    });

    component.$on('analysisComplete', mockAnalysisComplete);

    // Mock the fetch API
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        synthesis: {
          total_rooms: 2,
          room_breakdown: { bedroom: 1, kitchen: 1 },
          unified_description: 'This apartment has 2 rooms: 1 Bedroom, 1 Kitchen. Features include granite countertops. Overall style: modern.',
          property_overview: {
            property_type: 'apartment',
            style: 'modern',
            total_rooms: 2,
            room_breakdown: { bedroom: 1, kitchen: 1 },
            common_amenities: ['granite_counters', 'hardwood_floors'],
            common_materials: ['granite_counters', 'hardwood_floors'],
            condition: 'good'
          }
        },
        individual_analyses: [
          { 
            description: 'A bedroom with hardwood floors and large windows', 
            property_type: 'bedroom', 
            rooms: { bedroom: 1 }, 
            amenities: ['hardwood_floors'],
            style: 'modern',
            materials: ['hardwood_floors'],
            condition: 'good'
          },
          { 
            description: 'A kitchen with granite countertops', 
            property_type: 'kitchen', 
            rooms: { kitchen: 1 }, 
            amenities: ['granite_counters'],
            style: 'modern',
            materials: ['granite_counters'],
            condition: 'excellent'
          }
        ]
      })
    });

    const mockFiles = [
      new File(['image1'], 'test1.jpg', { type: 'image/jpeg' }),
      new File(['image2'], 'test2.jpg', { type: 'image/jpeg' })
    ];

    // Upload and analyze
    const fileInput = screen.getByLabelText('Multi-image upload zone').querySelector('input[type="file"]');
    await userEvent.upload(fileInput, mockFiles);

    const analyzeButton = screen.getByText('Analyze 2 Images');
    await userEvent.click(analyzeButton);

    await waitFor(() => {
      expect(screen.getByText('Property Overview')).toBeInTheDocument();
      expect(screen.getByText('2 rooms')).toBeInTheDocument();
      expect(screen.getByText('This apartment has 2 rooms:')).toBeInTheDocument();
    });
  });
});