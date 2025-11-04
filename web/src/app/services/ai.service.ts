import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AiService {
	private baseUrl = 'http://127.0.0.1:5000/api';

	constructor(private http: HttpClient) {}

	sendPromptToOpenAI(prompt: string): Observable<any> {
		return this.http.post(`${this.baseUrl}/openai`, { prompt });
	}
}
