import React, { useState, useRef } from 'react';
import type { EChartsOption } from 'echarts';
import { useDashboard } from '../hooks/useDashboard';
import { useGeo } from '../hooks/useGeo';
import { BaseChart } from '@/components/charts/BaseChart';
import { ingestionClient } from '@/features/dataset/api/ingestionClient';
import { useTenantStore } from '@/store/tenantStore';

// Per-sector copy mirrored from the marketing landing page so the dashboard
// header matches each sector's identity (Retail / Service / Education / Agriculture).
const SECTOR_META: Record<string, { title: string; eyebrow: string }> = {
  retail: {
    title: 'Retail',
    eyebrow: 'Grocery chains, quick-commerce, dark stores & distributors',
  },
  service: {
    title: 'Service',
    eyebrow: 'Support centers, repair & maintenance firms, salons, agencies',
  },
  education: {
    title: 'Education',
    eyebrow: 'Schools, colleges, academies & coaching institutes',
  },
  agriculture: {
    title: 'Agriculture',
    eyebrow: 'Farms, farming cooperatives & agri-input suppliers',
  },
};

const ACCENT = '#ff682c';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, isError, refetch } = useDashboard();
  const { data: geo } = useGeo();
  const { sectorId: storeSectorId } = useTenantStore();

  const [uploadState, setUploadState] = useState<'initial' | 'uploading' | 'processing' | 'success' | 'error'>('initial');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sectorId = storeSectorId || (data?.sectorId || '').toLowerCase();
  const meta = SECTOR_META[sectorId] || {
    title: sectorId ? sectorId[0].toUpperCase() + sectorId.slice(1) : 'Dashboard',
    eyebrow: 'AI decision intelligence for your organization',
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadState('initial');
      setUploadError('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !sectorId) return;
    setUploadState('uploading');
    try {
      const response = await ingestionClient.upload(sectorId, selectedFile);
      if (response && (response.status === 'processing' || response.status === 'accepted')) {
         setUploadState('processing');
      } else {
         setUploadState('success');
      }
      refetch();
    } catch (error) {
      console.error('Upload failed', error);
      setUploadState('error');
      setUploadError('Upload failed. Please check the file and try again.');
    }
  };

  const chartOption: EChartsOption | null =
    data && data.timeseries.labels.length > 0
      ? {
          grid: { left: 44, right: 20, top: 24, bottom: 32 },
          tooltip: { trigger: 'axis' },
          legend: {
            show: data.timeseries.series.length > 1,
            top: 0,
            textStyle: { color: '#4d4d4d' },
          },
          xAxis: {
            type: 'category',
            data: data.timeseries.labels,
            axisLine: { lineStyle: { color: '#e8e8e8' } },
            axisLabel: { color: '#828282' },
          },
          yAxis: {
            type: 'value',
            splitLine: { lineStyle: { color: '#efefef' } },
            axisLabel: { color: '#828282' },
          },
          color: [ACCENT, '#816729', '#202020'],
          series: data.timeseries.series.map((s, i) => ({
            name: s.name,
            type: 'line',
            smooth: true,
            showSymbol: false,
            data: s.values,
            lineStyle: { width: 3 },
            areaStyle:
              i === 0
                ? {
                    color: {
                      type: 'linear',
                      x: 0,
                      y: 0,
                      x2: 0,
                      y2: 1,
                      colorStops: [
                        { offset: 0, color: 'rgba(255,104,44,0.22)' },
                        { offset: 1, color: 'rgba(255,104,44,0)' },
                      ],
                    },
                  }
                : undefined,
          })),
        }
      : null;

  return (
    <div className="sector-dash">
      <style dangerouslySetInnerHTML={{ __html: DASH_THEME_CSS }} />

      {/* Sector hero header — mirrors the landing sector-intro */}
      <header className="sd-hero">
        <span className="sd-bullet" />
        <div>
          <h1 className="sd-title">{meta.title}</h1>
          <p className="sd-eyebrow">{meta.eyebrow}</p>
        </div>
      </header>

      {/* Import Data Section */}
      <section className="sd-section">
        <h2 className="sd-section-title">Import Data</h2>
        <p className="sd-eyebrow" style={{ marginTop: '-12px', marginBottom: '16px' }}>
          Upload your business data to generate analytics and AI-powered insights.
        </p>
        <div className="sd-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <input
            type="file"
            accept=".csv,.xlsx,.json"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          {uploadState === 'initial' || uploadState === 'error' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <button 
                onClick={() => fileInputRef.current?.click()}
                style={{ padding: '8px 16px', background: 'var(--mist)', border: '1px solid var(--chalk)', borderRadius: '6px', cursor: 'pointer', fontWeight: 500 }}
              >
                Choose a CSV or Excel file
              </button>
              <span className="sd-note" style={{ padding: 0 }}>Supported formats: CSV and Excel (.xlsx)</span>
            </div>
          ) : null}

          {selectedFile && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 12px', background: 'var(--fog)', borderRadius: '6px', border: '1px solid var(--chalk)', width: 'fit-content' }}>
              <span style={{ fontWeight: 500, color: 'var(--carbon)' }}>{selectedFile.name}</span>
              <span style={{ fontSize: '13px', color: 'var(--slate)' }}>{(selectedFile.size / 1024).toFixed(1)} KB</span>
              {(uploadState === 'initial' || uploadState === 'error') && (
                <button 
                  onClick={() => { setSelectedFile(null); setUploadState('initial'); }}
                  style={{ padding: '2px 6px', background: 'transparent', border: 'none', color: 'var(--signal-orange)', cursor: 'pointer', fontSize: '13px', marginLeft: '8px' }}
                >
                  Remove
                </button>
              )}
            </div>
          )}

          {uploadState === 'initial' && selectedFile && (
            <button 
              onClick={handleUpload}
              style={{ padding: '8px 20px', background: 'var(--signal-orange)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', alignSelf: 'flex-start', fontWeight: 600 }}
            >
              Upload Data
            </button>
          )}

          {uploadState === 'uploading' && (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <button disabled style={{ padding: '8px 20px', background: 'var(--chalk)', color: 'var(--slate)', border: 'none', borderRadius: '6px', cursor: 'not-allowed', fontWeight: 600 }}>
                Uploading...
              </button>
            </div>
          )}
          {uploadState === 'processing' && <p className="sd-note" style={{ color: 'var(--signal-orange)', fontWeight: 500 }}>File uploaded successfully. Your data is being processed.</p>}
          {uploadState === 'success' && <p className="sd-note" style={{ color: '#2e7d32', fontWeight: 500 }}>Data imported successfully.</p>}
          {uploadState === 'error' && <p className="sd-note sd-error" style={{ fontWeight: 500 }}>{uploadError}</p>}
        </div>
      </section>

      {isLoading && <div className="sd-note">Loading intelligence for {meta.title}…</div>}
      {isError && <div className="sd-note sd-error">Failed to load dashboard data.</div>}

      {data && (
        <>
          {/* KPIs */}
          <section className="sd-section">
            <h2 className="sd-section-title">Operating metrics</h2>
            <div className="sd-kpi-grid">
              {data.kpis.map((kpi) => (
                <div key={kpi.id} className="sd-kpi">
                  <span className="sd-kpi-accent" />
                  <p className="sd-kpi-label">{kpi.title}</p>
                  <p className="sd-kpi-value">
                    {kpi.unit === '$' ? '$' : ''}
                    {kpi.value.toLocaleString()}
                    {kpi.unit && kpi.unit !== '$' ? kpi.unit : ''}
                  </p>
                </div>
              ))}
              {data.kpis.length === 0 && <div className="sd-note">No KPIs yet for this sector.</div>}
            </div>
          </section>

          {/* Timeseries */}
          <section className="sd-section">
            <h2 className="sd-section-title">Trends over time</h2>
            <div className="sd-card">
              {chartOption ? (
                <BaseChart option={chartOption} theme="light" height="320px" />
              ) : (
                <div className="sd-note">No time-series data available.</div>
              )}
            </div>
          </section>

          {/* Geo */}
          <section className="sd-section">
            <h2 className="sd-section-title">Geographic footprint</h2>
            <div className="sd-card sd-geo">
              <span className="sd-geo-num">{geo ? geo.features.length : '—'}</span>
              <span className="sd-geo-cap">
                {geo ? `mapped location(s) across ${meta.title}` : 'Loading geographic data…'}
              </span>
            </div>
          </section>
        </>
      )}
    </div>
  );
};

