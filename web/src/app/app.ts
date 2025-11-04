// Angular
import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chatbot } from './pages/chatbot/chatbot';

@Component({
    selector: 'app-root',
    imports: [Chatbot],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {}
