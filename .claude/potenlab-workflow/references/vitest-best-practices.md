---
title: Vitest Testing Best Practices
impact: CRITICAL
impactDescription: Maintainable, fast, reliable tests that catch real bugs
tags: vitest, testing, tdd, mocks, assertions, async, test-doubles, performance
---

## Vitest Testing Best Practices

Expert-level vitest patterns for writing maintainable, effective tests. Covers organization, assertions, test doubles, async, and performance.

---

## NEVER Do

- **NEVER skip global mock cleanup** — Configure `clearMocks`, `resetMocks`, `restoreMocks` in `vitest.config.ts`. Manual cleanup creates order-dependent Heisenbugs.
- **NEVER nest describe >2 levels** — Put context in test names: `it('should add item to empty cart')`.
- **NEVER mock pure functions** — Mock only external deps (APIs, DBs, third-party). Prefer fakes > stubs > spies > mocks.
- **NEVER use `toBeTruthy()`/`toBeFalsy()`** — These pass for unintended values. Use `toBe(true)`, `toEqual()`, `toBeNull()`.
- **NEVER test implementation details** — Test behavior (inputs/outputs), not which internal functions were called.
- **NEVER share mutable state between tests** — Each test must be fully independent with fresh setup.
- **NEVER use `any` in test files** — Tests are executable docs. Use `Partial<T>` or factory functions.

---

## Before Writing Tests

1. **Check `vitest.config.ts`** for `clearMocks: true`, `resetMocks: true`, `restoreMocks: true`
2. **Discover setup files** — `test/setup.ts`, `vitest.setup.ts`, check `setupFiles` in config
3. **Analyze setup contents** — Global mocks, custom matchers (`@testing-library/jest-dom`), utilities
4. **Only add per-test cleanup for non-mock resources** (listeners, connections, custom state)

---

## 1. Organization

Co-locate tests next to implementation. One test file per module. Max 2 levels of `describe`.

**Incorrect:**

```
tests/components/button.test.tsx  # Separate directory
```

**Correct:**

```
src/components/button.tsx
src/components/button.test.tsx    # Co-located
```

**Incorrect (deep nesting):**

```ts
describe('Cart', () => {
  describe('when empty', () => {
    describe('addItem', () => {
      describe('with valid item', () => {
        it('should add', () => {});
      });
    });
  });
});
```

**Correct (flat, context in names):**

```ts
describe('ShoppingCart', () => {
  describe('addItem', () => {
    it('should add item to empty cart', () => {});
    it('should increment quantity for existing item', () => {});
    it('should throw for invalid item', () => {});
  });
});
```

---

## 2. AAA Pattern

Structure every test as **Arrange**, **Act**, **Assert**. Separate with blank lines.

**Incorrect (mixed concerns):**

```ts
test('product test', () => {
  const p = new ProductService().add({name: 'Widget'});
  expect(p.status).toBe('pendingApproval');
});
```

**Correct:**

```ts
it('should have pending status when no price specified', () => {
  // Arrange
  const service = new ProductService();

  // Act
  const product = service.add({ name: 'Widget' });

  // Assert
  expect(product.status).toEqual('pendingApproval');
});
```

For complex setup, extract to helper functions:

```ts
function createTestOrder(items: number = 3): Order {
  const order = new Order();
  for (let i = 0; i < items; i++) {
    order.addItem({ id: i, name: `Item ${i}`, price: 10 * i });
  }
  return order;
}
```

---

## 3. Parameterized Tests

Use `it.each` for variations. Separate happy/error paths. Use `$variable` in names.

**Incorrect (duplicate tests):**

```ts
it('should return 1 when given 0', () => { expect(factorial(0)).toEqual(1); });
it('should return 120 when given 5', () => { expect(factorial(5)).toEqual(120); });
```

**Correct:**

```ts
it.each([
  { input: 0, expected: 1 },
  { input: 1, expected: 1 },
  { input: 5, expected: 120 },
])('should return $expected when given $input', ({ input, expected }) => {
  expect(factorial(input)).toEqual(expected);
});

it('should throw when input is negative', () => {
  expect(() => factorial(-1)).toThrow('Number must not be negative');
});
```

Never mix valid/error cases in one `it.each` with conditional logic.

---

## 4. Error Handling

