import axios from "axios";
import type { QueryResult } from "@/lib/types";

export interface ApiClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export class RealEstateApiClientAxios {
  private axios;

  constructor(config: ApiClientConfig = {}) {
    this.axios = axios.create({
      baseURL:
        config.baseUrl ||
        process.env.NEXT_PUBLIC_API_URL ||
        "https://realtors-practice-api.onrender.com/api",
      timeout: config.timeout || 120000,
      headers: {
        "Content-Type": "application/json",
        ...config.headers,
      },
    });
    if (config.apiKey) {
      this.axios.defaults.headers.common["X-API-Key"] = config.apiKey;
    }
  }

  async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const response = await this.axios.request<T>({
      url: endpoint,
      method,
      data,
      params,
    });
    return response.data;
  }

  // Example endpoint
  async getProperties(params?: Record<string, any>) {
    return this.request<QueryResult>("GET", "/data/master", undefined, params);
  }
  // Add other endpoints as needed, following the pattern above
}

export const apiClientAxios = new RealEstateApiClientAxios();
