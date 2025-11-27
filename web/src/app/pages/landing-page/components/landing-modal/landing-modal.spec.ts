import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LandingModal } from './landing-modal';

describe('LandingModal', () => {
  let component: LandingModal;
  let fixture: ComponentFixture<LandingModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LandingModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LandingModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
