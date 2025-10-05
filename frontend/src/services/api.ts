import { ENDPOINT_API_V1 } from '../constants/endpoint/endpointApi';
import {
  ENDPOINT_LOGIN,
  ENDPOINT_ME,
  ENDPOINT_REGISTER,
} from '../constants/endpoint/endpointUser';
import getUrlsBase from '../utils/getUrlBase';

export interface StandardErrorResponse {
  success: false;
  error: string;
  details: Array<{
    field?: string;
    message: string;
    code?: string;
  }>;
  status_code: number;
  timestamp?: string;
}

export interface StandardSuccessResponse<T = any> {
  success: true;
  message: string;
  data?: T;
  timestamp?: string;
}

export type ApiResponse<T = any> =
  | StandardSuccessResponse<T>
  | StandardErrorResponse;

export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly details: StandardErrorResponse['details'];
  public readonly isApiError = true;

  constructor(errorResponse: StandardErrorResponse) {
    super(errorResponse.error);
    this.statusCode = errorResponse.status_code;
    this.details = errorResponse.details;
    this.name = 'ApiError';
  }

  getFormattedMessage(): string {
    if (this.details.length === 0) {
      return this.message;
    }

    const fieldErrors = this.details
      .filter((detail) => detail.field)
      .map((detail) => `${detail.field}: ${detail.message}`);

    const generalErrors = this.details
      .filter((detail) => !detail.field)
      .map((detail) => detail.message);

    const allErrors = [...fieldErrors, ...generalErrors];
    return allErrors.length > 0 ? allErrors.join(', ') : this.message;
  }
}

class ApiService {
  private baseUrl: string;

  constructor() {
    const finalBase = getUrlsBase();
    this.baseUrl = `${finalBase.replace(/\/+$/, '')}${ENDPOINT_API_V1}`;
  }

  private async handleResponse<T = any>(response: Response): Promise<T> {
    const contentType = response.headers.get('Content-Type');

    if (!contentType?.includes('application/json')) {
      throw new Error(
        `Réponse non-JSON reçue: ${response.status} ${response.statusText}`
      );
    }

    const data: ApiResponse<T> = await response.json();

    if (!response.ok) {
      if ('success' in data && !data.success) {
        throw new ApiError(data);
      }

      throw new ApiError({
        success: false,
        error: `Erreur HTTP ${response.status}`,
        details: [{ message: response.statusText }],
        status_code: response.status,
      });
    }

    if ('success' in data && data.success) {
      return data.data || (data as T);
    }

    return data as T;
  }

  async post<T = any>(
    endpoint: string,
    body: any,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(body),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async postForm<T = any>(
    endpoint: string,
    form: FormData,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        ...options.headers,
      },
      body: form,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async get<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async put<T = any>(
    endpoint: string,
    body: any,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(body),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    return this.handleResponse<T>(response);
  }
}

export const apiService = new ApiService();

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserData {
  username: string;
  email: string;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return apiService.post<AuthResponse>(ENDPOINT_LOGIN, credentials);
  },

  async register(userData: RegisterRequest): Promise<UserData> {
    return apiService.post<UserData>(ENDPOINT_REGISTER, userData);
  },

  async me(token: string): Promise<AuthResponse> {
    return apiService.get<AuthResponse>(ENDPOINT_ME, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  async testConnection(): Promise<any> {
    return apiService.get('/health');
  },
};
