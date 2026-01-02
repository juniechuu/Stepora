// Angular
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

// Components
import { Navbar } from './core/navbar/navbar';

@Component({
    selector: 'app-root',
    imports: [CommonModule, RouterOutlet, Navbar],
    templateUrl: './app.html',
    styleUrl: './app.scss',
})
export class App {}
