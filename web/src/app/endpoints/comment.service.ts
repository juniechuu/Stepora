import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Comment {
    id: number;
    user_id: number;
    search_query: string;
    search_type: string;
    comment_text: string;
    parent_id: number | null;
    created_at: string;
    updated_at: string;
    username: string;
    profile_picture?: string;
    replies?: Comment[];
}

@Injectable({
    providedIn: 'root',
})
export class CommentService {
    private baseUrl = 'http://127.0.0.1:5000/api/comments';

    constructor(private http: HttpClient) {}

    private getAuthHeaders(): HttpHeaders {
        const token = localStorage.getItem('session_token');
        return new HttpHeaders({
            Authorization: `Bearer ${token}`,
        });
    }

    addComment(
        searchQuery: string,
        searchType: string,
        commentText: string,
        parentId?: number,
    ): Observable<any> {
        return this.http.post(
            `${this.baseUrl}/`,
            {
                search_query: searchQuery,
                search_type: searchType,
                comment_text: commentText,
                parent_id: parentId,
            },
            { headers: this.getAuthHeaders() },
        );
    }

    getComments(
        searchQuery: string,
        searchType: string,
        limit: number = 100,
    ): Observable<{ comments: Comment[] }> {
        return this.http.get<{ comments: Comment[] }>(
            `${this.baseUrl}/${searchType}/${encodeURIComponent(searchQuery)}?limit=${limit}`,
        );
    }

    updateComment(commentId: number, commentText: string): Observable<any> {
        return this.http.put(
            `${this.baseUrl}/${commentId}`,
            {
                comment_text: commentText,
            },
            { headers: this.getAuthHeaders() },
        );
    }

    deleteComment(commentId: number): Observable<any> {
        return this.http.delete(`${this.baseUrl}/${commentId}`, {
            headers: this.getAuthHeaders(),
        });
    }

    getCommentCount(searchQuery: string, searchType: string): Observable<{ count: number }> {
        return this.http.get<{ count: number }>(
            `${this.baseUrl}/count/${searchType}/${encodeURIComponent(searchQuery)}`,
        );
    }

    // Helper to organize comments into threads
    organizeComments(comments: Comment[]): Comment[] {
        const commentMap = new Map<number, Comment>();
        const rootComments: Comment[] = [];

        // First pass: create map of all comments
        comments.forEach((comment) => {
            commentMap.set(comment.id, { ...comment, replies: [] });
        });

        // Second pass: organize into threads
        comments.forEach((comment) => {
            const commentWithReplies = commentMap.get(comment.id)!;
            if (comment.parent_id) {
                const parent = commentMap.get(comment.parent_id);
                if (parent) {
                    parent.replies!.push(commentWithReplies);
                }
            } else {
                rootComments.push(commentWithReplies);
            }
        });

        return rootComments;
    }
}
