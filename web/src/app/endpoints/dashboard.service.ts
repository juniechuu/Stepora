import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  profile_picture?: string;
  created_at: string;
  last_login?: string;
}

export interface DashboardStats {
  total_searches: number;
  total_ratings: number;
  average_rating: number;
  recent_searches: number;
}

export interface SearchHistory {
  id: number;
  search_query: string;
  search_type?: string;
  result_count: number;
  created_at: string;
}

export interface UserRating {
  id: number;
  item_type: string;
  item_id: string;
  rating: number;
  review?: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private baseUrl = 'http://127.0.0.1:5000/api/dashboard';

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('session_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  getUserProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.baseUrl}/profile`, {
      headers: this.getAuthHeaders()
    });
  }

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/stats`, {
      headers: this.getAuthHeaders()
    });
  }

  getSearchHistory(limit: number = 50): Observable<{ history: SearchHistory[] }> {
    return this.http.get<{ history: SearchHistory[] }>(
      `${this.baseUrl}/search-history?limit=${limit}`,
      { headers: this.getAuthHeaders() }
    );
  }

  addSearchHistory(searchQuery: string, searchType: string = 'general', resultCount: number = 0): Observable<any> {
    return this.http.post(`${this.baseUrl}/search-history`, {
      search_query: searchQuery,
      search_type: searchType,
      result_count: resultCount
    }, { headers: this.getAuthHeaders() });
  }

  getUserRatings(limit: number = 50): Observable<{ ratings: UserRating[] }> {
    return this.http.get<{ ratings: UserRating[] }>(
      `${this.baseUrl}/ratings?limit=${limit}`,
      { headers: this.getAuthHeaders() }
    );
  }

  addRating(itemType: string, itemId: string, rating: number, review?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/ratings`, {
      item_type: itemType,
      item_id: itemId,
      rating: rating,
      review: review
    }, { headers: this.getAuthHeaders() });
  }

  uploadProfilePicture(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('session_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.post(`${this.baseUrl}/profile-picture/upload`, formData, {
      headers: headers
    });
  }

  updateProfilePicture(pictureUrl: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/profile-picture`, {
      picture_url: pictureUrl
    }, { headers: this.getAuthHeaders() });
  }

  removeProfilePicture(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/profile-picture`, {
      headers: this.getAuthHeaders()
    });
  }

  getTopRatedArticles(limit: number = 100): Observable<{ articles: any[] }> {
    return this.http.get<{ articles: any[] }>(
      `${this.baseUrl}/ratings/top-articles?limit=${limit}`
    );
  }
}
