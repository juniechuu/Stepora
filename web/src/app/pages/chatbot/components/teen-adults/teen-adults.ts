import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AiService } from '../../../../endpoints/ai.service';
import { DashboardService } from '../../../../endpoints/dashboard.service';
import { AuthService } from '../../../../endpoints/auth.service';
import { CacheService } from '../../../../endpoints/cache.service';
import { CommentService, Comment } from '../../../../endpoints/comment.service';
import { RatingService } from '../../../../endpoints/rating.service';

interface Step {
    title: string;
    description: string;
    tips?: string[];
}

interface RelatedLink {
    title: string;
    url: string;
}

interface Article {
    title: string;
    introduction?: string;
    prerequisites?: string[];
    steps: Step[];
    conclusion?: string;
    relatedLinks?: RelatedLink[];
    readTime: number;
    difficulty: string;
}

@Component({
    selector: 'app-teen-adults',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './teen-adults.html',
    styleUrl: './teen-adults.scss',
})
export class TeenAdults implements OnInit {
    private aiService = inject(AiService);
    private dashboardService = inject(DashboardService);
    public authService = inject(AuthService);
    private cacheService = inject(CacheService);
    private commentService = inject(CommentService);
    private ratingService = inject(RatingService);

    searchQuery: string = '';
    article: Article | null = null;
    isLoading: boolean = false;
    error: string = '';
    experimentalMode: boolean = false;
    showSuggestions: boolean = false;
    suggestions: string[] = [];
    isLoadingSuggestions: boolean = false;
    fromCache: boolean = false;

    // Comment section
    comments: Comment[] = [];
    newComment: string = '';
    replyingTo: number | null = null;
    replyText: string = '';
    isLoadingComments: boolean = false;
    currentSearchQuery: string = '';

    // Rating section
    userRating: number = 0;
    hoveredRating: number = 0;
    isSubmittingRating: boolean = false;
    aggregateRating: number = 0;
    totalRatings: number = 0;

    ngOnInit(): void {
        // Check for pending search from leaderboard
        const pendingSearch = localStorage.getItem('teenAdultPendingSearch');
        if (pendingSearch) {
            this.searchQuery = pendingSearch;
            localStorage.removeItem('teenAdultPendingSearch');
            // Trigger search after a short delay to ensure component is fully loaded
            setTimeout(() => {
                this.searchTutorial();
            }, 100);
        }
    }

