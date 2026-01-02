import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CacheCheckResponse {
    cached: boolean;
    query?: string;
    response?: any;
    similarity?: number;
    hit_count?: number;
}

export interface CacheStats {
    total_cached: number;
    total_hits: number;
    by_type: Array<{
        search_type: string;
        count_by_type: number;
    }>;
}

@Injectable({
    providedIn: 'root',
})
export class CacheService {
    private baseUrl = 'http://127.0.0.1:5000/api/cache';

    constructor(private http: HttpClient) {}

    checkCache(
        query: string,
        searchType: string,
        similarityThreshold: number = 0.85,
    ): Observable<CacheCheckResponse> {
        return this.http.post<CacheCheckResponse>(`${this.baseUrl}/check`, {
            query,
            search_type: searchType,
            similarity_threshold: similarityThreshold,
        });
    }

    storeCache(query: string, searchType: string, responseData: any): Observable<any> {
        return this.http.post(`${this.baseUrl}/store`, {
            query,
            search_type: searchType,
            response_data: responseData,
        });
    }

    getCacheStats(): Observable<CacheStats> {
        return this.http.get<CacheStats>(`${this.baseUrl}/stats`);
    }
}
