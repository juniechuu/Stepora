// Angular
import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

// Pages
import { Chatbot } from './pages/chatbot/chatbot';
import { Navbar } from './core/navbar/navbar';
import { LandingPage } from './pages/landing-page/landing-page';

@Component({
    selector: 'app-root',
    imports: [Chatbot, Navbar, LandingPage],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {}
