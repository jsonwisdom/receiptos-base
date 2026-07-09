# Lesson 022 Validation Test Suite v0.1

Witness-only validation tests for the mock evidence pointer schema.

Authority: false.
No fake green.

## Expected Passing Cases

1. pointer: mock://case001/service/context
2. pointer: mock://case001/functional-impact
3. pointer: mock://MOCK-VA-CASE-001/evidence-pointer-a
4. case_ref: MOCK-VA-CASE-001
5. timestamp: valid date-time string

## Expected Rejection Cases

1. http://example.com/record
2. https://example.com/record
3. ipfs://bafyexample
4. file:///tmp/record.pdf
5. va.gov/real-system/path
6. pointer containing real private record language
7. pointer containing PII field
8. pointer containing PHI field
9. extra field outside schema
10. missing pointer
11. missing case_ref
12. missing timestamp

## Validation Result

The schema is valid only for mock pointer rehearsal.

Final state: validation test surface only.
