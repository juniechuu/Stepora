import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { DashboardService } from '../../endpoints/dashboard.service';

interface TopArticle {
  item_type: string;
  item_id: string;
  total_ratings: number;
  average_rating: number;
  last_rated: string;
}

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './leaderboard.html',
  styleUrl: './leaderboard.scss',
})
export class Leaderboard implements OnInit {
  private dashboardService = inject(DashboardService);
  private router = inject(Router);

  topArticles: TopArticle[] = [];
  isLoading: boolean = true;
  error: string = '';

  ngOnInit(): void {
    this.loadTopArticles();
  }

  loadTopArticles(): void {
    this.isLoading = true;
    this.dashboardService.getTopRatedArticles(100).subscribe({
      next: (response) => {
        this.topArticles = response.articles;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading top articles:', error);
        this.error = 'Failed to load leaderboard';
        this.isLoading = false;
      }
    });
  }

  getArticleTypeLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'teen-adult': 'How-To Guide',
      'toddler': 'Simple Guide',
      'elderly': 'Detailed Guide'
    };
    return labels[type] || type;
  }

  getStars(rating: number): number[] {
    return Array(5).fill(0).map((_, i) => i < Math.round(rating) ? 1 : 0);
  }

  viewArticle(articleTitle: string): void {
    // Navigate to home page and store the search query for teen-adults component
    localStorage.setItem('teenAdultPendingSearch', articleTitle);
    localStorage.setItem('autoSelectAdult', 'true');
    this.router.navigate(['/']);
  }
}