Test error type AND message. Use `rejects` for async. Cover boundaries and fault injection.

**Incorrect:**

```ts
expect(() => divide(10, 0)).toThrow(); // Which error? What message?
```

**Correct:**

```ts
expect(() => divide(10, 0)).toThrow(TypeError);
expect(() => divide(10, 0)).toThrow('Cannot divide by zero');
```

**Async errors:**

```ts
await expect(fetchUser('invalid')).rejects.toThrow('User not found');
await expect(fetchUser('invalid')).rejects.toThrow(NotFoundError);
```

**Fault injection (retry testing):**

```ts
const apiClient = {
  fetch: vi.fn()
    .mockRejectedValueOnce(new Error('Network error'))
    .mockRejectedValueOnce(new Error('Network error'))
    .mockResolvedValueOnce({ data: 'success' }),
};
const result = await service.fetchWithRetry('/api/data');
expect(result).toEqual({ data: 'success' });
expect(apiClient.fetch).toHaveBeenCalledTimes(3);
```

---

## 5. Assertions

Use strict assertions. `toEqual` for objects, `toBe` for primitives, `toStrictEqual` when undefined matters.

**Incorrect:**

```ts
expect(result).toBeTruthy();           // Could be 1, "false", [], {}
expect(result.length).toBeGreaterThan(0); // How many? Which items?
expect(user).toBe({ name: 'John' });   // Reference equality fails
```

**Correct:**

```ts
expect(user).toEqual({ name: 'John', email: 'john@example.com' });
expect(isValid).toBe(true);
expect(findUser('x')).toBeNull();
expect(user.middleName).toBeUndefined();
expect(result).toHaveLength(2);
expect(tax).toBeCloseTo(8.25, 2);  // Floating point
```

**Asymmetric matchers for dynamic values:**

```ts
expect(order).toEqual({
  id: expect.stringMatching(/^order-[a-f0-9]+$/),
  items: expect.arrayContaining([
    expect.objectContaining({ id: 1, quantity: 2 }),
  ]),
  createdAt: expect.any(Date),
  status: 'pending',
});
```

---

## 6. Test Doubles

Hierarchy: **Real > Fake > Stub > Spy > Mock**. Mock only external deps.

**Mock external deps:** APIs, databases, file system, non-deterministic functions (Date.now, Math.random).
**Don't mock:** Pure functions, your own code, simple utilities.

**Fake (in-memory implementation):**

```ts
class FakeUserRepo implements UserRepository {
  private users = new Map<string, User>();
  async save(user: User) { this.users.set(user.id, user); }
  async findById(id: string) { return this.users.get(id) || null; }
}
```

**Stub (pre-configured response):**

```ts
const apiClient = {
  fetch: vi.fn().mockResolvedValue({ temperature: 72, city: 'SF' }),
};
```

**Spy (record calls, keep real behavior):**

```ts
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
logger.error('fail');
expect(consoleSpy).toHaveBeenCalledWith('[ERROR]', 'fail');
```

**Module mock:**

```ts
vi.mock('uuid', () => ({ v4: vi.fn() }));
vi.mocked(uuidv4).mockReturnValueOnce('id-1');
```

**Partial module mock:**

```ts
vi.mock('../utils', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, fetchData: vi.fn() };
});
```

**Incorrect (over-mocking):**

```ts
// Mocking your own pure functions - just use real implementations
const mockHash = vi.fn().mockReturnValue('hashed');
const mockGenId = vi.fn().mockReturnValue('id-123');
```

---

## 7. Async Testing

Always `async/await`. Use `resolves`/`rejects` matchers. Fake timers for delays.

**Incorrect:**

```ts
it('should fetch user', () => {
  const user = fetchUser('123'); // Returns Promise, not user!
  expect(user).toEqual({ id: '123' }); // Passes incorrectly
});
```

**Correct:**

```ts
it('should fetch user', async () => {
  const user = await fetchUser('123');
  expect(user.id).toBe('123');
});

// Or with matchers
await expect(fetchUser('123')).resolves.toEqual({ id: '123', name: 'John' });
await expect(fetchUser('invalid')).rejects.toThrow('Not found');
```

**Fake timers for delays:**

