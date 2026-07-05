import React, { useEffect, useRef, useState } from 'react';
import type { ECharts, EChartsOption } from 'echarts';

interface BaseChartProps {
  option: EChartsOption;
  style?: React.CSSProperties;
  className?: string;
  theme?: 'light' | 'dark';
  height?: string;
  onEvents?: Record<string, (params: unknown) => void>;
}

export const BaseChart: React.FC<BaseChartProps> = React.memo(({ option, style, className, theme = 'dark', onEvents }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<ECharts | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    let resizeObserver: ResizeObserver;
    
    // Lazy load ECharts to fix Sprint 1 bundle size issue (>1.4MB)
    const loadECharts = async () => {
      if (!chartRef.current) return;
      
      const echarts = await import('echarts');
      
      if (!chartInstance.current) {
        chartInstance.current = echarts.init(chartRef.current, theme, {
          renderer: 'canvas',
          useDirtyRect: true, // Optimizes redrawing
        });
        
        if (onEvents) {
          Object.entries(onEvents).forEach(([eventName, handler]) => {
            chartInstance.current?.on(eventName, handler);
          });
        }
      }

      chartInstance.current.setOption(option, true);
      setIsLoaded(true);

      resizeObserver = new ResizeObserver(() => {
        chartInstance.current?.resize({
          animation: { duration: 100 }
        });
      });
      
      resizeObserver.observe(chartRef.current);
    };

    loadECharts();

    return () => {
      if (resizeObserver) resizeObserver.disconnect();
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [option, theme]);

  return (
    <div 
      style={{ width: '100%', height: '100%', minHeight: '300px', position: 'relative', ...style }} 
      className={className}
    >
      {!isLoaded && (
        <div className="h-full w-full flex items-center justify-center text-muted-foreground animate-pulse" style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          Loading Visualization Engine...
        </div>
      )}
      <div 
        ref={chartRef} 
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
});

BaseChart.displayName = 'BaseChart';
