// services/tmdb.ts - TMDB 元数据服务层

export interface TMDBSearchResult {
  id: number;
  title?: string;
  name?: string;
  original_title?: string;
  original_name?: string;
  release_date?: string;
  first_air_date?: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
  [key: string]: any;
}

export interface TMDBDetails {
  id: number;
  title?: string;
  name?: string;
  tagline?: string;
  overview?: string;
  genres?: Array<{ id: number; name: string }>;
  release_date?: string;
  first_air_date?: string;
  runtime?: number;
  episode_run_time?: number[];
  [key: string]: any;
}

export interface TMDBIdentifyResult {
  candidates: TMDBSearchResult[];
  ai_choice?: TMDBSearchResult | null;
}

export const tmdbService = {
  /**
   * 搜索影视作品
   * @param query 搜索关键词
   * @param type 类型（'movie' 或 'tv'）
   * @param year 年份（可选）
   */
  async search(
    query: string,
    type: 'movie' | 'tv' = 'movie',
    year?: number
  ): Promise<TMDBSearchResult[]> {
    const formData = new FormData();
    formData.append('q', query);
    formData.append('typ', type);
    if (year) {
      formData.append('year', year.toString());
    }

    const response = await fetch('/api/tmdb/search', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || 'TMDB 搜索失败');
    }

    return data.data;
  },

  /**
   * 获取影视详情
   * @param tmdbId TMDB ID
   * @param type 类型（'movie' 或 'tv'）
   */
  async getDetails(tmdbId: number, type: 'movie' | 'tv' = 'movie'): Promise<TMDBDetails> {
    const formData = new FormData();
    formData.append('tmdb_id', tmdbId.toString());
    formData.append('typ', type);

    const response = await fetch('/api/tmdb/details', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || '获取 TMDB 详情失败');
    }

    return data.data;
  },

  /**
   * AI 辅助识别影视作品
   * @param name 影视名称
   * @param type 类型（'movie' 或 'tv'）
   */
  async identify(name: string, type: 'movie' | 'tv' = 'movie'): Promise<TMDBIdentifyResult> {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('typ', type);

    const response = await fetch('/api/tmdb/identify', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || 'TMDB 识别失败');
    }

    return data.data;
  },
};