```ts
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it('should retry after delay', async () => {
  const mockFn = vi.fn()
    .mockRejectedValueOnce(new Error('Fail'))
    .mockResolvedValueOnce('Success');

  const promise = retryWithDelay(mockFn, { delay: 1000 });
  await vi.advanceTimersByTimeAsync(1000);

  const result = await promise;
  expect(result).toBe('Success');
});
```

**Event emitters:**

```ts
it('should emit complete', async () => {
  const processor = new DataProcessor();
  const done = new Promise((resolve) => processor.once('complete', resolve));
  processor.process(data);
  await done;
  expect(processor.isComplete()).toBe(true);
});
```

---

## 8. Performance

Tests should run in milliseconds. No real network, no real delays, minimal setup.

**Global mock cleanup config (configure once):**

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    clearMocks: true,
    resetMocks: true,
    restoreMocks: true,
  },
});
```

**Rules:**
- Mock network calls, never call real APIs in unit tests
- Use in-memory fakes instead of real databases
- Use `vi.useFakeTimers()` instead of real `delay()`
- Don't make sync tests async unnecessarily
- Use `it.each` to reduce setup duplication
- Only set up what each test actually needs (lazy initialization)
- Only clean up non-mock resources per-test (global config handles mocks)
- Create minimal test data, not large realistic objects

**Monitor slow tests:**

```bash
vitest --reporter=verbose
vitest --reporter=default --slow-test-threshold=1000
```

---

## 9. Vitest Features

**Filtering:** `it.only`, `it.skip`, `it.todo` (remove `.only` before commit)

**Conditional:** `it.runIf(condition)`, `it.skipIf(condition)`

**Concurrent:** `describe.concurrent` for isolated parallel tests

**Coverage:**

```ts
// vitest.config.ts
test: {
  coverage: {
    provider: 'v8',
    reporter: ['text', 'html', 'lcov'],
    exclude: ['node_modules/', '**/*.test.ts', '**/*.config.ts'],
    thresholds: { lines: 80, functions: 80, branches: 80, statements: 80 },
  },
}
```

**Type testing:**

```ts
import { expectTypeOf } from 'vitest';
expectTypeOf(result).toEqualTypeOf<Promise<User>>();
expectTypeOf(createUser).parameter(0).toMatchTypeOf<UserInput>();
```

**Environments:** `@vitest-environment jsdom` for DOM, `@vitest-environment node` for server

**Benchmarking:**

```ts
import { bench, describe } from 'vitest';
describe('perf', () => {
  bench('reduce', () => arr.reduce((s, n) => s + n, 0));
});
```

---

## 10. Snapshot Testing

Use sparingly. Good for complex structures, error messages, CLI output. Bad for dynamic data or simple values.

**Use property matchers for dynamic fields:**

```ts
expect(user).toMatchSnapshot({
  id: expect.any(String),
  createdAt: expect.any(Date),
});
```

**Prefer explicit assertions for simple values:**

```ts
// Bad
expect(name).toMatchInlineSnapshot(`"John Doe"`);
// Good
expect(name).toBe('John Doe');
```

**Rules:**
- Keep snapshots small and focused
- Always review snapshot changes before updating (`vitest run -u`)
- Combine snapshots with explicit assertions for critical values
- Never snapshot mock calls — use `toHaveBeenCalledWith()`

---

## Quick Reference: Assertion Cheat Sheet

| Use Case | Matcher |
|----------|---------|
| Primitives | `toBe(5)`, `toBe('hello')`, `toBe(true)` |
| Objects/Arrays | `toEqual({...})`, `toStrictEqual({...})` |
| Null/Undefined | `toBeNull()`, `toBeUndefined()`, `toBeDefined()` |
| Arrays | `toHaveLength(3)`, `toContainEqual({...})` |
| Strings | `toContain('sub')`, `toMatch(/regex/)` |
| Numbers | `toBeGreaterThan(0)`, `toBeCloseTo(8.25, 2)` |
| Errors | `toThrow(TypeError)`, `toThrow('message')` |
| Async errors | `rejects.toThrow('message')` |
| Object shape | `toMatchObject({...})`, `toHaveProperty('key')` |
| Dynamic values | `expect.any(String)`, `expect.stringMatching(/.../)` |
| Negation | `.not.toContainEqual(...)` |

Reference: [Vitest Docs](https://vitest.dev/)
