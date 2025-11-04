// Angular
import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// Services
import { AiService } from './services/ai.service';
import { HelperService } from './services/helper.service';

@Component({
    selector: 'app-root',
    imports: [
		CommonModule,
		FormsModule
	],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {
	// Injects
	private aiService = inject(AiService);
	private helperService = inject(HelperService);

	// Variables
	prompt: string = '';
	response: string = '';
	isLoading: boolean = false;
	error: string = '';

	// Events
	ngOnInit() {
		this.helperService.getHello().subscribe({
			next: (response) => {
				console.log('Response from /hello:', response);
			},
			error: (error) => {
				console.error('Error calling /hello:', error);
			}
		});
	}

	// Support Functions
	// #region API Calls
	submitPrompt() {
		if (!this.prompt.trim()) {
			this.error = 'Please enter a prompt';
			return;
		}

		this.isLoading = true;
		this.error = '';
		this.response = '';

		this.aiService.sendPromptToOpenAI(this.prompt).subscribe({
			next: (response) => {
				console.log('Response from OpenAI:', response);
				this.response = response.status;
				this.isLoading = false;
			},
			error: (error) => {
				console.error('Error calling OpenAI:', error);
				this.error = error.error?.error || 'An error occurred while processing your request';
				this.isLoading = false;
			}
		});
	}
	// #endregion
}
