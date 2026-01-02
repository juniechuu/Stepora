import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Rating {
  id: number;
  user_id: number;
  item_type: string;
  item_id: string;
  rating: number;
  review?: string;
  created_at: string;
}

export interface RatingStats {
  average_rating: number;
  total_ratings: number;
  user_rating?: number;
}

@Injectable({
  providedIn: 'root'
})
export class RatingService {
  private baseUrl = 'http://127.0.0.1:5000/api/dashboard';

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('session_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  addRating(itemType: string, itemId: string, rating: number, review?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/ratings`, {
      item_type: itemType,
      item_id: itemId,
      rating: rating,
      review: review
    }, { headers: this.getAuthHeaders() });
  }

  getUserRatings(limit: number = 50): Observable<{ ratings: Rating[] }> {
    return this.http.get<{ ratings: Rating[] }>(
      `${this.baseUrl}/ratings?limit=${limit}`,
      { headers: this.getAuthHeaders() }
    );
  }

  // Get user's specific rating for an item (we'll filter client-side)
  getUserRatingForItem(itemType: string, itemId: string): Observable<Rating | null> {
    return new Observable(observer => {
      this.getUserRatings().subscribe({
        next: (response) => {
          const rating = response.ratings.find(
            r => r.item_type === itemType && r.item_id === itemId
          );
          observer.next(rating || null);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Get aggregate rating statistics for a specific item
  getItemRatingStats(itemType: string, itemId: string): Observable<RatingStats> {
    return this.http.get<RatingStats>(
      `${this.baseUrl}/ratings/${itemType}/${encodeURIComponent(itemId)}/stats`
    );
  }
}
