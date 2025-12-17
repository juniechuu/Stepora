import { Routes } from '@angular/router';
import { LandingPage } from './pages/landing-page/landing-page';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';
import { UserDashboard } from './pages/user-dashboard/user-dashboard';
import { About } from './pages/about/about';
import { Leaderboard } from './pages/leaderboard/leaderboard';

export const routes: Routes = [
  { path: '', component: LandingPage },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'dashboard', component: UserDashboard },
  { path: 'about', component: About },
  { path: 'leaderboard', component: Leaderboard },
  { path: '**', redirectTo: '' }
];