    searchTutorial(): void {
        if (!this.searchQuery.trim()) return;

        // Business logic: Validate input length for better accuracy
        const wordCount = this.searchQuery.trim().split(/\s+/).length;
        if (wordCount <= 3) {
            this.generateSuggestions(this.searchQuery.trim());
            return;
        }

        this.isLoading = true;
        this.error = '';
        this.article = null;
        this.fromCache = false;

        const searchType = this.experimentalMode ? 'wikihow' : 'teen-adult';

        // Check cache first
        this.cacheService.checkCache(this.searchQuery, searchType, 0.85).subscribe({
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
                    this.article = cacheResponse.response;
                    this.currentSearchQuery = this.searchQuery;
                    this.scrollToTop();
                    this.loadComments();
                    this.loadUserRating();
                    this.loadAggregateRating();

                    // Track search in history
                    if (this.authService.isLoggedIn() && this.article) {
                        this.dashboardService
                            .addSearchHistory(
                                this.searchQuery,
                                searchType + '-cached',
                                this.article.steps.length,
                            )
                            .subscribe({
                                error: (err) =>
                                    console.error('Failed to save search history:', err),
                            });
                    }
                } else {
                    // Cache miss - fetch from source
                    if (this.experimentalMode) {
                        this.fetchFromWikiHow();
                    } else {
                        this.fetchFromAI();
                    }
                }
            },
            error: (err) => {
                console.error('Cache check error, falling back to source:', err);
                if (this.experimentalMode) {
                    this.fetchFromWikiHow();
                } else {
                    this.fetchFromAI();
                }
            },
        });
    }

    private fetchFromWikiHow(): void {
        this.aiService.scrapeWikiHow(this.searchQuery).subscribe({
            next: (response) => {
                console.log('WikiHow scrape response:', response);
                this.isLoading = false;
                this.article = this.parseScrapedArticle(response);
                this.currentSearchQuery = this.searchQuery;
                this.scrollToTop();
                this.loadComments();
                this.loadUserRating();
                this.loadAggregateRating();

                // Cache the result
                this.cacheService.storeCache(this.searchQuery, 'wikihow', this.article).subscribe({
                    next: () => console.log('WikiHow response cached'),
                    error: (err) => console.error('Failed to cache response:', err),
                });

                // Track search in history if user is logged in
                if (this.authService.isLoggedIn()) {
                    this.dashboardService
                        .addSearchHistory(this.searchQuery, 'wikihow', this.article.steps.length)
                        .subscribe({
                            error: (err) => console.error('Failed to save search history:', err),
                        });
                }
            },
            error: (error) => {
                console.error('Error scraping WikiHow:', error);
                this.isLoading = false;
                this.error =
                    error.error?.error || 'Failed to scrape WikiHow. Try a different query.';
            },
        });
    }

    private fetchFromAI(): void {
        const prompt = `Write a comprehensive, professional how-to article about: ${this.searchQuery}. 

Format the response EXACTLY as follows:

TITLE: [Clear, descriptive title]

INTRODUCTION: [Brief introduction explaining what will be covered and why it's useful]

PREREQUISITES: [List any prerequisites, one per line, or write "None"]

STEPS:
STEP 1: [Step title]
[Detailed description]
TIPS: [Optional tips, one per line]

STEP 2: [Step title]
[Detailed description]
TIPS: [Optional tips, one per line]

[Continue for all steps...]

CONCLUSION: [Summary and final thoughts]

RELATED: [3-5 related topics or resources, one per line]`;

        this.aiService.sendPromptToOpenAI(prompt).subscribe({
            next: (response) => {
                console.log('Response from OpenAI:', response);
                this.isLoading = false;
                this.article = this.parseArticle(response.response || '', this.searchQuery);
                this.currentSearchQuery = this.searchQuery;
                this.scrollToTop();
                this.loadComments();
                this.loadUserRating();
                this.loadAggregateRating();

                // Cache the result
                this.cacheService
                    .storeCache(this.searchQuery, 'teen-adult', this.article)
                    .subscribe({
                        next: () => console.log('AI response cached'),
                        error: (err) => console.error('Failed to cache response:', err),
                    });

                // Track search in history if user is logged in
                if (this.authService.isLoggedIn()) {
                    this.dashboardService
                        .addSearchHistory(this.searchQuery, 'teen-adult', this.article.steps.length)
                        .subscribe({
                            error: (err) => console.error('Failed to save search history:', err),
                        });
                }
            },
            error: (error) => {
                console.error('Error calling OpenAI:', error);
                this.isLoading = false;
                this.error =
                    error.error?.error || 'An error occurred while processing your request';
            },
        });
    }

    parseScrapedArticle(response: any): Article {
        return {
            title: response.title || this.searchQuery,
            introduction: response.introduction,
            prerequisites: response.prerequisites || undefined,
            steps: response.steps.map((step: any) => ({
                title: step.title,
                description: step.description,
                tips: step.tips || undefined,
            })),
            conclusion: response.conclusion,
            relatedLinks: response.relatedLinks || undefined,
            readTime: response.readTime || 5,
            difficulty: response.difficulty || 'Intermediate',
        };
    }

    toggleExperimentalMode(): void {
        this.experimentalMode = !this.experimentalMode;
        console.log('Experimental mode:', this.experimentalMode ? 'ON' : 'OFF');
    }

    parseArticle(response: string, query: string): Article {
        const lines = response
            .split('\n')
            .map((line) => line.trim())
            .filter((line) => line);

        const article: Article = {
            title: query,
            steps: [],
            readTime: 5,
            difficulty: 'Intermediate',
        };

        let currentSection = '';
        let currentStep: Step | null = null;
        let currentTips: string[] = [];

        for (const line of lines) {
            if (line.startsWith('TITLE:')) {
                article.title = line.replace('TITLE:', '').trim();
            } else if (line.startsWith('INTRODUCTION:')) {
                currentSection = 'intro';
                article.introduction = line.replace('INTRODUCTION:', '').trim();
            } else if (line.startsWith('PREREQUISITES:')) {
                currentSection = 'prereq';
                article.prerequisites = [];
            } else if (line.startsWith('STEPS:')) {
                currentSection = 'steps';
            } else if (line.startsWith('CONCLUSION:')) {
                currentSection = 'conclusion';
                article.conclusion = line.replace('CONCLUSION:', '').trim();
            } else if (line.startsWith('RELATED:')) {
                currentSection = 'related';
                article.relatedLinks = [];
            } else if (line.match(/^STEP \d+:/)) {
                if (currentStep) {
                    if (currentTips.length > 0) {
                        currentStep.tips = currentTips;
                        currentTips = [];
                    }
                    article.steps.push(currentStep);
                }
                currentStep = {
                    title: line.replace(/^STEP \d+:/, '').trim(),
                    description: '',
                };
            } else if (line.startsWith('TIPS:')) {
                // Skip the TIPS: header
                continue;
            } else {
                if (currentSection === 'intro' && article.introduction) {
                    article.introduction += ' ' + line;
                } else if (
                    currentSection === 'prereq' &&
                    article.prerequisites &&
                    line !== 'None'
                ) {
                    article.prerequisites.push(line.replace(/^[-•*]\s*/, ''));
                } else if (currentSection === 'steps' && currentStep) {
                    if (line.startsWith('-') || line.startsWith('•') || line.startsWith('*')) {
                        currentTips.push(line.replace(/^[-•*]\s*/, ''));
                    } else {
                        currentStep.description += (currentStep.description ? ' ' : '') + line;
                    }
                } else if (currentSection === 'conclusion' && article.conclusion) {
                    article.conclusion += ' ' + line;
                } else if (currentSection === 'related' && article.relatedLinks) {
                    const cleanLine = line.replace(/^[-•*]\s*/, '');
                    article.relatedLinks.push({
                        title: cleanLine,
                        url: `https://www.google.com/search?q=${encodeURIComponent(cleanLine)}`,
                    });
                }
            }
        }

        // Add the last step
        if (currentStep) {
            if (currentTips.length > 0) {
                currentStep.tips = currentTips;
            }
            article.steps.push(currentStep);
        }

        // Calculate read time based on steps
        article.readTime = Math.max(3, Math.ceil(article.steps.length * 1.5));

        return article;
    }

    handleKeyPress(event: KeyboardEvent): void {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.searchTutorial();
        }
    }

    scrollToTop(): void {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    scrollToStep(index: number): void {
        const element = document.getElementById(`step-${index}`);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    generateSuggestions(shortQuery: string): void {
        this.showSuggestions = true;
        this.isLoadingSuggestions = true;
        this.suggestions = [];
        this.error = '';

        const prompt = `A user is searching for "${shortQuery}". This query is too short. Generate 4 complete, professional "How to" tutorial queries that the user might be looking for. Each should be detailed and specific (at least 4-5 words). Return ONLY the 4 queries, numbered 1-4, nothing else.`;

        this.aiService.sendPromptToOpenAI(prompt).subscribe({
            next: (response) => {
                console.log('Suggestions from OpenAI:', response);
                this.isLoadingSuggestions = false;

                const suggestionText = response.response || '';
                const lines = suggestionText.split('\n').filter((line: string) => line.trim());

                this.suggestions = lines
                    .map((line: string) => line.replace(/^\d+\.?\s*/, '').trim())
                    .filter((line: string) => line.length > 0)
                    .slice(0, 4);

                if (this.suggestions.length === 0) {
                    this.closeSuggestions();
                    this.error =
                        'Please provide more details (at least 4 words) for better accuracy.';
                }
            },
            error: (error) => {
                console.error('Error generating suggestions:', error);
                this.isLoadingSuggestions = false;
                this.closeSuggestions();
                this.error = 'Please provide more details (at least 4 words) for better accuracy.';
            },
        });
    }

    selectSuggestion(suggestion: string): void {
        this.searchQuery = suggestion;
        this.closeSuggestions();
        this.searchTutorial();
    }

    closeSuggestions(): void {
        this.showSuggestions = false;
        this.suggestions = [];
        this.isLoadingSuggestions = false;
    }

    // Comment methods
    loadComments(): void {
        if (!this.currentSearchQuery) return;

        this.isLoadingComments = true;
        this.commentService.getComments(this.currentSearchQuery, 'teen-adult').subscribe({
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
        if (!this.newComment.trim() || !this.authService.isLoggedIn() || !this.currentSearchQuery)
            return;

        this.commentService
            .addComment(this.currentSearchQuery, 'teen-adult', this.newComment)
            .subscribe({
                next: (response) => {
                    this.newComment = '';
                    this.loadComments();
                },
                error: (error) => {
                    console.error('Error adding comment:', error);
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
        if (!this.replyText.trim() || !this.authService.isLoggedIn() || !this.currentSearchQuery)
            return;

        this.commentService
            .addComment(this.currentSearchQuery, 'teen-adult', this.replyText, parentId)
            .subscribe({
                next: (response) => {
                    this.replyText = '';
                    this.replyingTo = null;
                    this.loadComments();
                },
                error: (error) => {
                    console.error('Error adding reply:', error);
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
            },
        });
    }

    isCommentOwner(comment: Comment): boolean {
        const currentUser = this.authService.getCurrentUserValue();
        return currentUser ? comment.user_id === currentUser.id : false;
    }

    // Rating methods
    loadUserRating(): void {
        if (!this.authService.isLoggedIn() || !this.currentSearchQuery) return;

        this.ratingService.getUserRatingForItem('teen-adult', this.currentSearchQuery).subscribe({
            next: (rating) => {
                this.userRating = rating ? rating.rating : 0;
            },
            error: (error) => {
                console.error('Error loading user rating:', error);
            },
        });
    }

    loadAggregateRating(): void {
        if (!this.currentSearchQuery) return;

        this.ratingService.getItemRatingStats('teen-adult', this.currentSearchQuery).subscribe({
            next: (stats) => {
                this.aggregateRating = stats.average_rating;
                this.totalRatings = stats.total_ratings;
            },
            error: (error) => {
                console.error('Error loading aggregate rating:', error);
            },
        });
    }

    hoverRating(rating: number): void {
        this.hoveredRating = rating;
    }

    clearHover(): void {
        this.hoveredRating = 0;
    }

    submitRating(rating: number): void {
        if (!this.authService.isLoggedIn() || !this.currentSearchQuery || this.isSubmittingRating)
            return;

        this.isSubmittingRating = true;
        this.ratingService.addRating('teen-adult', this.currentSearchQuery, rating).subscribe({
            next: () => {
                this.userRating = rating;
                this.isSubmittingRating = false;
                this.loadAggregateRating(); // Reload aggregate stats after rating
            },
            error: (error) => {
                console.error('Error submitting rating:', error);
                this.isSubmittingRating = false;
            },
        });
    }

    getStarClass(starNumber: number): string {
        const activeRating = this.hoveredRating || this.userRating;
        return starNumber <= activeRating ? 'filled' : 'empty';
    }
}
