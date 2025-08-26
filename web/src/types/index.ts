// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'mod' | 'user';
  created_at: string;
}

// Document types
export interface Tag {
  id: number;
  name: string;
  slug: string;
  description: string;
  created_at: string;
}

export interface DocumentText {
  extracted_text: string;
  extraction_method: string;
  extraction_confidence: number | null;
  word_count: number;
  preview: string;
}

export interface Document {
  id: number;
  title: string;
  slug: string;
  description: string;
  file_url: string;
  mime_type: string;
  file_size: number;
  file_extension: string;
  sha256_hash: string;
  
  // FOIA specific fields
  request_id: string;
  agency_office: string;
  release_date: string | null;
  exemptions_applied: string[];
  redaction_notes: string;
  source_link: string;
  record_date_start: string | null;
  record_date_end: string | null;
  
  // Relationships
  tags: Tag[];
  uploaded_by: string;
  text_content?: DocumentText;
  
  // Metadata
  created_at: string;
  updated_at: string;
  is_pdf: boolean;
  is_text_extractable: boolean;
}

// Search types
export interface SearchResult {
  id: number;
  title: string;
  description: string;
  slug: string;
  agency_office: string;
  tags: string[];
  mime_type: string;
  file_size: number;
  release_date: string | null;
  created_at: string;
  file_extension: string;
  _formatted?: {
    title?: string;
    description?: string;
    extracted_text?: string;
  };
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  limit: number;
  offset: number;
  processing_time: number;
  facets?: {
    agency_office: Record<string, number>;
    tags: Record<string, number>;
    mime_type: Record<string, number>;
    file_extension: Record<string, number>;
  };
  error?: string;
}

export interface SearchParams {
  q?: string;
  agency_office?: string;
  tags?: string;
  mime_type?: string;
  release_date_from?: string;
  release_date_to?: string;
  record_date_from?: string;
  record_date_to?: string;
  sort?: string;
  limit?: number;
  offset?: number;
  facets?: boolean;
}

// Analytics types
export interface AnalyticsSummary {
  period_days: number;
  start_date: string;
  end_date: string;
  total_views: number;
  total_searches: number;
  total_downloads: number;
  total_uploads: number;
  unique_users: number;
  avg_search_results: number;
  top_searches: Array<{ query: string; count: number }>;
  top_documents: Array<{
    document__title: string;
    document__slug: string;
    views: number;
  }>;
  top_downloads: Array<{
    document__title: string;
    document__slug: string;
    downloads: number;
  }>;
}

export interface DailyStats {
  daily_views: Array<{ date: string; count: number }>;
  daily_searches: Array<{ date: string; count: number }>;
  daily_downloads: Array<{ date: string; count: number }>;
  start_date: string;
  end_date: string;
}

// Form types
export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export interface DocumentUploadForm {
  title: string;
  description?: string;
  file: File;
  request_id?: string;
  agency_office?: string;
  release_date?: string;
  exemptions_applied?: string[];
  redaction_notes?: string;
  source_link?: string;
  record_date_start?: string;
  record_date_end?: string;
  tag_ids?: number[];
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// UI State types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface FilterState {
  agency_office?: string;
  tags?: string[];
  mime_type?: string;
  release_date_from?: string;
  release_date_to?: string;
  record_date_from?: string;
  record_date_to?: string;
}

// Navigation types
export interface NavItem {
  name: string;
  href: string;
  icon?: React.ComponentType<any>;
  requiresAuth?: boolean;
  requiredRole?: User['role'];
}