// Scoped landing-sector theme for the dashboard. Local + route-mounted only,
// so it never alters the app's global Tailwind theme or the shell chrome.
const DASH_THEME_CSS = `
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Inter:wght@400;500;600&display=swap');

.sector-dash {
  --signal-orange: #ff682c;
  --carbon: #202020;
  --graphite: #4d4d4d;
  --slate: #828282;
  --fog: #f5f5f5;
  --mist: #efefef;
  --chalk: #e8e8e8;
  --paper: #ffffff;
  min-height: 100%;
  margin: -1px;
  padding: 40px clamp(20px, 4vw, 56px) 64px;
  background:
    radial-gradient(1000px 480px at 0% -10%, rgba(255,104,44,0.08), transparent 60%),
    var(--mist);
  font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
  color: var(--carbon);
}
.sd-hero { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 40px; }
.sd-bullet {
  width: 14px; height: 14px; margin-top: 12px; border-radius: 50%;
  background: var(--signal-orange);
  box-shadow: 0 0 0 6px rgba(255,104,44,0.15);
  flex-shrink: 0;
}
.sd-title {
  font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
  font-size: clamp(36px, 5vw, 56px);
  line-height: 1.02;
  letter-spacing: -1px;
  font-weight: 600;
  color: var(--carbon);
}
.sd-eyebrow { margin-top: 6px; font-size: 16px; color: var(--slate); }
.sd-section { margin-bottom: 40px; }
.sd-section-title {
  font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
  font-size: 20px; font-weight: 600; letter-spacing: -0.3px;
  color: var(--carbon); margin-bottom: 16px;
}
.sd-kpi-grid {
  display: grid; gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
.sd-kpi {
  position: relative; overflow: hidden;
  background: var(--paper);
  border: 1px solid var(--chalk);
  border-radius: 18px;
  padding: 22px 22px 24px;
  box-shadow: 0 1px 3px rgba(32,32,32,0.04), 0 4px 16px rgba(32,32,32,0.04);
}
.sd-kpi-accent { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--signal-orange); }
.sd-kpi-label { font-size: 13px; font-weight: 500; color: var(--slate); text-transform: uppercase; letter-spacing: 0.4px; }
.sd-kpi-value {
  margin-top: 10px;
  font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
  font-size: 34px; font-weight: 600; letter-spacing: -0.8px; color: var(--carbon);
}
.sd-card {
  background: var(--paper);
  border: 1px solid var(--chalk);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(32,32,32,0.04), 0 4px 16px rgba(32,32,32,0.04);
}
.sd-geo { display: flex; align-items: baseline; gap: 14px; }
.sd-geo-num {
  font-family: 'DM Sans', ui-sans-serif, system-ui, sans-serif;
  font-size: 44px; font-weight: 600; letter-spacing: -1px; color: var(--signal-orange);
}
.sd-geo-cap { font-size: 15px; color: var(--graphite); }
.sd-note { color: var(--slate); font-size: 15px; padding: 8px 0; }
.sd-error { color: var(--signal-orange); }
`;
