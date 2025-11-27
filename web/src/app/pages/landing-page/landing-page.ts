import { Component } from '@angular/core';
import { LandingModal, AgeGroup } from './components/landing-modal/landing-modal';
import { TeenAdults } from '../chatbot/components/teen-adults/teen-adults';
import { Toddler } from '../chatbot/components/toddler/toddler';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [LandingModal, TeenAdults, Toddler],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.scss',
})
export class LandingPage {
  selectedAgeGroup: AgeGroup | null = null;

  onAgeGroupSelected(group: AgeGroup): void {
    this.selectedAgeGroup = group;
    console.log('Selected age group:', group);
    // You can store this in a service or perform other actions here
  }
}
