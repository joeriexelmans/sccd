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
    (||{
      let scope = &mut $closure.0;
      let function = &mut $closure.1;
      return function($($param),* scope);
    })()
  };
}
