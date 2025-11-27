import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Elderly } from './elderly';

describe('Elderly', () => {
  let component: Elderly;
  let fixture: ComponentFixture<Elderly>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Elderly]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Elderly);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
