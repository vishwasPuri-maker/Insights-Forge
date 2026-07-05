// Matches GeoFeatureCollection / GeoFeature in openapi.json.
export interface GeoFeature {
  type: 'Feature';
  geometry: Record<string, unknown>;
  properties: Record<string, unknown>;
}

export interface GeoFeatureCollection {
  type: 'FeatureCollection';
  sector: string;
  features: GeoFeature[];
}
