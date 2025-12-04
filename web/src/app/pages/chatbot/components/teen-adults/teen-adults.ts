import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AiService } from '../../../../endpoints/ai.service';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './teen-adults.html',
  styleUrl: './teen-adults.scss',
})
export class TeenAdults {
  private aiService = inject(AiService);

  searchQuery: string = '';
  article: Article | null = null;
  isLoading: boolean = false;
  error: string = '';
  experimentalMode: boolean = false;
  showSuggestions: boolean = false;
  suggestions: string[] = [];
  isLoadingSuggestions: boolean = false;

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

    if (this.experimentalMode) {
      // Experimental mode: Scrape WikiHow
      this.aiService.scrapeWikiHow(this.searchQuery).subscribe({
        next: (response) => {
          console.log('WikiHow scrape response:', response);
          this.isLoading = false;
          this.article = this.parseScrapedArticle(response);
          this.scrollToTop();
        },
        error: (error) => {
          console.error('Error scraping WikiHow:', error);
          this.isLoading = false;
          this.error = error.error?.error || 'Failed to scrape WikiHow. Try a different query.';
        }
      });
    } else {
      // Normal mode: Use AI knowledge
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
          this.scrollToTop();
        },
        error: (error) => {
          console.error('Error calling OpenAI:', error);
          this.isLoading = false;
          this.error = error.error?.error || 'An error occurred while processing your request';
        }
      });
    }
  }

  parseScrapedArticle(response: any): Article {
    return {
      title: response.title || this.searchQuery,
      introduction: response.introduction,
      prerequisites: response.prerequisites || undefined,
      steps: response.steps.map((step: any) => ({
        title: step.title,
        description: step.description,
        tips: step.tips || undefined
      })),
      conclusion: response.conclusion,
      relatedLinks: response.relatedLinks || undefined,
      readTime: response.readTime || 5,
      difficulty: response.difficulty || 'Intermediate'
    };
  }

  toggleExperimentalMode(): void {
    this.experimentalMode = !this.experimentalMode;
    console.log('Experimental mode:', this.experimentalMode ? 'ON' : 'OFF');
  }

  parseArticle(response: string, query: string): Article {
    const lines = response.split('\n').map(line => line.trim()).filter(line => line);
    
    const article: Article = {
      title: query,
      steps: [],
      readTime: 5,
      difficulty: 'Intermediate'
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
          description: ''
        };
      } else if (line.startsWith('TIPS:')) {
        // Skip the TIPS: header
        continue;
      } else {
        if (currentSection === 'intro' && article.introduction) {
          article.introduction += ' ' + line;
        } else if (currentSection === 'prereq' && article.prerequisites && line !== 'None') {
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
            url: `https://www.google.com/search?q=${encodeURIComponent(cleanLine)}`
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
          this.error = 'Please provide more details (at least 4 words) for better accuracy.';
        }
      },
      error: (error) => {
        console.error('Error generating suggestions:', error);
        this.isLoadingSuggestions = false;
        this.closeSuggestions();
        this.error = 'Please provide more details (at least 4 words) for better accuracy.';
      }
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
}
