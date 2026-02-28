# Testing Guide

This guide covers testing strategies, test execution, and quality assurance for the ACH to RTP Conversion Service.

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [End-to-End Tests](#end-to-end-tests)
5. [Performance Testing](#performance-testing)
6. [Test Execution](#test-execution)
7. [Coverage Analysis](#coverage-analysis)

## Testing Strategy

The service implements a comprehensive testing strategy following the testing pyramid:

```
        ▲
       /|\
      / | \
     /  |  \  End-to-End Tests (Few)
    /   |   \
   /    |    \
  /     |     \
 /      |      \
/───────┼───────\
|   Integration  |  Integration Tests (Some)
|     Tests      |
├────────────────┤
|   Unit Tests   |  Unit Tests (Many)
└────────────────┘
```

### Test Levels

1. **Unit Tests**: Test individual components in isolation
   - Fast execution
   - No external dependencies
   - High code coverage target: >80%

2. **Integration Tests**: Test component interactions
   - Database integration
   - Message queue integration
   - API integration

3. **End-to-End Tests**: Test complete workflows
   - File upload to message publishing
   - Error scenarios
   - Performance under load

## Unit Tests

### ACH Field Extractor Tests

**File:** `src/test/java/com/example/ach2rtp/util/AchFieldExtractorTest.java`

**Test Cases:**
- String field extraction
- Numeric field extraction
- Amount field extraction
- Date field extraction
- Time field extraction
- Invalid field handling
- Field validation
- Blank field detection

**Example:**
```java
@Test
@DisplayName("Should extract string field correctly")
void testExtractStringField() {
    String result = AchFieldExtractor.extractStringField(SAMPLE_RECORD, 1, 1);
    assertEquals("1", result);
}
```

### RTP Message Builder Tests

**File:** `src/test/java/com/example/ach2rtp/service/RtpMessageBuilderServiceTest.java`

**Test Cases:**
- Valid RTP message generation
- Missing required fields validation
- Invalid amount handling
- XML special character escaping
- Addenda information inclusion

**Example:**
```java
@Test
@DisplayName("Should build valid RTP message")
void testBuildRtpMessage() {
    String message = rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader);
    
    assertNotNull(message);
    assertTrue(message.contains("<?xml version=\"1.0\""));
    assertTrue(message.contains("CstmrCdtTrfInitn"));
}
```

### Running Unit Tests

```bash
# Run all unit tests
mvn test

# Run specific test class
mvn test -Dtest=AchFieldExtractorTest

# Run specific test method
mvn test -Dtest=AchFieldExtractorTest#testExtractStringField

# Run with coverage
mvn test jacoco:report
```

## Integration Tests

### ACH File Parser Integration Test

**File:** `src/test/java/com/example/ach2rtp/parser/AchFileParserIntegrationTest.java`

**Test Scenarios:**
- Parse valid ACH file
- Handle malformed records
- Process multiple batches
- Validate record counts

**Example:**
```java
@Test
@DisplayName("Should parse valid ACH file")
void testParseValidAchFile() throws IOException {
    InputStream inputStream = new FileInputStream("test-data/sample.ach");
    AchFile achFile = achFileParser.parseFile(inputStream, "sample.ach");
    
    assertNotNull(achFile);
    assertEquals(1, achFile.getBatches().size());
    assertEquals(100, achFile.getTotalEntries());
}
```

### Message Publisher Integration Test

**File:** `src/test/java/com/example/ach2rtp/service/MessagePublisherServiceIntegrationTest.java`

**Test Scenarios:**
- Publish message to RabbitMQ
- Handle connection errors
- Verify message headers

**Setup:**
```java
@SpringBootTest
@ActiveProfiles("test")
class MessagePublisherServiceIntegrationTest {
    
    @Autowired
    private MessagePublisherService messagePublisherService;
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    // Tests here
}
```

### Running Integration Tests

```bash
# Run integration tests
mvn verify

# Run specific integration test
mvn verify -Dit.test=AchFileParserIntegrationTest

# Run with test containers
mvn verify -Dcontainers=true
```

## End-to-End Tests

### Complete Workflow Test

**Scenario:** Upload ACH file → Parse → Convert → Publish

```bash
# 1. Start services
docker-compose up -d

# 2. Upload file
curl -X POST \
  -F "file=@test-data/sample.ach" \
  http://localhost:8080/api/v1/conversion/upload

# 3. Verify messages in queue
curl -u guest:guest \
  http://localhost:15672/api/queues/%2F/rtp-queue

# 4. Check conversion status
curl http://localhost:8080/api/v1/jobs/{jobId}
```

### Test Data

**Sample ACH File:** `test-data/sample.ach`

```
101 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000
5200ORIGIN BANK          1234567890PPDPAYROLL    2024010120240101000001000000100000000000000000000000000
622021000210123456789000000001000000000000000000000000000000000000000000000000000000000000000000000001
820000010000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
9000001000001000000010000000010000000000000000000000000000000000000000000000000000000000000000000000000
```

## Performance Testing

### Load Testing

**Tool:** Apache JMeter

**Test Plan:**
```
Thread Group (100 threads, ramp-up 10s, duration 60s)
├── HTTP Sampler (POST /v1/conversion/upload)
├── Response Assertion
└── Aggregate Report
```

**Execution:**
```bash
jmeter -n -t load-test.jmx -l results.jtl -j jmeter.log
```

### Stress Testing

**Objective:** Determine breaking point

**Test Scenarios:**
- Gradually increase load
- Monitor response times
- Track error rates
- Identify bottlenecks

### Benchmark Results

Expected performance metrics:

| Metric | Target | Actual |
|--------|--------|--------|
| File Upload (10 MB) | <5s | TBD |
| ACH Parsing (1000 entries) | <2s | TBD |
| RTP Message Generation | <100ms per entry | TBD |
| Message Publishing | <50ms per message | TBD |
| 95th Percentile Latency | <500ms | TBD |
| Error Rate | <0.1% | TBD |

## Test Execution

### Local Development

```bash
# Run all tests
mvn clean test

# Run with specific profile
mvn test -Dspring.profiles.active=test

# Run with debugging
mvn test -Dmaven.surefire.debug
```

### Continuous Integration

```bash
# GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-java@v2
        with:
          java-version: '17'
      - run: mvn clean verify
      - uses: codecov/codecov-action@v2
```

### Docker-Based Testing

```bash
# Run tests in Docker
docker build -t ach-to-rtp-service:test --target test .
docker run --rm ach-to-rtp-service:test mvn test

# Run with docker-compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Coverage Analysis

### Code Coverage

**Tool:** JaCoCo

**Configuration:**
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.8</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**Generate Report:**
```bash
mvn clean test jacoco:report
# Report available at: target/site/jacoco/index.html
```

### Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| Util Classes | >90% |
| Service Classes | >85% |
| Controller Classes | >80% |
| Model Classes | >70% |
| Overall | >80% |

### Coverage Badges

```markdown
[![codecov](https://codecov.io/gh/user/ach-to-rtp-service/branch/main/graph/badge.svg)](https://codecov.io/gh/user/ach-to-rtp-service)
```

## Test Data Management

### Sample Files

**Valid ACH File:** `test-data/valid.ach`
- 1 batch with 100 entries
- All fields populated correctly
- Expected to process successfully

**Invalid ACH File:** `test-data/invalid.ach`
- Malformed records
- Missing required fields
- Expected to fail with validation errors

**Edge Cases:** `test-data/edge-cases.ach`
- Maximum file size
- Special characters in names
- Large amounts
- Multiple batches

### Test Data Cleanup

```bash
# Clear test data
rm -rf test-data/output/*

# Reset test database
psql -h localhost -U postgres -d ach_rtp_db -f test-data/reset.sql
```

## Quality Metrics

### Code Quality

**SonarQube Integration:**
```bash
mvn clean verify sonar:sonar \
  -Dsonar.projectKey=ach-to-rtp-service \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=<token>
```

**Quality Gates:**
- Code Coverage: >80%
- Duplicated Lines: <3%
- Maintainability Rating: A
- Reliability Rating: A
- Security Rating: A

### Test Metrics

| Metric | Target |
|--------|--------|
| Test Pass Rate | 100% |
| Code Coverage | >80% |
| Build Time | <5 minutes |
| Test Execution Time | <2 minutes |

## Troubleshooting Tests

### Common Issues

**Issue:** Tests fail with database connection error
```bash
# Solution: Start PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

**Issue:** Tests fail with RabbitMQ connection error
```bash
# Solution: Start RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
```

**Issue:** Tests timeout
```bash
# Solution: Increase timeout
mvn test -DargLine="-Dtimeout=60000"
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what is being tested
3. **Coverage**: Aim for >80% code coverage
4. **Performance**: Unit tests should complete in <100ms
5. **Maintenance**: Update tests when code changes
6. **Documentation**: Document complex test scenarios
7. **Automation**: Run tests on every commit
8. **Monitoring**: Track coverage trends over time

## References

- [JUnit 5 Documentation](https://junit.org/junit5/)
- [Mockito Documentation](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- [Spring Boot Testing Guide](https://spring.io/guides/gs/testing-web/)
- [JaCoCo Code Coverage](https://www.jacoco.org/)
- [Apache JMeter](https://jmeter.apache.org/)
