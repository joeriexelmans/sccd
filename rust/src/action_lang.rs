
// Requirements for working with time durations in SCCD:
//  1) Use of integer types. Floating point types have complex behavior when it comes to precision, mathematical operations introducing roundoff errors that are hard to predict.
//  2) The type system should prevent mixing up durations' units (e.g. mistaking a value in milliseconds to be a value in microseconds).
//  3) Under the hood, duration values should not all be converted to the same "base" unit (e.g. microseconds). Because we use integers, there is always a tradeoff between the smallest duration expressable vs. the largest duration expressable, and the optimal tradeoff is model-specific.
//  4) There should be no additional runtime cost when performing arithmetic on durations of the same unit.

use std::marker::PhantomData;
use std::ops::{Add, Sub};

// 32 bit provides wide enough range for most applications, and has better performance than 64 bit, even on amd64 architectures
pub type TimeType = i32;

// Just a marker
pub trait Unit{}

// Our units are also just markers
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Femtos();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Picos();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Nanos();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Micros();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Millis();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Seconds();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Minutes();
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Hours();

impl Unit for Femtos{}
impl Unit for Picos{}
impl Unit for Nanos{}
impl Unit for Micros{}
impl Unit for Millis{}
impl Unit for Seconds{}
impl Unit for Minutes{}
impl Unit for Hours{}

// Duration type
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Copy, Clone)]
pub struct Dur<U: Unit> {
  value: TimeType,
  unit: PhantomData<U>,
}
impl<U: Unit> Dur<U> {
  fn new(value: TimeType) -> Self {
    Self{
      value,
      unit: Default::default(),
    }
  }
}
impl<U: Unit> Add for Dur<U> {
  type Output = Self;

  fn add(self, other: Self) -> Self::Output {
    Self::new(self.value + other.value)
  }
}
impl<U: Unit> Sub for Dur<U> {
  type Output = Self;

  fn sub(self, other: Self) -> Self::Output {
    Self::new(self.value - other.value)
  }
}

impl Dur<Femtos> {
  pub fn to_picos(&self) -> Dur<Picos> {
    Dur::<Picos>::new(self.value / 1000)
  }
}
impl Dur<Picos> {
  pub fn to_femtos(&self) -> Dur<Femtos> {
    Dur::<Femtos>::new(self.value * 1000)
  }
  pub fn to_nanos(&self) -> Dur<Nanos> {
    Dur::<Nanos>::new(self.value / 1000)
  }
}
impl Dur<Nanos> {
  pub fn to_picos(&self) -> Dur<Picos> {
    Dur::<Picos>::new(self.value * 1000)
  }
  pub fn to_micros(&self) -> Dur<Micros> {
    Dur::<Micros>::new(self.value / 1000)
  }
}
impl Dur<Micros> {
  pub fn to_nanos(&self) -> Dur<Nanos> {
    Dur::<Nanos>::new(self.value * 1000)
  }
  pub fn to_millis(&self) -> Dur<Millis> {
    Dur::<Millis>::new(self.value / 1000)
  }
}
impl Dur<Millis> {
  pub fn to_micros(&self) -> Dur<Micros> {
    Dur::<Micros>::new(self.value * 1000)
  }
  pub fn to_seconds(&self) -> Dur<Seconds> {
    Dur::<Seconds>::new(self.value / 1000)
  }
}
impl Dur<Seconds> {
  pub fn to_millis(&self) -> Dur<Millis> {
    Dur::<Millis>::new(self.value * 1000)
  }
  pub fn to_minutes(&self) -> Dur<Minutes> {
    Dur::<Minutes>::new(self.value / 60)
  }
}
impl Dur<Minutes> {
  pub fn to_seconds(&self) -> Dur<Seconds> {
    Dur::<Seconds>::new(self.value * 60)
  }
  pub fn to_hours(&self) -> Dur<Hours> {
    Dur::<Hours>::new(self.value / 60)
  }
}
impl Dur<Hours> {
  pub fn to_minutes(&self) -> Dur<Minutes> {
    Dur::<Minutes>::new(self.value * 60)
  }
}

#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn duration_addition() {
    let result = Dur::<Seconds>::new(42) + Dur::<Seconds>::new(10);
    assert_eq!(result, Dur::<Seconds>::new(52))
  }
  #[test]
  fn duration_subtraction() {
    let result = Dur::<Seconds>::new(52) - Dur::<Seconds>::new(10);
    assert_eq!(result, Dur::<Seconds>::new(42))
  }
  #[test]
  fn duration_conversion() {
    let result = Dur::<Millis>::new(42000).to_seconds();
    assert_eq!(result, Dur::<Seconds>::new(42))
  }
}


// Helpers used by from-action-lang-generated Rust code

#[allow(unused_imports)]
use std::ops::Deref;

#[allow(unused_imports)]
use std::ops::DerefMut;

// This macro lets a struct "inherit" the data members of another struct
// The inherited struct is added as a struct member and the Deref and DerefMut
// traits are implemented to return a reference to the base struct
#[macro_export]
macro_rules! inherit_struct {
  ($name: ident ($base: ty) { $($element: ident: $ty: ty),* $(,)? } ) => {
    #[derive(Copy, Clone)]
    struct $name {
      _base: $base,
      $($element: $ty),*
    }
    impl Deref for $name {
      type Target = $base;
      fn deref(&self) -> &$base {
        &self._base
      }
    }
    impl DerefMut for $name {
      fn deref_mut(&mut self) -> &mut $base {
        &mut self._base
      }
    }
  }
}

// "Base struct" for all scopes
#[derive(Copy, Clone)]
pub struct Empty{}

// A closure object is a pair of a functions first argument and that function.
// The call may be part of an larger expression, and therefore we cannot just write 'let' statements to assign the pair's elements to identifiers which we need for the call.
// This macro does exactly that, in an anonymous Rust closure, which is immediately called.
#[macro_export]
macro_rules! call_closure {
  ($closure: expr, $($param: expr),*  $(,)?) => {
    {
      let scope = &mut $closure.0;
      let function = &mut $closure.1;
      function($($param),* scope)
    }
  };
}
