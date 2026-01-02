import { Component, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AiService } from '../../../../endpoints/ai.service';
import { DashboardService } from '../../../../endpoints/dashboard.service';
import { AuthService } from '../../../../endpoints/auth.service';
import { CacheService } from '../../../../endpoints/cache.service';
import { CommentService, Comment } from '../../../../endpoints/comment.service';
import { Router } from '@angular/router';

interface PresetQuestion {
    question: string;
    icon: string;
    color: string;
}

@Component({
    selector: 'app-toddler',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './toddler.html',
    styleUrls: ['./toddler.scss', './experimental-modal.scss'],
})
export class Toddler {
    private aiService = inject(AiService);
    private dashboardService = inject(DashboardService);
    public authService = inject(AuthService);
    private cacheService = inject(CacheService);
    private commentService = inject(CommentService);
    private router = inject(Router);

    fromCache: boolean = false;

    // Comment section
    comments: Comment[] = [];
    newComment: string = '';
    replyingTo: number | null = null;
    replyText: string = '';
    isLoadingComments: boolean = false;

    searchQuery: string = '';
    isLoading: boolean = false;
    error: string = '';
    experimentalMode: boolean = false;

    // Modal state
    showModal: boolean = false;
    modalQuestion: string = '';
    steps: string[] = [];
    currentStep: number = 0;

    // Suggestion state
    showSuggestions: boolean = false;
    suggestions: string[] = [];
    isLoadingSuggestions: boolean = false;

    presetQuestions: PresetQuestion[] = [
        {
            question: 'How to draw a cat?',
            icon: '/icons/cat-orange.svg',
            color: '#ff9a3c',
        },
        {
            question: 'How to take care of a fish?',
            icon: '/icons/clownfish.svg',
            color: '#4ecdc4',
        },
        {
            question: 'How to make a paper airplane?',
            icon: '/icons/plane.svg',
            color: '#667eea',
        },
        {
            question: 'How to grow a plant?',
            icon: '/icons/apple-tree.svg',
            color: '#10b981',
        },
        {
            question: 'How to make cookies?',
            icon: '/icons/cookie.svg',
            color: '#f59e0b',
        },
        {
            question: 'How to build a snowman?',
            icon: '/icons/snowman.svg',
            color: '#60a5fa',
        },
    ];

    askQuestion(question: string): void {
        if (!question.trim()) {
            this.error = 'Please enter a question';
            return;
        }

        // Business logic: Show suggestions for short queries
        const wordCount = question.trim().split(/\s+/).length;
        if (wordCount <= 3) {
            this.generateSuggestions(question);
            return;
        }

        this.isLoading = true;
        this.error = '';
        this.showSuggestions = false;
        this.fromCache = false;

        // Check cache first
        this.cacheService.checkCache(question, 'toddler', 0.85).subscribe({
            next: (cacheResponse) => {
                if (cacheResponse.cached && cacheResponse.response) {
                    // Use cached response
                    console.log(
                        'Using cached response (similarity:',
                        cacheResponse.similarity,
                        ')',
                    );
                    this.isLoading = false;
                    this.fromCache = true;
                    this.steps = cacheResponse.response.steps || [];
                    this.modalQuestion = question;
                    this.currentStep = 0;
                    this.showModal = true;

                    // Load comments
                    this.loadComments();

                    // Track search in history
                    if (this.authService.isLoggedIn()) {
                        this.dashboardService
                            .addSearchHistory(question, 'toddler-cached', this.steps.length)
                            .subscribe({
                                error: (err) =>
                                    console.error('Failed to save search history:', err),
                            });
                    }
                } else {
                    // Cache miss - call OpenAI
                    this.fetchFromAPI(question);
                }
            },
            error: (err) => {
                console.error('Cache check error, falling back to API:', err);
                this.fetchFromAPI(question);
            },
        });
    }

    private fetchFromAPI(question: string): void {
        this.aiService.sendPromptToOpenAI(question).subscribe({
            next: (response) => {
                console.log('Response from OpenAI:', response);
                this.isLoading = false;

                // Parse response into steps
                const responseText = response.response || 'No response received';
                this.steps = this.parseSteps(responseText);
                this.modalQuestion = question;
                this.currentStep = 0;
                this.showModal = true;

                // Load comments
                this.loadComments();

                // Cache the result
                this.cacheService.storeCache(question, 'toddler', { steps: this.steps }).subscribe({
                    next: () => console.log('Response cached successfully'),
                    error: (err) => console.error('Failed to cache response:', err),
                });

                // Track search in history if user is logged in
                if (this.authService.isLoggedIn()) {
                    this.dashboardService
                        .addSearchHistory(question, 'toddler', this.steps.length)
                        .subscribe({
                            error: (err) => console.error('Failed to save search history:', err),
                        });
                }
            },
            error: (error) => {
                console.error('Error calling OpenAI:', error);
                this.error =
                    error.error?.error || 'An error occurred while processing your request';
                this.isLoading = false;
            },
        });
    }

