import { api } from './api'

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  business_name: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserProfile {
  id: string
  email: string
  full_name: string
  role: string
  tenant_id: string | null
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const params = new URLSearchParams()
  params.append('username', credentials.username)
  params.append('password', credentials.password)
  const response = await api.post<AuthResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}

export async function register(data: RegisterData): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/register', data)
  return response.data
}

export async function getMe(): Promise<UserProfile> {
  const response = await api.get<UserProfile>('/auth/me')
  return response.data
}
