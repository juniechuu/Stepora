import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Toddler } from './toddler';

describe('Toddler', () => {
  let component: Toddler;
  let fixture: ComponentFixture<Toddler>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Toddler]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Toddler);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
