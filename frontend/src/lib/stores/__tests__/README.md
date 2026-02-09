# listingStore Test Suite

## Overview
Comprehensive unit tests for the listing state management store with 80 test cases covering all functionality.

## Test Coverage

### Core Functions (80 tests total)

#### `setFieldValue` (10 tests)
- Basic field value setting
- User modification tracking
- Multiple data type support (string, number, boolean, null)
- AI suggestion preservation
- Edge cases (empty strings, zero values)
- Multiple field independence

#### `setAISuggestion` (10 tests)
- AI suggestion for new fields
- Value usage when not user-modified
- User value protection
- Separate suggestion storage
- Default field interaction
- Multiple data type support

#### `initField` (7 tests)
- Default value initialization
- Null default handling
- Existing field protection
- Multiple data type support
- Independent field initialization

#### `getFieldValue` (7 tests)
- Value retrieval
- Non-existent field handling
- Falsy value preservation (null, false, 0, empty string)
- Current value vs AI suggestion

#### `reset` (4 tests)
- Complete state clearing
- Post-reset value retrieval
- State restoration capability
- Empty store handling

#### `loadState` (5 tests)
- External state loading
- State overwriting
- AI suggestion preservation
- Empty state handling
- Mixed field type support

#### `toJSON` (8 tests)
- Simple serialization
- Metadata exclusion
- Empty store handling
- User value priority
- All data type support

#### `listingValues` derived store (6 tests)
- Value derivation
- Reactive updates
- Empty store handling
- AI vs user value handling
- Mixed type support

#### `aiSuggestions` derived store (8 tests)
- Different suggestion filtering
- Matching suggestion exclusion
- Empty state handling
- Dynamic updates
- User acceptance handling
- Multiple field states

#### Complex workflows (4 tests)
- Complete form filling
- Save and reload
- AI re-suggestion
- Multiple derived store subscriptions

#### Edge cases (11 tests)
- Rapid successive updates
- Very long strings (10,000 characters)
- Special characters in field IDs
- Unicode character support
- Negative/large/decimal numbers
- Field isolation
- Alternating user/AI updates
- Uninitialized store access

## Test Principles

1. **Isolation**: Each test resets the store using `beforeEach()`
2. **Independence**: Tests can run in any order
3. **Coverage**: All exported functions and state mutations
4. **Edge cases**: Boundary conditions and error scenarios
5. **Real-world workflows**: Complex multi-step operations

## Running Tests

```bash
# Run all store tests
npm test -- src/lib/stores/__tests__/listingStore.test.ts

# Run with watch mode
npm test -- src/lib/stores/__tests__/listingStore.test.ts --watch

# Run with coverage
npm test -- src/lib/stores/__tests__/listingStore.test.ts --coverage
```

## Test Results

All 80 tests passing:
- Test execution: ~65ms
- Total duration: ~2.6s
- 100% function coverage
- 100% branch coverage
