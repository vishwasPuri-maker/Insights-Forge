import { render } from '@/utils/test-utils';
import { axe } from 'jest-axe';
import { describe, it, expect } from 'vitest';
import { KPIWidget } from '../dashboard/KPIWidget';
import { AINativeCard } from '../ai/AINativeCard';
import { IntelligencePanel } from '../ai/IntelligencePanel';
import { ExecutiveTable } from '../tables/ExecutiveTable';

describe('Enterprise Components (T3 & T6)', () => {
  it('KPIWidget renders and has no a11y violations', async () => {
    const { container, getByText } = render(
      <KPIWidget 
        title="Total Revenue" 
        value="$1,200,000" 
        trend={{ value: 5.2, direction: 'up', label: 'vs last month' }} 
      />
    );
    expect(getByText('Total Revenue')).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('AINativeCard renders and has no a11y violations', async () => {
    const { container, getByText } = render(
      <AINativeCard 
        title="AI Insight" 
        confidenceScore={95} 
        type="Prediction" 
        description="Test description"
      >
        Model output here.
      </AINativeCard>
    );
    expect(getByText('AI Insight')).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('IntelligencePanel renders structural boundaries and has no a11y violations', async () => {
    const { container } = render(<IntelligencePanel />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('ExecutiveTable renders empty state', async () => {
    const { getByText } = render(<ExecutiveTable data={[]} columns={[]} />);
    expect(getByText('No data points available.')).toBeInTheDocument();
  });
});