    parseSteps(response: string): string[] {
        // Remove common intro phrases
        let cleanedResponse = response
            .replace(
                /^(To .+?, follow these steps?:|Here are the steps?:|Follow these steps?:)\s*/i,
                '',
            )
            .replace(/^(Here's how to .+?:|Here's how you .+?:|Let me show you how .+?:)\s*/i, '')
            .trim();

        // Split by numbered steps or newlines
        let steps: string[] = [];

        // Try to split by numbered list
        const numberedSteps = cleanedResponse.split(/\n(?=\d+\.\s+)/);
        if (numberedSteps.length > 1) {
            // Remove the numbering from each step
            steps = numberedSteps
                .map((step) => step.replace(/^\d+\.\s+/, '').trim())
                .filter((step) => step.length > 0);
        } else {
            // Try to split by "Step X:"
            const namedSteps = cleanedResponse.split(/\n(?=Step\s+\d+:)/i);
            if (namedSteps.length > 1) {
                // Remove "Step X:" prefix
                steps = namedSteps
                    .map((step) => step.replace(/^Step\s+\d+:\s*/i, '').trim())
                    .filter((step) => step.length > 0);
            } else {
                // Fall back to splitting by double newlines or sentences
                steps = cleanedResponse.split(/\n\n+/).filter((step) => step.trim().length > 0);
                if (steps.length === 1) {
                    // If still one block, split by newlines
                    steps = cleanedResponse.split(/\n/).filter((step) => step.trim().length > 0);
                }
            }
        }

        return steps.length > 0 ? steps : [cleanedResponse];
    }

    closeModal(): void {
        this.showModal = false;
        this.steps = [];
        this.currentStep = 0;
        this.modalQuestion = '';
        this.comments = [];
        this.newComment = '';
        this.replyingTo = null;
        this.replyText = '';
    }

    loadComments(): void {
        if (!this.modalQuestion) return;

        this.isLoadingComments = true;
        this.commentService.getComments(this.modalQuestion, 'toddler').subscribe({
            next: (response) => {
                this.comments = this.commentService.organizeComments(response.comments);
                this.isLoadingComments = false;
            },
            error: (error) => {
                console.error('Error loading comments:', error);
                this.isLoadingComments = false;
            },
        });
    }

    addComment(): void {
        if (!this.newComment.trim() || !this.authService.isLoggedIn()) return;

        this.commentService.addComment(this.modalQuestion, 'toddler', this.newComment).subscribe({
            next: (response) => {
                this.newComment = '';
                this.loadComments();
            },
            error: (error) => {
                console.error('Error adding comment:', error);
                alert('Failed to add comment. Please try again.');
            },
        });
    }

    startReply(commentId: number): void {
        this.replyingTo = commentId;
        this.replyText = '';
    }

    cancelReply(): void {
        this.replyingTo = null;
        this.replyText = '';
    }

    addReply(parentId: number): void {
        if (!this.replyText.trim() || !this.authService.isLoggedIn()) return;

        this.commentService
            .addComment(this.modalQuestion, 'toddler', this.replyText, parentId)
            .subscribe({
                next: (response) => {
                    this.replyText = '';
                    this.replyingTo = null;
                    this.loadComments();
                },
                error: (error) => {
                    console.error('Error adding reply:', error);
                    alert('Failed to add reply. Please try again.');
                },
            });
    }

    deleteComment(commentId: number): void {
        if (!confirm('Are you sure you want to delete this comment?')) return;

        this.commentService.deleteComment(commentId).subscribe({
            next: () => {
                this.loadComments();
            },
            error: (error) => {
                console.error('Error deleting comment:', error);
                alert('Failed to delete comment.');
            },
        });
    }

    isCommentOwner(comment: Comment): boolean {
        const currentUser = this.authService.getCurrentUserValue();
        return currentUser ? currentUser.id === comment.user_id : false;
    }

    generateSuggestions(shortQuery: string): void {
        this.isLoadingSuggestions = true;
        this.showSuggestions = true;
        this.error = '';
        this.suggestions = [];

        const prompt = `A kid is searching for "${shortQuery}". Generate 4 complete, kid-friendly "How to" questions that they might be looking for. Make them simple and fun for children.

Format: Return ONLY 4 questions, one per line, starting with "How to". No numbering, no extra text.`;

        this.aiService.sendPromptToOpenAI(prompt).subscribe({
            next: (response) => {
                this.isLoadingSuggestions = false;
                const lines = response.response
                    .split('\n')
                    .filter((line: string) => line.trim().length > 0);
                this.suggestions = lines
                    .slice(0, 4)
                    .map((line: string) => line.replace(/^\d+\.\s*/, '').trim());
            },
            error: (error) => {
                console.error('Error generating suggestions:', error);
                this.isLoadingSuggestions = false;
                this.error = 'Could not generate suggestions. Please try a longer question!';
                this.showSuggestions = false;
            },
        });
    }

    selectSuggestion(suggestion: string): void {
        this.searchQuery = suggestion;
        this.showSuggestions = false;
        this.askQuestion(suggestion);
    }

    closeSuggestions(): void {
        this.showSuggestions = false;
        this.suggestions = [];
    }

    nextStep(): void {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;
        }
    }

    prevStep(): void {
        if (this.currentStep > 0) {
            this.currentStep--;
        }
    }

    handleSearch(): void {
        this.askQuestion(this.searchQuery);
    }

    handlePresetClick(question: string): void {
        this.searchQuery = question;
        this.askQuestion(question);
    }

    toggleExperimentalMode(): void {
        this.experimentalMode = !this.experimentalMode;
        console.log('Experimental mode:', this.experimentalMode ? 'ON' : 'OFF');
    }

    handleKeyPress(event: KeyboardEvent): void {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.handleSearch();
        }
    }

    @HostListener('window:keydown', ['$event'])
    handleModalKeyPress(event: KeyboardEvent): void {
        if (!this.showModal) return;

        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            this.prevStep();
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            this.nextStep();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            this.closeModal();
        }
    }
}
