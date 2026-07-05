import { render } from '@/utils/test-utils';
import { BaseChart } from '../BaseChart';
import { describe, it, expect, vi } from 'vitest';
import type { EChartsOption } from 'echarts';

// Mock ECharts to prevent "Initialize failed: invalid dom" in JSDOM
vi.mock('echarts', () => ({
  init: () => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
  })
}));

describe('BaseChart Visualization Lifecycle (T7)', () => {
  const mockOption: EChartsOption = {
    title: { text: 'Test Chart' },
    series: [{ type: 'bar' as const, data: [1, 2, 3] }]
  };

  it('renders loading state before dynamic import resolves', () => {
    const { getByText } = render(<BaseChart option={mockOption} />);
    expect(getByText('Loading Visualization Engine...')).toBeInTheDocument();
  });

  it('mounts and unmounts without crashing (Lifecycle check)', () => {
    const { unmount } = render(<BaseChart option={mockOption} />);
    expect(() => unmount()).not.toThrow();
  });
});
