import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  profile_picture?: string;
}

export interface AuthResponse {
  message: string;
  session_token?: string;
  user?: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = 'http://127.0.0.1:5000/api/auth';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Check if user is already logged in on service initialization
    this.checkExistingSession();
  }

  private checkExistingSession(): void {
    const token = this.getToken();
    if (token) {
      this.verifyToken().subscribe({
        next: (response: any) => {
          if (response.valid) {
            this.currentUserSubject.next(response.user);
          } else {
            this.logout();
          }
        },
        error: () => {
          this.logout();
        }
      });
    }
  }

  register(username: string, email: string, password: string, fullName?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/register`, {
      username,
      email,
      password,
      full_name: fullName
    });
  }

  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.baseUrl}/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        if (response.session_token && response.user) {
          this.setToken(response.session_token);
          this.currentUserSubject.next(response.user);
        }
      })
    );
  }

  logout(): void {
    const token = this.getToken();
    if (token) {
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });
      this.http.post(`${this.baseUrl}/logout`, {}, { headers }).subscribe();
    }
    this.removeToken();
    this.currentUserSubject.next(null);
  }

  verifyToken(): Observable<any> {
    const token = this.getToken();
    if (!token) {
      return new Observable(observer => {
        observer.next({ valid: false });
        observer.complete();
      });
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.get(`${this.baseUrl}/verify`, { headers });
  }

  getCurrentUser(): Observable<any> {
    const token = this.getToken();
    if (!token) {
      return new Observable(observer => {
        observer.error({ error: 'No token found' });
        observer.complete();
      });
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.get(`${this.baseUrl}/me`, { headers });
  }

  isLoggedIn(): boolean {
    return !!this.getToken() && !!this.currentUserSubject.value;
  }

  getToken(): string | null {
    return localStorage.getItem('session_token');
  }

  private setToken(token: string): void {
    localStorage.setItem('session_token', token);
  }

  private removeToken(): void {
    localStorage.removeItem('session_token');
  }

  getCurrentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  updateCurrentUser(updates: Partial<User>): void {
    const currentUser = this.currentUserSubject.value;
    if (currentUser) {
      this.currentUserSubject.next({ ...currentUser, ...updates });
    }
  }
}
