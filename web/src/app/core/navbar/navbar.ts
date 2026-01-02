import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthService, User } from '../../endpoints/auth.service';

@Component({
    selector: 'app-navbar',
    imports: [CommonModule, RouterLink],
    templateUrl: './navbar.html',
    styleUrl: './navbar.scss',
})
export class Navbar implements OnInit {
    currentUser: User | null = null;
    isLoggedIn: boolean = false;
    showUserMenu: boolean = false;

    constructor(
        public authService: AuthService,
        private router: Router,
    ) {}

    ngOnInit(): void {
        // Subscribe to current user changes
        this.authService.currentUser$.subscribe((user) => {
            this.currentUser = user;
            this.isLoggedIn = !!user;
        });
    }

    goToLogin(): void {
        this.router.navigate(['/login']);
    }

    goToRegister(): void {
        this.router.navigate(['/register']);
    }

    toggleUserMenu(): void {
        this.showUserMenu = !this.showUserMenu;
    }

    goToDashboard(): void {
        this.router.navigate(['/dashboard']);
        this.showUserMenu = false;
    }

    logout(): void {
        this.authService.logout();
        this.showUserMenu = false;
        this.router.navigate(['/']);
    }

    onImageError(event: Event): void {
        console.error('Failed to load profile picture:', this.currentUser?.profile_picture);
        // Fall back to showing initials by clearing the profile_picture
        if (this.currentUser) {
            this.currentUser.profile_picture = undefined;
        }
    }
}
