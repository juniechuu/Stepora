import { Component, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AiService } from '../../../../endpoints/ai.service';
import { Router } from '@angular/router';

interface PresetQuestion {
  question: string;
  icon: string;
  color: string;
}

@Component({
  selector: 'app-toddler',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './toddler.html',
  styleUrls: ['./toddler.scss', './experimental-modal.scss'],
})
export class Toddler {
  private aiService = inject(AiService);
  private router = inject(Router);

  searchQuery: string = '';
  isLoading: boolean = false;
  error: string = '';
  experimentalMode: boolean = false;
  
  // Modal state
  showModal: boolean = false;
  modalQuestion: string = '';
  steps: string[] = [];
  currentStep: number = 0;

  presetQuestions: PresetQuestion[] = [
    {
      question: 'How to draw a cat?',
      icon: '/icons/cat-orange.svg',
      color: '#ff9a3c'
    },
    {
      question: 'How to take care of a fish?',
      icon: '/icons/clownfish.svg',
      color: '#4ecdc4'
    },
    {
      question: 'How to make a paper airplane?',
      icon: '/icons/plane.svg',
      color: '#667eea'
    },
    {
      question: 'How to grow a plant?',
      icon: '/icons/apple-tree.svg',
      color: '#10b981'
    },
    {
      question: 'How to make cookies?',
      icon: '/icons/cookie.svg',
      color: '#f59e0b'
    },
    {
      question: 'How to build a snowman?',
      icon: '/icons/snowman.svg',
      color: '#60a5fa'
    }
  ];

  askQuestion(question: string): void {
    if (!question.trim()) {
      this.error = 'Please enter a question';
      return;
    }

    this.isLoading = true;
    this.error = '';

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
      },
      error: (error) => {
        console.error('Error calling OpenAI:', error);
        this.error = error.error?.error || 'An error occurred while processing your request';
        this.isLoading = false;
      }
    });
  }

  parseSteps(response: string): string[] {
    // Remove common intro phrases
    let cleanedResponse = response
      .replace(/^(To .+?, follow these steps?:|Here are the steps?:|Follow these steps?:)\s*/i, '')
      .replace(/^(Here's how to .+?:|Here's how you .+?:|Let me show you how .+?:)\s*/i, '')
      .trim();
    
    // Split by numbered steps or newlines
    let steps: string[] = [];
    
    // Try to split by numbered list
    const numberedSteps = cleanedResponse.split(/\n(?=\d+\.\s+)/);
    if (numberedSteps.length > 1) {
      // Remove the numbering from each step
      steps = numberedSteps
        .map(step => step.replace(/^\d+\.\s+/, '').trim())
        .filter(step => step.length > 0);
    } else {
      // Try to split by "Step X:"
      const namedSteps = cleanedResponse.split(/\n(?=Step\s+\d+:)/i);
      if (namedSteps.length > 1) {
        // Remove "Step X:" prefix
        steps = namedSteps
          .map(step => step.replace(/^Step\s+\d+:\s*/i, '').trim())
          .filter(step => step.length > 0);
      } else {
        // Fall back to splitting by double newlines or sentences
        steps = cleanedResponse.split(/\n\n+/).filter(step => step.trim().length > 0);
        if (steps.length === 1) {
          // If still one block, split by newlines
          steps = cleanedResponse.split(/\n/).filter(step => step.trim().length > 0);
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
