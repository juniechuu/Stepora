import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

export type AgeGroup = 'toddler' | 'adult' | 'elderly';

@Component({
  selector: 'app-landing-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing-modal.html',
  styleUrl: './landing-modal.scss',
})
export class LandingModal {
  @Output() ageGroupSelected = new EventEmitter<AgeGroup>();
  isVisible = true;

  selectAgeGroup(group: AgeGroup): void {
    this.ageGroupSelected.emit(group);
    this.isVisible = false;
  }
}
