import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeenAdults } from './teen-adults';

describe('TeenAdults', () => {
  let component: TeenAdults;
  let fixture: ComponentFixture<TeenAdults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TeenAdults]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TeenAdults);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
