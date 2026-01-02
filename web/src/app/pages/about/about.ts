import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
    selector: 'app-about',
    imports: [CommonModule],
    templateUrl: './about.html',
    styleUrl: './about.scss',
})
export class About {
    features = [
        {
            icon: '/icons/search.svg',
            title: 'Smart Search',
            description: 'Search WikiHow articles with AI-powered results tailored to your needs',
        },
        {
            icon: '/icons/users.svg',
            title: 'Age-Appropriate Content',
            description: 'Content adapted for toddlers, teens/adults, and elderly users',
        },
        {
            icon: '/icons/star.svg',
            title: 'Rating System',
            description: 'Rate and review content to help others find the best resources',
        },
        {
            icon: '/icons/chart.svg',
            title: 'Leaderboard',
            description: 'Track your progress and compete with other learners',
        },
        {
            icon: '/icons/user.svg',
            title: 'Personal Dashboard',
            description: 'View your search history, ratings, and activity statistics',
        },
        {
            icon: '/icons/heart.svg',
            title: 'AI-Powered Chat',
            description: 'Interactive chatbot to guide you through learning processes',
        },
    ];

    teamMembers = [
        {
            name: 'Development Team',
            role: 'Full Stack Development',
            description: 'Building the future of accessible learning',
        },
    ];

    constructor(private router: Router) {}

    navigateToRegister(): void {
        this.router.navigate(['/register']);
    }
}
