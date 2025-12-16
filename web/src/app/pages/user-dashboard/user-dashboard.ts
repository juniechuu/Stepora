import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, User } from '../../endpoints/auth.service';
import { DashboardService, UserProfile, DashboardStats, SearchHistory, UserRating } from '../../endpoints/dashboard.service';

@Component({
  selector: 'app-user-dashboard',
  imports: [CommonModule, FormsModule],
  templateUrl: './user-dashboard.html',
  styleUrl: './user-dashboard.scss',
})
export class UserDashboard implements OnInit {
  currentUser: User | null = null;
  userProfile: UserProfile | null = null;
  stats: DashboardStats | null = null;
  searchHistory: SearchHistory[] = [];
  ratings: UserRating[] = [];
  isLoading: boolean = true;
  activeTab: string = 'overview';
  isEditingPicture: boolean = false;
  newPictureUrl: string = '';
  pictureError: string = '';
  selectedFile: File | null = null;
  uploadMode: 'url' | 'file' = 'file';

  constructor(
    private authService: AuthService,
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.currentUser = this.authService.getCurrentUserValue();
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading = true;

    // Load profile
    this.dashboardService.getUserProfile().subscribe({
      next: (profile) => {
        this.userProfile = profile;
      },
      error: (error) => {
        console.error('Error loading profile:', error);
      }
    });

    // Load stats
    this.dashboardService.getDashboardStats().subscribe({
      next: (stats) => {
        this.stats = stats;
      },
      error: (error) => {
        console.error('Error loading stats:', error);
      }
    });

    // Load search history
    this.dashboardService.getSearchHistory(20).subscribe({
      next: (response) => {
        this.searchHistory = response.history;
      },
      error: (error) => {
        console.error('Error loading search history:', error);
      }
    });

    // Load ratings
    this.dashboardService.getUserRatings(20).subscribe({
      next: (response) => {
        this.ratings = response.ratings;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading ratings:', error);
        this.isLoading = false;
      }
    });
  }

  setActiveTab(tab: string): void {
    this.activeTab = tab;
  }

  getInitials(): string {
    if (this.userProfile?.full_name) {
      const names = this.userProfile.full_name.split(' ');
      if (names.length >= 2) {
        return names[0].charAt(0).toUpperCase() + names[1].charAt(0).toUpperCase();
      }
      return names[0].charAt(0).toUpperCase();
    }
    return (this.userProfile?.username || 'U').charAt(0).toUpperCase();
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  }

  formatDateTime(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
    return this.formatDate(dateString);
  }

  getStarArray(rating: number): boolean[] {
    return Array(5).fill(false).map((_, i) => i < rating);
  }

  togglePictureEdit(): void {
    this.isEditingPicture = !this.isEditingPicture;
    this.newPictureUrl = '';
    this.pictureError = '';
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        this.pictureError = 'Invalid file type. Please upload PNG, JPG, GIF, or WebP';
        this.selectedFile = null;
        return;
      }
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        this.pictureError = 'File too large. Maximum size is 5MB';
        this.selectedFile = null;
        return;
      }
      
      this.selectedFile = file;
      this.pictureError = '';
    }
  }

  uploadFile(): void {
    if (!this.selectedFile) {
      this.pictureError = 'Please select a file';
      return;
    }

    this.dashboardService.uploadProfilePicture(this.selectedFile).subscribe({
      next: (response) => {
        const pictureUrl = response.picture_url;
        if (this.userProfile) {
          this.userProfile.profile_picture = pictureUrl;
        }
        // Update currentUser reference
        this.currentUser = this.authService.getCurrentUserValue();
        // Update auth service to notify navbar
        this.authService.updateCurrentUser({ profile_picture: pictureUrl });
        this.isEditingPicture = false;
        this.selectedFile = null;
      },
      error: (error) => {
        this.pictureError = error.error?.error || 'Failed to upload profile picture';
      }
    });
  }

  switchMode(mode: 'url' | 'file'): void {
    this.uploadMode = mode;
    this.pictureError = '';
    this.selectedFile = null;
    this.newPictureUrl = '';
  }

  updateProfilePicture(): void {
    this.pictureError = '';
    
    if (!this.newPictureUrl.trim()) {
      this.pictureError = 'Please enter a picture URL';
      return;
    }

    // Basic URL validation
    try {
      new URL(this.newPictureUrl);
    } catch {
      this.pictureError = 'Please enter a valid URL';
      return;
    }

    this.dashboardService.updateProfilePicture(this.newPictureUrl).subscribe({
      next: (response) => {
        const pictureUrl = response.picture_url.startsWith('http') ? response.picture_url : this.newPictureUrl;
        if (this.userProfile) {
          this.userProfile.profile_picture = pictureUrl;
        }
        // Update currentUser reference
        this.currentUser = this.authService.getCurrentUserValue();
        // Update auth service to notify navbar
        this.authService.updateCurrentUser({ profile_picture: pictureUrl });
        this.isEditingPicture = false;
        this.newPictureUrl = '';
      },
      error: (error) => {
        this.pictureError = error.error?.error || 'Failed to update profile picture';
      }
    });
  }

  removeProfilePicture(): void {
    if (!confirm('Are you sure you want to remove your profile picture?')) {
      return;
    }

    this.dashboardService.removeProfilePicture().subscribe({
      next: () => {
        if (this.userProfile) {
          this.userProfile.profile_picture = undefined;
        }
        // Update auth service to notify navbar
        this.authService.updateCurrentUser({ profile_picture: undefined });
        this.isEditingPicture = false;
      },
      error: (error) => {
        this.pictureError = error.error?.error || 'Failed to remove profile picture';
      }
    });
  }
}
